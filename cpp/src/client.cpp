/**
 * @file client.cpp
 * @brief Implementation of Client class with all gRPC operations.
 *
 * Terminology (with backwards compatibility):
 * - Space (formerly Group): A hierarchical container/namespace
 * - Item (formerly Product): An asset/entity in the graph
 * - Revision (formerly Version): A specific state of an item
 * - Artifact (formerly Resource): A file/location attached to a revision
 * - Edge (formerly Link): A relationship between revisions
 * - Bundle (formerly Collection): A curated set of items
 */

#include "kumiho/client.hpp"
#include "kumiho/project.hpp"
#include "kumiho/space.hpp"
#include "kumiho/item.hpp"
#include "kumiho/revision.hpp"
#include "kumiho/artifact.hpp"
#include "kumiho/edge.hpp"
#include "kumiho/bundle.hpp"
#include "kumiho/event.hpp"
#include "kumiho/error.hpp"
#include "kumiho/token_loader.hpp"
#include "kumiho/discovery.hpp"
#include <grpcpp/grpcpp.h>
#include <regex>
#include <sstream>
#include <fstream>
#include <cctype>
#include <cstdlib>
#include <algorithm>
#include <chrono>
#include <random>
#include <iomanip>

namespace kumiho {
namespace api {

// --- Helper Functions ---

namespace {

struct EndpointConfig {
    std::string address;
    std::string authority;
    bool use_tls;
};

EndpointConfig NormaliseEndpoint(const std::string& raw) {
    EndpointConfig config{};
    std::string value = raw;

    const auto start = value.find_first_not_of(" \t\r\n");
    const auto end = value.find_last_not_of(" \t\r\n");
    if (start == std::string::npos) {
        throw ValidationError("Kumiho endpoint cannot be empty");
    }
    value = value.substr(start, end - start + 1);

    std::string scheme;
    std::string host;
    std::string port;

    const auto scheme_pos = value.find("://");
    if (scheme_pos != std::string::npos) {
        scheme = value.substr(0, scheme_pos);
        std::transform(scheme.begin(), scheme.end(), scheme.begin(), [](unsigned char c) {
            return static_cast<char>(std::tolower(c));
        });
        std::string remainder = value.substr(scheme_pos + 3);
        const auto slash = remainder.find('/');
        if (slash != std::string::npos) {
            remainder = remainder.substr(0, slash);
        }
        const auto colon = remainder.find(':');
        if (colon != std::string::npos) {
            host = remainder.substr(0, colon);
            port = remainder.substr(colon + 1);
        } else {
            host = remainder;
        }
        if (port.empty()) {
            if (scheme == "https" || scheme == "grpcs") {
                port = "443";
            } else if (scheme == "http" || scheme == "grpc") {
                port = "80";
            }
        }
    } else {
        scheme.clear();
        std::string remainder = value;
        const auto slash = remainder.find('/');
        if (slash != std::string::npos) {
            remainder = remainder.substr(0, slash);
        }
        const auto colon = remainder.find(':');
        if (colon != std::string::npos) {
            host = remainder.substr(0, colon);
            port = remainder.substr(colon + 1);
        } else {
            host = remainder;
        }
    }

    if (host.empty()) {
        throw ValidationError("Invalid Kumiho endpoint: " + raw);
    }

    if (port.empty()) {
        port = (scheme == "https" || scheme == "grpcs") ? "443" : "8080";
    }

    config.address = host + ":" + port;
    config.authority = host;
    config.use_tls = (scheme == "https" || scheme == "grpcs" || port == "443");
    return config;
}

bool ParseFlag(const char* value) {
    if (value == nullptr || *value == '\0') {
        return false;
    }
    std::string flag(value);
    std::transform(flag.begin(), flag.end(), flag.begin(), [](unsigned char c) { 
        return static_cast<char>(std::tolower(c)); 
    });
    return flag == "1" || flag == "true" || flag == "yes";
}

std::string ReadFileContents(const char* path) {
    if (path == nullptr || *path == '\0') {
        return {};
    }
    std::ifstream stream(path, std::ios::binary);
    if (!stream) {
        throw RpcError(std::string("Failed to open CA bundle: ") + path);
    }
    std::stringstream buffer;
    buffer << stream.rdbuf();
    return buffer.str();
}

/// Generate a unique correlation ID for end-to-end request tracing.
/// Format: kumiho-<hex timestamp><random suffix>
std::string generateCorrelationId() {
    auto now = std::chrono::system_clock::now();
    auto epoch = now.time_since_epoch();
    auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(epoch).count();
    
    // Generate random suffix
    static std::random_device rd;
    static std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 0xFFFF);
    int random_suffix = dis(gen);
    
    std::stringstream ss;
    ss << "kumiho-" << std::hex << millis << std::setfill('0') << std::setw(4) << random_suffix;
    return ss.str();
}

/// Resolve the default per-RPC deadline in seconds.
/// Reads KUMIHO_RPC_TIMEOUT_SECONDS; defaults to 30s. Non-positive or
/// unparseable values fall back to the default.
double defaultRpcTimeoutSeconds() {
    const char* raw = std::getenv("KUMIHO_RPC_TIMEOUT_SECONDS");
    if (raw == nullptr || *raw == '\0') {
        return 30.0;
    }
    try {
        double value = std::stod(raw);
        if (value > 0.0) {
            return value;
        }
    } catch (...) {
        // Fall through to default on any parse failure.
    }
    return 30.0;
}

}  // namespace

void applyKeepaliveArgs(grpc::ChannelArguments& args) {
    // Keep long-lived channels (including event streams) alive through idle
    // NAT/proxy timeouts and surface dead connections promptly.
    args.SetInt(GRPC_ARG_KEEPALIVE_TIME_MS, 30000);
    args.SetInt(GRPC_ARG_KEEPALIVE_TIMEOUT_MS, 10000);
    args.SetInt(GRPC_ARG_KEEPALIVE_PERMIT_WITHOUT_CALLS, 1);
    args.SetInt(GRPC_ARG_HTTP2_MIN_SENT_PING_INTERVAL_WITHOUT_DATA_MS, 10000);
    args.SetInt(GRPC_ARG_HTTP2_MAX_PINGS_WITHOUT_DATA, 3);
}

// --- Client Implementation ---

Client::Client(std::shared_ptr<grpc::Channel> channel)
    : stub_(std::shared_ptr<kumiho::KumihoService::StubInterface>(
        ::kumiho::KumihoService::NewStub(channel))) {}

Client::Client(std::shared_ptr<kumiho::KumihoService::StubInterface> stub)
    : stub_(std::move(stub)) {}

void Client::setAuthToken(const std::string& token) {
    auth_token_ = token;
}

void Client::configureContext(grpc::ClientContext& context, bool with_deadline) const {
    // Add correlation ID for end-to-end tracing
    context.AddMetadata("x-correlation-id", generateCorrelationId());

    if (!auth_token_.empty()) {
        context.AddMetadata("authorization", "Bearer " + auth_token_);
    }

    // Apply a default per-RPC deadline for unary calls. Streaming RPCs opt out
    // (they pass with_deadline = false) so long-lived streams are not cut off.
    if (with_deadline) {
        const double seconds = defaultRpcTimeoutSeconds();
        const auto millis = static_cast<long long>(seconds * 1000.0);
        context.set_deadline(
            std::chrono::system_clock::now() + std::chrono::milliseconds(millis)
        );
    }
}

std::shared_ptr<Client> Client::createFromEnv() {
    const char* env_endpoint = std::getenv("KUMIHO_SERVER_ENDPOINT");
    const char* legacy_endpoint = std::getenv("KUMIHO_SERVER_ADDRESS");
    const bool has_explicit_endpoint =
        (env_endpoint && *env_endpoint != '\0') ||
        (legacy_endpoint && *legacy_endpoint != '\0');

    // Self-hosted CE auto-probe (cloud-safety invariant): only when the caller
    // supplied neither an explicit endpoint nor a resolved token. A user with a
    // token or explicit endpoint behaves exactly as before. On a CE hit we adopt
    // the tokenless loopback client and skip token loading + discovery entirely.
    if (!has_explicit_endpoint && !loadBearerToken().has_value()) {
        auto ce_client = clientFromLocalCe();
        if (ce_client) {
            return ce_client;
        }
    }

    std::string endpoint = env_endpoint ? env_endpoint : "";
    if (endpoint.empty()) {
        endpoint = legacy_endpoint ? legacy_endpoint : "localhost:50051";
    }

    EndpointConfig config = NormaliseEndpoint(endpoint);
    const char* force_tls = std::getenv("KUMIHO_SERVER_USE_TLS");
    if (force_tls) {
        config.use_tls = ParseFlag(force_tls);
    }

    const char* authority_override = std::getenv("KUMIHO_SERVER_AUTHORITY");
    if (authority_override && *authority_override != '\0') {
        config.authority = authority_override;
    }

    // Security: Warn if connecting to non-localhost without TLS
    bool isLocalhost = (config.authority == "localhost" || 
                        config.authority == "127.0.0.1" ||
                        config.authority == "::1");
    const char* require_tls_env = std::getenv("KUMIHO_REQUIRE_TLS");
    bool requireTls = ParseFlag(require_tls_env);
    
    if (!isLocalhost && !config.use_tls) {
        if (requireTls) {
            throw ValidationError(
                "TLS is required but connecting to " + config.authority + 
                " without TLS. Set KUMIHO_SERVER_USE_TLS=true or use https://.");
        }
        std::cerr << "Warning: Connecting to " << config.authority 
                  << " without TLS. Credentials may be transmitted in plaintext. "
                  << "Set KUMIHO_SERVER_USE_TLS=true for production." << std::endl;
    }

    grpc::ChannelArguments args;
    applyKeepaliveArgs(args);
    std::shared_ptr<grpc::ChannelCredentials> credentials;

    if (config.use_tls) {
        grpc::SslCredentialsOptions ssl_opts;
        const char* ca_file = std::getenv("KUMIHO_SERVER_CA_FILE");
        if (ca_file && *ca_file != '\0') {
            ssl_opts.pem_root_certs = ReadFileContents(ca_file);
        }
        credentials = grpc::SslCredentials(ssl_opts);
        args.SetString(GRPC_ARG_DEFAULT_AUTHORITY, config.authority);
        const char* override_host = std::getenv("KUMIHO_SSL_TARGET_OVERRIDE");
        if (override_host && *override_host != '\0') {
            args.SetString(GRPC_SSL_TARGET_NAME_OVERRIDE_ARG, override_host);
        }
    } else {
        credentials = grpc::InsecureChannelCredentials();
    }

    auto channel = grpc::CreateCustomChannel(config.address, credentials, args);
    auto client = std::make_shared<Client>(channel);
    
    // Load authentication token
    auto token = loadBearerToken();
    if (token) {
        client->setAuthToken(*token);
    }
    
    return client;
}

// --- Project Operations ---

std::shared_ptr<Project> Client::createProject(const std::string& name, const std::string& description) {
    ::kumiho::CreateProjectRequest req;
    req.set_name(name);
    req.set_description(description);

    ::kumiho::ProjectResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateProject(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::RESOURCE_EXHAUSTED) {
            throw ProjectLimitError(status.error_message());
        }
        throw RpcError("CreateProject failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Project>(res, this);
}

std::vector<std::shared_ptr<Project>> Client::getProjects() {
    ::kumiho::GetProjectsRequest req;
    ::kumiho::GetProjectsResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetProjects(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetProjects failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Project>> projects;
    for (const auto& pb : res.projects()) {
        projects.push_back(std::make_shared<Project>(pb, this));
    }
    return projects;
}

std::shared_ptr<Project> Client::getProject(const std::string& name) {
    auto projects = getProjects();
    for (const auto& project : projects) {
        if (project->getName() == name) {
            return project;
        }
    }
    return nullptr;
}

StatusResponse Client::deleteProject(const std::string& project_id, bool force) {
    ::kumiho::DeleteProjectRequest req;
    req.set_project_id(project_id);
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteProject(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteProject failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return StatusResponse{res.success(), res.message()};
}

std::shared_ptr<Project> Client::updateProject(
    const std::string& project_id,
    std::optional<bool> allow_public,
    std::optional<std::string> description
) {
    ::kumiho::UpdateProjectRequest req;
    req.set_project_id(project_id);
    if (allow_public.has_value()) {
        req.set_allow_public(allow_public.value());
    }
    if (description.has_value()) {
        req.set_description(description.value());
    }

    ::kumiho::ProjectResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UpdateProject(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UpdateProject failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Project>(res, this);
}

// --- Space Operations (formerly Group) ---

std::shared_ptr<Space> Client::createSpace(const std::string& parent_path, const std::string& name) {
    ::kumiho::CreateSpaceRequest req;
    req.set_parent_path(parent_path);
    req.set_space_name(name);

    ::kumiho::SpaceResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateSpace(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateSpace failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Space>(res, this);
}

std::shared_ptr<Space> Client::getSpace(const std::string& path) {
    ::kumiho::GetSpaceRequest req;
    req.set_path_or_kref(path);

    ::kumiho::SpaceResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetSpace(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            throw NotFoundError("Space not found: " + path);
        }
        throw RpcError("GetSpace failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Space>(res, this);
}

std::vector<std::shared_ptr<Space>> Client::getChildSpaces(
    const std::string& parent_path,
    bool recursive,
    std::optional<int32_t> page_size,
    std::optional<std::string> cursor
) {
    ::kumiho::GetChildSpacesRequest req;
    req.set_parent_path(parent_path);
    req.set_recursive(recursive);

    if (page_size.has_value() || cursor.has_value()) {
        auto* pagination = req.mutable_pagination();
        pagination->set_page_size(page_size.value_or(100));
        if (cursor.has_value()) pagination->set_cursor(cursor.value());
    }

    ::kumiho::GetChildSpacesResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetChildSpaces(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetChildSpaces failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Space>> spaces;
    for (const auto& pb : res.spaces()) {
        spaces.push_back(std::make_shared<Space>(pb, this));
    }
    return spaces;
}

PagedList<std::shared_ptr<Space>> Client::getChildSpacesPaged(
    const std::string& parent_path,
    bool recursive,
    int32_t page_size,
    const std::string& cursor
) {
    ::kumiho::GetChildSpacesRequest req;
    req.set_parent_path(parent_path);
    req.set_recursive(recursive);

    if (page_size > 0 || !cursor.empty()) {
        auto* pagination = req.mutable_pagination();
        pagination->set_page_size(page_size > 0 ? page_size : 100);
        if (!cursor.empty()) pagination->set_cursor(cursor);
    }

    ::kumiho::GetChildSpacesResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetChildSpaces(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetChildSpaces failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    PagedList<std::shared_ptr<Space>> result;
    for (const auto& pb : res.spaces()) {
        result.items.push_back(std::make_shared<Space>(pb, this));
    }

    if (res.has_pagination()) {
        result.next_cursor = res.pagination().next_cursor();
        result.total_count = res.pagination().total_count();
    }

    return result;
}

std::shared_ptr<Space> Client::updateSpaceMetadata(const Kref& kref, const Metadata& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    req.mutable_kref()->set_uri(kref.uri());
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::SpaceResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UpdateSpaceMetadata(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UpdateSpaceMetadata failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Space>(res, this);
}

StatusResponse Client::deleteSpace(const std::string& path, bool force) {
    ::kumiho::DeleteSpaceRequest req;
    req.set_path(path);
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteSpace(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteSpace failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return StatusResponse{res.success(), res.message()};
}

// --- Item Operations (formerly Product) ---

std::shared_ptr<Item> Client::createItem(const std::string& parent_path, const std::string& name, const std::string& kind, const Metadata& metadata) {
    if (isReservedKind(kind)) {
        throw ReservedKindError(
            "Item kind '" + kind + "' is reserved. Use createBundle() instead."
        );
    }

    ::kumiho::CreateItemRequest req;
    req.set_parent_path(parent_path);
    req.set_item_name(name);
    req.set_kind(kind);

    ::kumiho::ItemResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateItem(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateItem failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    // CreateItemRequest has no metadata field; mirror Python by applying any
    // supplied metadata via a follow-up UpdateItemMetadata call.
    if (!metadata.empty()) {
        updateItemMetadata(Kref(res.kref().uri()), metadata);
    }
    return std::make_shared<Item>(res, this);
}

std::shared_ptr<Item> Client::getItem(const std::string& parent_path, const std::string& name, const std::string& kind) {
    ::kumiho::GetItemRequest req;
    req.set_parent_path(parent_path);
    req.set_item_name(name);
    req.set_kind(kind);

    ::kumiho::ItemResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetItem(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            throw NotFoundError("Item not found: " + parent_path + "/" + name + "." + kind);
        }
        throw RpcError("GetItem failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Item>(res, this);
}

std::shared_ptr<Item> Client::getItemByKref(const std::string& kref_uri) {
    Kref kref(kref_uri);
    std::string path = kref.getPath();
    
    size_t slash_pos = path.rfind('/');
    if (slash_pos == std::string::npos) {
        throw ValidationError("Invalid item kref format: " + kref_uri);
    }
    
    std::string space_path = "/" + path.substr(0, slash_pos);
    std::string item_name_kind = path.substr(slash_pos + 1);
    
    size_t dot_pos = item_name_kind.find('.');
    if (dot_pos == std::string::npos) {
        throw ValidationError("Invalid item name.kind format: " + item_name_kind);
    }
    
    std::string item_name = item_name_kind.substr(0, dot_pos);
    std::string kind = item_name_kind.substr(dot_pos + 1);

    return getItem(space_path, item_name, kind);
}

std::shared_ptr<Item> Client::getItemFromRevision(const std::string& revision_kref) {
    auto revision = getRevision(revision_kref);
    return getItemByKref(revision->getItemKref());
}

std::vector<std::shared_ptr<Item>> Client::getItems(
    const std::string& parent_path,
    const std::string& item_name_filter,
    const std::string& kind_filter,
    bool include_deprecated,
    std::optional<int32_t> page_size,
    std::optional<std::string> cursor
) {
    ::kumiho::GetItemsRequest req;
    req.set_parent_path(parent_path);
    req.set_item_name_filter(item_name_filter);
    req.set_kind_filter(kind_filter);
    req.set_include_deprecated(include_deprecated);

    if (page_size.has_value() || cursor.has_value()) {
        auto* pagination = req.mutable_pagination();
        pagination->set_page_size(page_size.value_or(100));
        if (cursor.has_value()) pagination->set_cursor(cursor.value());
    }

    ::kumiho::GetItemsResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetItems(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetItems failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Item>> items;
    for (const auto& pb : res.items()) {
        items.push_back(std::make_shared<Item>(pb, this));
    }
    return items;
}

PagedList<std::shared_ptr<Item>> Client::itemSearch(
    const std::string& context_filter,
    const std::string& name_filter,
    const std::string& kind_filter,
    std::optional<int32_t> page_size,
    std::optional<std::string> cursor,
    bool include_deprecated
) {
    ::kumiho::ItemSearchRequest req;
    req.set_context_filter(context_filter);
    req.set_item_name_filter(name_filter);
    req.set_kind_filter(kind_filter);
    req.set_include_deprecated(include_deprecated);

    if (page_size.has_value() || cursor.has_value()) {
        auto* pagination = req.mutable_pagination();
        if (page_size.has_value()) pagination->set_page_size(page_size.value());
        if (cursor.has_value()) pagination->set_cursor(cursor.value());
    }

    ::kumiho::GetItemsResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->ItemSearch(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("ItemSearch failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    PagedList<std::shared_ptr<Item>> result;
    for (const auto& pb : res.items()) {
        result.items.push_back(std::make_shared<Item>(pb, this));
    }

    if (res.has_pagination()) {
        result.next_cursor = res.pagination().next_cursor();
        result.total_count = res.pagination().total_count();
    }

    return result;
}

std::shared_ptr<Item> Client::updateItemMetadata(const Kref& kref, const Metadata& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    *req.mutable_kref() = kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::ItemResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UpdateItemMetadata(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UpdateItemMetadata failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Item>(res, this);
}

void Client::deleteItem(const Kref& kref, bool force) {
    ::kumiho::DeleteItemRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteItem(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteItem failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

void Client::setItemDeprecated(const Kref& kref, bool deprecated) {
    ::kumiho::SetDeprecatedRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_deprecated(deprecated);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->SetDeprecated(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("SetDeprecated failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

// --- Revision Operations (formerly Version) ---

std::shared_ptr<Revision> Client::createRevision(const Kref& item_kref, const Metadata& metadata, int number, const std::string& embedding_text) {
    ::kumiho::CreateRevisionRequest req;
    *req.mutable_item_kref() = item_kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }
    req.set_number(number);
    if (!embedding_text.empty()) {
        req.set_embedding_text(embedding_text);
    }

    ::kumiho::RevisionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateRevision(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateRevision failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Revision>(res, this);
}

std::shared_ptr<Revision> Client::getRevision(const std::string& kref_uri) {
    // Parse kref_uri for tag/time parameters (?t=/?tag=/?time=) and resolve
    // those via ResolveKref, mirroring the Python client.
    std::string base_kref = kref_uri;
    std::string tag;
    std::string time;
    bool has_tag = false;
    bool has_time = false;

    auto qpos = kref_uri.find('?');
    if (qpos != std::string::npos) {
        base_kref = kref_uri.substr(0, qpos);
        std::string params = kref_uri.substr(qpos + 1);
        std::stringstream ss(params);
        std::string param;
        while (std::getline(ss, param, '&')) {
            if (param.rfind("t=", 0) == 0) {
                tag = param.substr(2);
                has_tag = true;
            } else if (param.rfind("tag=", 0) == 0) {
                tag = param.substr(4);
                has_tag = true;
            } else if (param.rfind("time=", 0) == 0) {
                time = param.substr(5);
                has_time = true;
                std::regex time_regex("^\\d{12}$");
                if (!std::regex_match(time, time_regex)) {
                    throw ValidationError("time must be in YYYYMMDDHHMM format");
                }
            }
        }
    }

    // Presence-based (like Python's `tag is not None`): an explicit ?t= with an
    // empty value still routes through ResolveKref, not the direct GetRevision.
    if (has_tag || has_time) {
        auto revision = resolveKref(base_kref, tag, time);
        if (!revision) {
            throw NotFoundError("Revision not found: " + kref_uri);
        }
        return revision;
    }

    ::kumiho::KrefRequest req;
    req.mutable_kref()->set_uri(kref_uri);

    ::kumiho::RevisionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetRevision(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            throw NotFoundError("Revision not found: " + kref_uri);
        }
        throw RpcError("GetRevision failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Revision>(res, this);
}

std::shared_ptr<Revision> Client::resolveKref(const std::string& kref_uri, const std::string& tag, const std::string& time) {
    std::string time_str = time;
    
    if (!time.empty()) {
        // Check if it's already ISO/RFC3339 format (contains 'T')
        if (time.find('T') != std::string::npos) {
            // Already in ISO format, pass through directly
            time_str = time;
        } else {
            // Validate YYYYMMDDHHMM format: exactly 12 digits
            std::regex time_regex("^\\d{12}$");
            if (!std::regex_match(time, time_regex)) {
                throw ValidationError("time must be in YYYYMMDDHHMM or ISO 8601 format (e.g., 2024-06-01T13:30:00Z)");
            }
            // Convert YYYYMMDDHHMM to ISO 8601 format for the server
            // Format: YYYY-MM-DDTHH:MM:59+00:00 (use :59 seconds to include the full minute)
            time_str = time.substr(0, 4) + "-" + time.substr(4, 2) + "-" + time.substr(6, 2) +
                       "T" + time.substr(8, 2) + ":" + time.substr(10, 2) + ":59+00:00";
        }
    }

    ::kumiho::ResolveKrefRequest req;
    req.set_kref(kref_uri);
    if (!tag.empty()) req.set_tag(tag);
    if (!time_str.empty()) req.set_time(time_str);

    ::kumiho::RevisionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->ResolveKref(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            return nullptr;
        }
        throw RpcError("ResolveKref failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Revision>(res, this);
}

std::optional<std::string> Client::resolve(const std::string& kref_uri) {
    // Resolve a kref to a file location via the server-side ResolveLocation RPC,
    // mirroring the Python client.resolve. Tag/time are parsed from the query
    // (?t=/?tag=/?time=) and passed explicitly; any failure yields nullopt.
    std::string tag;
    std::string time;
    const auto qpos = kref_uri.find('?');
    if (qpos != std::string::npos) {
        std::stringstream ss(kref_uri.substr(qpos + 1));
        std::string param;
        while (std::getline(ss, param, '&')) {
            if (param.rfind("t=", 0) == 0) {
                tag = param.substr(2);
            } else if (param.rfind("tag=", 0) == 0) {
                tag = param.substr(4);
            } else if (param.rfind("time=", 0) == 0) {
                time = param.substr(5);
            }
        }
    }

    ::kumiho::ResolveLocationRequest req;
    req.set_kref(kref_uri);
    if (!tag.empty()) req.set_tag(tag);
    if (!time.empty()) req.set_time(time);

    ::kumiho::ResolveLocationResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->ResolveLocation(&context, req, &res);
    if (!status.ok()) {
        return std::nullopt;
    }
    return res.location();
}

std::vector<std::shared_ptr<Revision>> Client::getRevisions(const Kref& item_kref) {
    ::kumiho::GetRevisionsRequest req;
    *req.mutable_item_kref() = item_kref.toPb();

    ::kumiho::GetRevisionsResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetRevisions(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetRevisions failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Revision>> revisions;
    for (const auto& pb : res.revisions()) {
        revisions.push_back(std::make_shared<Revision>(pb, this));
    }
    return revisions;
}

std::shared_ptr<Revision> Client::getLatestRevision(const Kref& item_kref) {
    // Mirrors Python get_latest_revision: resolve the item kref to its latest
    // revision; resolveKref returns nullptr on NOT_FOUND (no revisions).
    return resolveKref(item_kref.uri());
}

int Client::peekNextRevision(const Kref& item_kref) {
    ::kumiho::PeekNextRevisionRequest req;
    *req.mutable_item_kref() = item_kref.toPb();

    ::kumiho::PeekNextRevisionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->PeekNextRevision(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("PeekNextRevision failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return res.number();
}

std::shared_ptr<Revision> Client::updateRevisionMetadata(const Kref& kref, const Metadata& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    *req.mutable_kref() = kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::RevisionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UpdateRevisionMetadata(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UpdateRevisionMetadata failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Revision>(res, this);
}

void Client::tagRevision(const Kref& kref, const std::string& tag) {
    ::kumiho::TagRevisionRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_tag(tag);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->TagRevision(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("TagRevision failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

void Client::untagRevision(const Kref& kref, const std::string& tag) {
    ::kumiho::UnTagRevisionRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_tag(tag);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UnTagRevision(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UnTagRevision failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

bool Client::hasTag(const Kref& kref, const std::string& tag) {
    ::kumiho::HasTagRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_tag(tag);

    ::kumiho::HasTagResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->HasTag(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("HasTag failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return res.has_tag();
}

bool Client::wasTagged(const Kref& kref, const std::string& tag) {
    ::kumiho::WasTaggedRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_tag(tag);

    ::kumiho::WasTaggedResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->WasTagged(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("WasTagged failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return res.was_tagged();
}

void Client::setRevisionDeprecated(const Kref& kref, bool deprecated) {
    ::kumiho::SetDeprecatedRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_deprecated(deprecated);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->SetDeprecated(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("SetDeprecated failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

void Client::deleteRevision(const Kref& kref, bool force) {
    ::kumiho::DeleteRevisionRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteRevision(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteRevision failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

// --- Artifact Operations (formerly Resource) ---

std::shared_ptr<Artifact> Client::createArtifact(const Kref& revision_kref, const std::string& name, const std::string& location, const Metadata& metadata) {
    ::kumiho::CreateArtifactRequest req;
    *req.mutable_revision_kref() = revision_kref.toPb();
    req.set_name(name);
    req.set_location(location);
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::ArtifactResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateArtifact(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateArtifact failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Artifact>(res, this);
}

std::shared_ptr<Artifact> Client::getArtifact(const Kref& revision_kref, const std::string& name) {
    ::kumiho::GetArtifactRequest req;
    *req.mutable_revision_kref() = revision_kref.toPb();
    req.set_name(name);

    ::kumiho::ArtifactResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetArtifact(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            throw NotFoundError("Artifact not found: " + name);
        }
        throw RpcError("GetArtifact failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Artifact>(res, this);
}

std::shared_ptr<Artifact> Client::getArtifactByKref(const std::string& kref_uri) {
    Kref kref(kref_uri);
    std::string artifact_name = kref.getArtifactName();
    if (!artifact_name.empty()) {
        // Build the revision kref by removing the artifact part ("&a=...").
        std::string revision_kref_uri = kref_uri;
        auto pos = kref_uri.find("&a=");
        if (pos != std::string::npos) {
            revision_kref_uri = kref_uri.substr(0, pos);
        }
        return getArtifact(Kref(revision_kref_uri), artifact_name);
    }

    // No artifact name: interpret as a request for the default artifact of the
    // resolved revision (item kref -> latest revision; revision kref -> itself).
    auto revision = getRevision(kref_uri);
    auto default_name = revision->getDefaultArtifact();
    if (!default_name || default_name->empty()) {
        throw ValidationError(
            "Invalid artifact kref format: " + kref_uri +
            " (missing &a=artifact_name and no default_artifact set)"
        );
    }
    return getArtifact(revision->getKref(), *default_name);
}

std::vector<std::shared_ptr<Artifact>> Client::getArtifacts(const Kref& revision_kref) {
    ::kumiho::GetArtifactsRequest req;
    *req.mutable_revision_kref() = revision_kref.toPb();

    ::kumiho::GetArtifactsResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetArtifacts(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetArtifacts failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Artifact>> artifacts;
    for (const auto& pb : res.artifacts()) {
        artifacts.push_back(std::make_shared<Artifact>(pb, this));
    }
    return artifacts;
}

std::vector<std::shared_ptr<Artifact>> Client::getArtifactsByLocation(const std::string& location) {
    ::kumiho::GetArtifactsByLocationRequest req;
    req.set_location(location);

    ::kumiho::GetArtifactsByLocationResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetArtifactsByLocation(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetArtifactsByLocation failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Artifact>> artifacts;
    for (const auto& pb : res.artifacts()) {
        artifacts.push_back(std::make_shared<Artifact>(pb, this));
    }
    return artifacts;
}

void Client::setDefaultArtifact(const Kref& revision_kref, const std::string& artifact_name) {
    ::kumiho::SetDefaultArtifactRequest req;
    *req.mutable_revision_kref() = revision_kref.toPb();
    req.set_artifact_name(artifact_name);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->SetDefaultArtifact(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("SetDefaultArtifact failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

std::shared_ptr<Artifact> Client::updateArtifactMetadata(const Kref& kref, const Metadata& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    *req.mutable_kref() = kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::ArtifactResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UpdateArtifactMetadata(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UpdateArtifactMetadata failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Artifact>(res, this);
}

void Client::deleteArtifact(const Kref& kref, bool force) {
    ::kumiho::DeleteArtifactRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteArtifact(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteArtifact failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

void Client::setArtifactDeprecated(const Kref& kref, bool deprecated) {
    ::kumiho::SetDeprecatedRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_deprecated(deprecated);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->SetDeprecated(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("SetDeprecated failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

// --- Edge Operations (formerly Link) ---

std::shared_ptr<Edge> Client::createEdge(
    const Kref& source_kref,
    const Kref& target_kref,
    const std::string& edge_type,
    const Metadata& metadata
) {
    validateEdgeType(edge_type);

    ::kumiho::CreateEdgeRequest req;
    *req.mutable_source_revision_kref() = source_kref.toPb();
    *req.mutable_target_revision_kref() = target_kref.toPb();
    req.set_edge_type(edge_type);
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateEdge(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateEdge failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    // Construct Edge object from request data
    ::kumiho::Edge edge_pb;
    *edge_pb.mutable_source_kref() = source_kref.toPb();
    *edge_pb.mutable_target_kref() = target_kref.toPb();
    edge_pb.set_edge_type(edge_type);
    for (const auto& pair : metadata) {
        (*edge_pb.mutable_metadata())[pair.first] = pair.second;
    }

    return std::make_shared<Edge>(edge_pb, this);
}

std::vector<std::shared_ptr<Edge>> Client::getEdges(const Kref& kref, const std::string& edge_type_filter, EdgeDirection direction) {
    ::kumiho::GetEdgesRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_edge_type_filter(edge_type_filter);
    req.set_direction(static_cast<::kumiho::EdgeDirection>(static_cast<int>(direction)));

    ::kumiho::GetEdgesResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetEdges(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetEdges failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Edge>> edges;
    for (const auto& pb : res.edges()) {
        edges.push_back(std::make_shared<Edge>(pb, this));
    }
    return edges;
}

void Client::deleteEdge(const Kref& source_kref, const Kref& target_kref, const std::string& edge_type) {
    validateEdgeType(edge_type);

    ::kumiho::DeleteEdgeRequest req;
    *req.mutable_source_kref() = source_kref.toPb();
    *req.mutable_target_kref() = target_kref.toPb();
    req.set_edge_type(edge_type);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteEdge(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteEdge failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

// --- Graph Traversal Operations ---

TraversalResult Client::traverseEdges(
    const Kref& origin_kref,
    int direction,
    const std::vector<std::string>& edge_type_filter,
    int max_depth,
    int limit,
    bool include_path
) {
    ::kumiho::TraverseEdgesRequest req;
    *req.mutable_origin_kref() = origin_kref.toPb();
    req.set_direction(static_cast<::kumiho::EdgeDirection>(direction));
    for (const auto& et : edge_type_filter) {
        req.add_edge_type_filter(et);
    }
    req.set_max_depth(max_depth);
    req.set_limit(limit);
    req.set_include_path(include_path);

    ::kumiho::TraverseEdgesResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->TraverseEdges(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("TraverseEdges failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    TraversalResult result;
    result.total_count = res.total_count();
    result.truncated = res.truncated();

    // Convert paths
    for (const auto& pb_path : res.paths()) {
        RevisionPath path;
        path.total_depth = pb_path.total_depth();
        for (const auto& pb_step : pb_path.steps()) {
            PathStep step;
            step.revision_kref = pb_step.revision_kref().uri();
            step.edge_type = pb_step.edge_type();
            step.depth = pb_step.depth();
            path.steps.push_back(step);
        }
        result.paths.push_back(path);
    }

    // Convert revision krefs
    for (const auto& pb_kref : res.revision_krefs()) {
        result.revision_krefs.push_back(pb_kref.uri());
    }

    // Convert edges
    for (const auto& pb_edge : res.edges()) {
        result.edges.push_back(std::make_shared<Edge>(pb_edge, this));
    }

    return result;
}

ShortestPathResult Client::findShortestPath(
    const Kref& source_kref,
    const Kref& target_kref,
    const std::vector<std::string>& edge_type_filter,
    int max_depth,
    bool all_shortest
) {
    ::kumiho::ShortestPathRequest req;
    *req.mutable_source_kref() = source_kref.toPb();
    *req.mutable_target_kref() = target_kref.toPb();
    for (const auto& et : edge_type_filter) {
        req.add_edge_type_filter(et);
    }
    req.set_max_depth(max_depth);
    req.set_all_shortest(all_shortest);

    ::kumiho::ShortestPathResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->FindShortestPath(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("FindShortestPath failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    ShortestPathResult result;
    result.path_exists = res.path_exists();
    result.path_length = res.path_length();

    // Convert paths
    for (const auto& pb_path : res.paths()) {
        RevisionPath path;
        path.total_depth = pb_path.total_depth();
        for (const auto& pb_step : pb_path.steps()) {
            PathStep step;
            step.revision_kref = pb_step.revision_kref().uri();
            step.edge_type = pb_step.edge_type();
            step.depth = pb_step.depth();
            path.steps.push_back(step);
        }
        result.paths.push_back(path);
    }

    return result;
}

ImpactAnalysisResult Client::analyzeImpact(
    const Kref& revision_kref,
    const std::vector<std::string>& edge_type_filter,
    int max_depth,
    int limit
) {
    ::kumiho::ImpactAnalysisRequest req;
    *req.mutable_revision_kref() = revision_kref.toPb();
    for (const auto& et : edge_type_filter) {
        req.add_edge_type_filter(et);
    }
    req.set_max_depth(max_depth);
    req.set_limit(limit);

    ::kumiho::ImpactAnalysisResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->AnalyzeImpact(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("AnalyzeImpact failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    ImpactAnalysisResult result;
    result.total_impacted = res.total_impacted();
    result.truncated = res.truncated();

    // Convert impacted revisions
    for (const auto& pb_ir : res.impacted_revisions()) {
        ImpactedRevision ir;
        ir.revision_kref = pb_ir.revision_kref().uri();
        ir.item_kref = pb_ir.item_kref().uri();
        ir.impact_depth = pb_ir.impact_depth();
        for (const auto& pt : pb_ir.impact_path_types()) {
            ir.impact_path_types.push_back(pt);
        }
        result.impacted_revisions.push_back(ir);
    }

    return result;
}

// --- Attribute Operations ---

std::optional<std::string> Client::getAttribute(const Kref& kref, const std::string& key) {
    ::kumiho::GetAttributeRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_key(key);

    ::kumiho::GetAttributeResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetAttribute(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetAttribute failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    if (res.exists()) {
        return res.value();
    }
    return std::nullopt;
}

bool Client::setAttribute(const Kref& kref, const std::string& key, const std::string& value) {
    ::kumiho::SetAttributeRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_key(key);
    req.set_value(value);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->SetAttribute(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("SetAttribute failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return res.success();
}

bool Client::deleteAttribute(const Kref& kref, const std::string& key) {
    ::kumiho::DeleteAttributeRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_key(key);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteAttribute(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteAttribute failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return res.success();
}

// --- Bundle Operations (formerly Collection) ---

std::shared_ptr<Bundle> Client::createBundle(const std::string& parent_path, const std::string& name, const Metadata& metadata) {
    ::kumiho::CreateBundleRequest req;
    req.set_parent_path(parent_path);
    req.set_bundle_name(name);
    // CreateBundleRequest carries metadata directly (unlike CreateItemRequest);
    // mirror Python create_bundle which passes metadata in the request.
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::ItemResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateBundle(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateBundle failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Bundle>(res, this);
}

std::shared_ptr<Bundle> Client::createBundle(const Kref& parent_kref, const std::string& name, const Metadata& metadata) {
    // Convert Kref to path (Kref format: kref://project/path/to/space)
    std::string path = "/" + parent_kref.getPath();
    return createBundle(path, name, metadata);
}

std::shared_ptr<Bundle> Client::getBundle(const std::string& parent_path, const std::string& name) {
    // Bundle is an item with kind "bundle"
    ::kumiho::GetItemRequest req;
    req.set_parent_path(parent_path);
    req.set_item_name(name);
    req.set_kind("bundle");

    ::kumiho::ItemResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetItem(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            throw NotFoundError("Bundle not found: " + parent_path + "/" + name + ".bundle");
        }
        throw RpcError("GetItem failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Bundle>(res, this);
}

std::shared_ptr<Bundle> Client::getBundleByKref(const std::string& kref_uri) {
    // Verify the referenced item is a bundle.
    auto item = getItemByKref(kref_uri);
    if (item->getKind() != "bundle") {
        throw ValidationError(
            "Item '" + kref_uri + "' is not a bundle (kind='" + item->getKind() + "'). "
            "Use getItem() for non-bundle items."
        );
    }

    // Parse the kref path: parent space path (with leading '/') is everything
    // before the last '/', and the bundle name is the last segment before '.'.
    Kref kref(kref_uri);
    std::string path = kref.getPath();
    size_t slash_pos = path.rfind('/');
    if (slash_pos == std::string::npos) {
        throw ValidationError("Invalid bundle kref format: " + kref_uri);
    }

    std::string parent_path = "/" + path.substr(0, slash_pos);
    std::string item_name_kind = path.substr(slash_pos + 1);
    size_t dot_pos = item_name_kind.find('.');
    std::string bundle_name =
        (dot_pos == std::string::npos) ? item_name_kind : item_name_kind.substr(0, dot_pos);

    return getBundle(parent_path, bundle_name);
}

BundleMemberResult Client::addBundleMember(const Kref& bundle_kref, const Kref& item_kref, const Metadata& metadata) {
    ::kumiho::AddBundleMemberRequest req;
    *req.mutable_bundle_kref() = bundle_kref.toPb();
    *req.mutable_member_item_kref() = item_kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::AddBundleMemberResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->AddBundleMember(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("AddBundleMember failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    BundleMemberResult result;
    result.success = res.success();
    result.message = res.message();
    if (res.has_new_revision()) {
        result.new_revision = std::make_shared<Revision>(res.new_revision(), this);
    }
    return result;
}

BundleMemberResult Client::removeBundleMember(const Kref& bundle_kref, const Kref& item_kref, const Metadata& metadata) {
    ::kumiho::RemoveBundleMemberRequest req;
    *req.mutable_bundle_kref() = bundle_kref.toPb();
    *req.mutable_member_item_kref() = item_kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::RemoveBundleMemberResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->RemoveBundleMember(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("RemoveBundleMember failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    BundleMemberResult result;
    result.success = res.success();
    result.message = res.message();
    if (res.has_new_revision()) {
        result.new_revision = std::make_shared<Revision>(res.new_revision(), this);
    }
    return result;
}

std::vector<BundleMember> Client::getBundleMembers(const Kref& bundle_kref, int revision_number) {
    ::kumiho::GetBundleMembersRequest req;
    *req.mutable_bundle_kref() = bundle_kref.toPb();
    if (revision_number > 0) {
        req.set_revision_number(revision_number);
    }

    ::kumiho::GetBundleMembersResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetBundleMembers(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetBundleMembers failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<BundleMember> members;
    for (const auto& pb : res.members()) {
        BundleMember member;
        member.item_kref = Kref(pb.item_kref().uri());
        member.added_at = pb.added_at();
        member.added_by = pb.added_by();
        member.added_by_username = pb.added_by_username();
        member.added_in_revision = pb.added_in_revision();
        members.push_back(member);
    }
    return members;
}

std::vector<BundleRevisionHistory> Client::getBundleHistory(const Kref& bundle_kref) {
    ::kumiho::GetBundleHistoryRequest req;
    *req.mutable_bundle_kref() = bundle_kref.toPb();

    ::kumiho::GetBundleHistoryResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetBundleHistory(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetBundleHistory failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<BundleRevisionHistory> history;
    for (const auto& pb : res.history()) {
        BundleRevisionHistory entry;
        entry.revision_number = pb.revision_number();
        entry.action = pb.action();
        if (pb.has_member_item_kref()) {
            entry.member_item_kref = Kref(pb.member_item_kref().uri());
        }
        entry.author = pb.author();
        entry.username = pb.username();
        entry.created_at = pb.created_at();
        entry.metadata = {pb.metadata().begin(), pb.metadata().end()};
        history.push_back(entry);
    }
    return history;
}

// --- Tenant Operations ---

TenantUsage Client::getTenantUsage() {
    ::kumiho::GetTenantUsageRequest req;
    ::kumiho::TenantUsageResponse res;
    grpc::ClientContext context; configureContext(context);
    
    grpc::Status status = stub_->GetTenantUsage(&context, req, &res);
    
    if (!status.ok()) {
        throw RpcError("GetTenantUsage failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    
    TenantUsage usage;
    usage.node_count = res.node_count();
    usage.node_limit = res.node_limit();
    usage.tenant_id = res.tenant_id();
    return usage;
}

// --- Event Streaming ---

std::shared_ptr<EventStream> Client::eventStream(const std::string& routing_key_filter, const std::string& kref_filter) {
    ::kumiho::EventStreamRequest request;
    request.set_routing_key_filter(routing_key_filter);
    request.set_kref_filter(kref_filter);

    context_ = std::make_shared<grpc::ClientContext>();
    // Streaming RPC: configure auth/correlation but opt out of the per-RPC
    // deadline so the stream is not cut off after KUMIHO_RPC_TIMEOUT_SECONDS.
    configureContext(*context_, /*with_deadline=*/false);

    std::unique_ptr<grpc::ClientReaderInterface<::kumiho::Event>> reader =
        stub_->EventStream(context_.get(), request);
    return std::make_shared<EventStream>(std::move(reader));
}

EventCapabilities Client::getEventCapabilities() {
    ::kumiho::GetEventCapabilitiesRequest req;
    ::kumiho::EventCapabilities res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetEventCapabilities(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetEventCapabilities failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    EventCapabilities caps;
    caps.supports_replay = res.supports_replay();
    caps.supports_cursor = res.supports_cursor();
    caps.supports_consumer_groups = res.supports_consumer_groups();
    caps.max_retention_hours = res.max_retention_hours();
    caps.max_buffer_size = res.max_buffer_size();
    caps.tier = res.tier();
    return caps;
}

// --- Convenience Functions ---

std::shared_ptr<Space> createSpace(std::shared_ptr<Client> client, const std::string& path) {
    std::vector<std::string> parts;
    std::stringstream ss(path);
    std::string part;

    while (std::getline(ss, part, '/')) {
        if (!part.empty()) {
            parts.push_back(part);
        }
    }

    if (parts.empty()) {
        throw ValidationError("Invalid path: " + path);
    }

    std::string current_path = "/";
    std::shared_ptr<Space> space;

    for (const auto& p : parts) {
        current_path += p;
        try {
            space = client->getSpace(current_path);
        } catch (const NotFoundError&) {
            // Space doesn't exist, create it
            std::string parent_path = current_path.substr(0, current_path.length() - p.length());
            if (parent_path.empty()) parent_path = "/";
            space = client->createSpace(parent_path, p);
        }
        current_path += "/";
    }

    return space;
}

std::string getCurrentUser() {
#ifdef _WIN32
    char* username = nullptr;
    size_t size = 0;
    if (_dupenv_s(&username, &size, "USERNAME") == 0 && username != nullptr) {
        std::string result(username);
        free(username);
        return result;
    }
#else
    const char* username = std::getenv("USERNAME");
    if (username) {
        return std::string(username);
    }
    username = std::getenv("USER");
    if (username) {
        return std::string(username);
    }
#endif
    return "unknown";
}

} // namespace api
} // namespace kumiho
