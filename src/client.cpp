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

}  // namespace

// --- Client Implementation ---

Client::Client(std::shared_ptr<grpc::Channel> channel)
    : stub_(std::shared_ptr<kumiho::KumihoService::StubInterface>(
        ::kumiho::KumihoService::NewStub(channel))) {}

Client::Client(std::shared_ptr<kumiho::KumihoService::StubInterface> stub)
    : stub_(std::move(stub)) {}

void Client::setAuthToken(const std::string& token) {
    auth_token_ = token;
}

void Client::configureContext(grpc::ClientContext& context) const {
    // Add correlation ID for end-to-end tracing
    context.AddMetadata("x-correlation-id", generateCorrelationId());
    
    if (!auth_token_.empty()) {
        context.AddMetadata("authorization", "Bearer " + auth_token_);
    }
}

std::shared_ptr<Client> Client::createFromEnv() {
    const char* env_endpoint = std::getenv("KUMIHO_SERVER_ENDPOINT");
    std::string endpoint = env_endpoint ? env_endpoint : "";
    if (endpoint.empty()) {
        const char* legacy = std::getenv("KUMIHO_SERVER_ADDRESS");
        endpoint = legacy ? legacy : "localhost:50051";
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

void Client::deleteProject(const std::string& project_id, bool force) {
    ::kumiho::DeleteProjectRequest req;
    req.set_project_id(project_id);
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteProject(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteProject failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
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

std::vector<std::shared_ptr<Space>> Client::getChildSpaces(const std::string& parent_path) {
    ::kumiho::GetChildSpacesRequest req;
    req.set_parent_path(parent_path);

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

void Client::deleteSpace(const std::string& path, bool force) {
    ::kumiho::DeleteSpaceRequest req;
    req.set_path(path);
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteSpace(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteSpace failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

// --- Item Operations (formerly Product) ---

std::shared_ptr<Item> Client::createItem(const std::string& parent_path, const std::string& name, const std::string& kind) {
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

PagedList<std::shared_ptr<Item>> Client::itemSearch(
    const std::string& context_filter,
    const std::string& name_filter,
    const std::string& kind_filter,
    std::optional<int32_t> page_size,
    std::optional<std::string> cursor
) {
    ::kumiho::ItemSearchRequest req;
    req.set_context_filter(context_filter);
    req.set_item_name_filter(name_filter);
    req.set_kind_filter(kind_filter);

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

std::shared_ptr<Revision> Client::createRevision(const Kref& item_kref, const Metadata& metadata, int number) {
    ::kumiho::CreateRevisionRequest req;
    *req.mutable_item_kref() = item_kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }
    req.set_number(number);

    ::kumiho::RevisionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateRevision(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateRevision failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Revision>(res, this);
}

std::shared_ptr<Revision> Client::getRevision(const std::string& kref_uri) {
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
    Kref kref(kref_uri);
    std::string path = kref.getPath();
    
    // Try to get revision and resolve to default artifact location
    try {
        auto revision = resolveKref(kref_uri);
        if (revision) {
            auto default_res = revision->getDefaultArtifact();
            if (default_res) {
                auto artifact = revision->getArtifact(*default_res);
                return artifact->getLocation();
            }
            // Fallback to first artifact
            auto artifacts = revision->getArtifacts();
            if (!artifacts.empty()) {
                return artifacts[0]->getLocation();
            }
        }
    } catch (...) {
        // Fall through
    }
    
    return std::nullopt;
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

std::shared_ptr<Artifact> Client::createArtifact(const Kref& revision_kref, const std::string& name, const std::string& location) {
    ::kumiho::CreateArtifactRequest req;
    *req.mutable_revision_kref() = revision_kref.toPb();
    req.set_name(name);
    req.set_location(location);

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

std::vector<std::shared_ptr<Edge>> Client::getEdges(const Kref& kref, const std::string& edge_type_filter) {
    ::kumiho::GetEdgesRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_edge_type_filter(edge_type_filter);

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

std::shared_ptr<Bundle> Client::createBundle(const std::string& parent_path, const std::string& name) {
    ::kumiho::CreateBundleRequest req;
    req.set_parent_path(parent_path);
    req.set_bundle_name(name);

    ::kumiho::ItemResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateBundle(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateBundle failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Bundle>(res, this);
}

std::shared_ptr<Bundle> Client::createBundle(const Kref& parent_kref, const std::string& name) {
    // Convert Kref to path (Kref format: kref://project/path/to/space)
    std::string path = "/" + parent_kref.getPath();
    return createBundle(path, name);
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

void Client::addBundleMember(const Kref& bundle_kref, const Kref& item_kref) {
    ::kumiho::AddBundleMemberRequest req;
    *req.mutable_bundle_kref() = bundle_kref.toPb();
    *req.mutable_member_item_kref() = item_kref.toPb();

    ::kumiho::AddBundleMemberResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->AddBundleMember(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("AddBundleMember failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

void Client::removeBundleMember(const Kref& bundle_kref, const Kref& item_kref) {
    ::kumiho::RemoveBundleMemberRequest req;
    *req.mutable_bundle_kref() = bundle_kref.toPb();
    *req.mutable_member_item_kref() = item_kref.toPb();

    ::kumiho::RemoveBundleMemberResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->RemoveBundleMember(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("RemoveBundleMember failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

std::vector<BundleMember> Client::getBundleMembers(const Kref& bundle_kref) {
    ::kumiho::GetBundleMembersRequest req;
    *req.mutable_bundle_kref() = bundle_kref.toPb();

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

    std::unique_ptr<grpc::ClientReaderInterface<::kumiho::Event>> reader = 
        stub_->EventStream(context_.get(), request);
    return std::make_shared<EventStream>(std::move(reader));
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
