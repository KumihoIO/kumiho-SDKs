/**
 * @file client.cpp
 * @brief Implementation of Client class with all gRPC operations.
 */

#include "kumiho/client.hpp"
#include "kumiho/project.hpp"
#include "kumiho/group.hpp"
#include "kumiho/product.hpp"
#include "kumiho/version.hpp"
#include "kumiho/resource.hpp"
#include "kumiho/link.hpp"
#include "kumiho/collection.hpp"
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

// --- Group Operations ---

std::shared_ptr<Group> Client::createGroup(const std::string& parent_path, const std::string& name) {
    ::kumiho::CreateGroupRequest req;
    req.set_parent_path(parent_path);
    req.set_group_name(name);

    ::kumiho::GroupResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateGroup(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateGroup failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Group>(res, this);
}

std::shared_ptr<Group> Client::getGroup(const std::string& path) {
    ::kumiho::GetGroupRequest req;
    req.set_path_or_kref(path);

    ::kumiho::GroupResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetGroup(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            throw NotFoundError("Group not found: " + path);
        }
        throw RpcError("GetGroup failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Group>(res, this);
}

std::vector<std::shared_ptr<Group>> Client::getChildGroups(const std::string& parent_path) {
    ::kumiho::GetChildGroupsRequest req;
    req.set_parent_path(parent_path);

    ::kumiho::GetChildGroupsResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetChildGroups(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetChildGroups failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Group>> groups;
    for (const auto& pb : res.groups()) {
        groups.push_back(std::make_shared<Group>(pb, this));
    }
    return groups;
}

std::shared_ptr<Group> Client::updateGroupMetadata(const Kref& kref, const Metadata& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    req.mutable_kref()->set_uri(kref.uri());
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::GroupResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UpdateGroupMetadata(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UpdateGroupMetadata failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Group>(res, this);
}

void Client::deleteGroup(const std::string& path, bool force) {
    ::kumiho::DeleteGroupRequest req;
    req.set_path(path);
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteGroup(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteGroup failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

// --- Product Operations ---

std::shared_ptr<Product> Client::createProduct(const std::string& parent_path, const std::string& name, const std::string& ptype) {
    if (isReservedProductType(ptype)) {
        throw ReservedProductTypeError(
            "Product type '" + ptype + "' is reserved. Use createCollection() instead."
        );
    }

    ::kumiho::CreateProductRequest req;
    req.set_parent_path(parent_path);
    req.set_product_name(name);
    req.set_product_type(ptype);

    ::kumiho::ProductResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateProduct(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateProduct failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Product>(res, this);
}

std::shared_ptr<Product> Client::getProduct(const std::string& parent_path, const std::string& name, const std::string& ptype) {
    ::kumiho::GetProductRequest req;
    req.set_parent_path(parent_path);
    req.set_product_name(name);
    req.set_product_type(ptype);

    ::kumiho::ProductResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetProduct(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            throw NotFoundError("Product not found: " + parent_path + "/" + name + "." + ptype);
        }
        throw RpcError("GetProduct failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Product>(res, this);
}

std::shared_ptr<Product> Client::getProductByKref(const std::string& kref_uri) {
    Kref kref(kref_uri);
    std::string path = kref.getPath();
    
    size_t slash_pos = path.rfind('/');
    if (slash_pos == std::string::npos) {
        throw ValidationError("Invalid product kref format: " + kref_uri);
    }
    
    std::string group_path = "/" + path.substr(0, slash_pos);
    std::string product_name_type = path.substr(slash_pos + 1);
    
    size_t dot_pos = product_name_type.find('.');
    if (dot_pos == std::string::npos) {
        throw ValidationError("Invalid product name.type format: " + product_name_type);
    }
    
    std::string product_name = product_name_type.substr(0, dot_pos);
    std::string product_type = product_name_type.substr(dot_pos + 1);
    
    return getProduct(group_path, product_name, product_type);
}

std::vector<std::shared_ptr<Product>> Client::productSearch(
    const std::string& context_filter,
    const std::string& name_filter,
    const std::string& ptype_filter
) {
    ::kumiho::ProductSearchRequest req;
    req.set_context_filter(context_filter);
    req.set_product_name_filter(name_filter);
    req.set_product_type_filter(ptype_filter);

    ::kumiho::GetProductsResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->ProductSearch(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("ProductSearch failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Product>> products;
    for (const auto& pb : res.products()) {
        products.push_back(std::make_shared<Product>(pb, this));
    }
    return products;
}

std::shared_ptr<Product> Client::updateProductMetadata(const Kref& kref, const Metadata& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    *req.mutable_kref() = kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::ProductResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UpdateProductMetadata(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UpdateProductMetadata failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Product>(res, this);
}

void Client::deleteProduct(const Kref& kref, bool force) {
    ::kumiho::DeleteProductRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteProduct(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteProduct failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

void Client::setProductDeprecated(const Kref& kref, bool deprecated) {
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

// --- Version Operations ---

std::shared_ptr<Version> Client::createVersion(const Kref& product_kref, const Metadata& metadata, int number) {
    ::kumiho::CreateVersionRequest req;
    *req.mutable_product_kref() = product_kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }
    req.set_number(number);

    ::kumiho::VersionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateVersion(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateVersion failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Version>(res, this);
}

std::shared_ptr<Version> Client::getVersion(const std::string& kref_uri) {
    ::kumiho::KrefRequest req;
    req.mutable_kref()->set_uri(kref_uri);

    ::kumiho::VersionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetVersion(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            throw NotFoundError("Version not found: " + kref_uri);
        }
        throw RpcError("GetVersion failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Version>(res, this);
}

std::shared_ptr<Version> Client::resolveKref(const std::string& kref_uri, const std::string& tag, const std::string& time) {
    if (!time.empty()) {
        // Validate time format: exactly 12 digits (YYYYMMDDHHMM)
        std::regex time_regex("^\\d{12}$");
        if (!std::regex_match(time, time_regex)) {
            throw ValidationError("time must be in YYYYMMDDHHMM format");
        }
    }

    ::kumiho::ResolveKrefRequest req;
    req.set_kref(kref_uri);
    if (!tag.empty()) req.set_tag(tag);
    if (!time.empty()) req.set_time(time);

    ::kumiho::VersionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->ResolveKref(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            return nullptr;
        }
        throw RpcError("ResolveKref failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Version>(res, this);
}

std::optional<std::string> Client::resolve(const std::string& kref_uri) {
    Kref kref(kref_uri);
    std::string path = kref.getPath();
    
    // Try to get version and resolve to default resource location
    try {
        auto version = resolveKref(kref_uri);
        if (version) {
            auto default_res = version->getDefaultResource();
            if (default_res) {
                auto resource = version->getResource(*default_res);
                return resource->getLocation();
            }
            // Fallback to first resource
            auto resources = version->getResources();
            if (!resources.empty()) {
                return resources[0]->getLocation();
            }
        }
    } catch (...) {
        // Fall through
    }
    
    return std::nullopt;
}

std::vector<std::shared_ptr<Version>> Client::getVersions(const Kref& product_kref) {
    ::kumiho::GetVersionsRequest req;
    *req.mutable_product_kref() = product_kref.toPb();

    ::kumiho::GetVersionsResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetVersions(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetVersions failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Version>> versions;
    for (const auto& pb : res.versions()) {
        versions.push_back(std::make_shared<Version>(pb, this));
    }
    return versions;
}

int Client::peekNextVersion(const Kref& product_kref) {
    ::kumiho::PeekNextVersionRequest req;
    *req.mutable_product_kref() = product_kref.toPb();

    ::kumiho::PeekNextVersionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->PeekNextVersion(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("PeekNextVersion failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return res.number();
}

std::shared_ptr<Version> Client::updateVersionMetadata(const Kref& kref, const Metadata& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    *req.mutable_kref() = kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::VersionResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UpdateVersionMetadata(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UpdateVersionMetadata failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Version>(res, this);
}

void Client::tagVersion(const Kref& kref, const std::string& tag) {
    ::kumiho::TagVersionRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_tag(tag);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->TagVersion(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("TagVersion failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

void Client::untagVersion(const Kref& kref, const std::string& tag) {
    ::kumiho::UnTagVersionRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_tag(tag);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UnTagVersion(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UnTagVersion failed: " + status.error_message(), static_cast<int>(status.error_code()));
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

void Client::setVersionDeprecated(const Kref& kref, bool deprecated) {
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

void Client::deleteVersion(const Kref& kref, bool force) {
    ::kumiho::DeleteVersionRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteVersion(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteVersion failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

// --- Resource Operations ---

std::shared_ptr<Resource> Client::createResource(const Kref& version_kref, const std::string& name, const std::string& location) {
    ::kumiho::CreateResourceRequest req;
    *req.mutable_version_kref() = version_kref.toPb();
    req.set_name(name);
    req.set_location(location);

    ::kumiho::ResourceResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateResource(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateResource failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Resource>(res, this);
}

std::shared_ptr<Resource> Client::getResource(const Kref& version_kref, const std::string& name) {
    ::kumiho::GetResourceRequest req;
    *req.mutable_version_kref() = version_kref.toPb();
    req.set_name(name);

    ::kumiho::ResourceResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetResource(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            throw NotFoundError("Resource not found: " + name);
        }
        throw RpcError("GetResource failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Resource>(res, this);
}

std::vector<std::shared_ptr<Resource>> Client::getResources(const Kref& version_kref) {
    ::kumiho::GetResourcesRequest req;
    *req.mutable_version_kref() = version_kref.toPb();

    ::kumiho::GetResourcesResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetResources(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetResources failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Resource>> resources;
    for (const auto& pb : res.resources()) {
        resources.push_back(std::make_shared<Resource>(pb, this));
    }
    return resources;
}

std::vector<std::shared_ptr<Resource>> Client::getResourcesByLocation(const std::string& location) {
    ::kumiho::GetResourcesByLocationRequest req;
    req.set_location(location);

    ::kumiho::GetResourcesByLocationResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetResourcesByLocation(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetResourcesByLocation failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Resource>> resources;
    for (const auto& pb : res.resources()) {
        resources.push_back(std::make_shared<Resource>(pb, this));
    }
    return resources;
}

void Client::setDefaultResource(const Kref& version_kref, const std::string& resource_name) {
    ::kumiho::SetDefaultResourceRequest req;
    *req.mutable_version_kref() = version_kref.toPb();
    req.set_resource_name(resource_name);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->SetDefaultResource(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("SetDefaultResource failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

std::shared_ptr<Resource> Client::updateResourceMetadata(const Kref& kref, const Metadata& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    *req.mutable_kref() = kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::ResourceResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->UpdateResourceMetadata(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("UpdateResourceMetadata failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Resource>(res, this);
}

void Client::deleteResource(const Kref& kref, bool force) {
    ::kumiho::DeleteResourceRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_force(force);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteResource(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteResource failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

void Client::setResourceDeprecated(const Kref& kref, bool deprecated) {
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

// --- Link Operations ---

std::shared_ptr<Link> Client::createLink(
    const Kref& source_kref,
    const Kref& target_kref,
    const std::string& link_type,
    const Metadata& metadata
) {
    validateLinkType(link_type);

    ::kumiho::CreateLinkRequest req;
    *req.mutable_source_version_kref() = source_kref.toPb();
    *req.mutable_target_version_kref() = target_kref.toPb();
    req.set_link_type(link_type);
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateLink(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateLink failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    // Construct Link object from request data
    ::kumiho::Link link_pb;
    *link_pb.mutable_source_kref() = source_kref.toPb();
    *link_pb.mutable_target_kref() = target_kref.toPb();
    link_pb.set_link_type(link_type);
    for (const auto& pair : metadata) {
        (*link_pb.mutable_metadata())[pair.first] = pair.second;
    }

    return std::make_shared<Link>(link_pb, this);
}

std::vector<std::shared_ptr<Link>> Client::getLinks(const Kref& kref, const std::string& link_type_filter) {
    ::kumiho::GetLinksRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_link_type_filter(link_type_filter);

    ::kumiho::GetLinksResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetLinks(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetLinks failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<std::shared_ptr<Link>> links;
    for (const auto& pb : res.links()) {
        links.push_back(std::make_shared<Link>(pb, this));
    }
    return links;
}

void Client::deleteLink(const Kref& source_kref, const Kref& target_kref, const std::string& link_type) {
    ::kumiho::DeleteLinkRequest req;
    *req.mutable_source_kref() = source_kref.toPb();
    *req.mutable_target_kref() = target_kref.toPb();
    req.set_link_type(link_type);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->DeleteLink(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("DeleteLink failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

// --- Graph Traversal Operations ---

TraversalResult Client::traverseLinks(
    const Kref& origin_kref,
    int direction,
    const std::vector<std::string>& link_type_filter,
    int max_depth,
    int limit,
    bool include_path
) {
    ::kumiho::TraverseLinksRequest req;
    *req.mutable_origin_kref() = origin_kref.toPb();
    req.set_direction(static_cast<::kumiho::LinkDirection>(direction));
    for (const auto& lt : link_type_filter) {
        req.add_link_type_filter(lt);
    }
    req.set_max_depth(max_depth);
    req.set_limit(limit);
    req.set_include_path(include_path);

    ::kumiho::TraverseLinksResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->TraverseLinks(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("TraverseLinks failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    TraversalResult result;
    result.total_count = res.total_count();
    result.truncated = res.truncated();

    // Convert paths
    for (const auto& pb_path : res.paths()) {
        VersionPath path;
        path.total_depth = pb_path.total_depth();
        for (const auto& pb_step : pb_path.steps()) {
            PathStep step;
            step.version_kref = pb_step.version_kref().uri();
            step.link_type = pb_step.link_type();
            step.depth = pb_step.depth();
            path.steps.push_back(step);
        }
        result.paths.push_back(path);
    }

    // Convert version krefs
    for (const auto& pb_kref : res.version_krefs()) {
        result.version_krefs.push_back(pb_kref.uri());
    }

    // Convert links
    for (const auto& pb_link : res.links()) {
        result.links.push_back(std::make_shared<Link>(pb_link, this));
    }

    return result;
}

ShortestPathResult Client::findShortestPath(
    const Kref& source_kref,
    const Kref& target_kref,
    const std::vector<std::string>& link_type_filter,
    int max_depth,
    bool all_shortest
) {
    ::kumiho::ShortestPathRequest req;
    *req.mutable_source_kref() = source_kref.toPb();
    *req.mutable_target_kref() = target_kref.toPb();
    for (const auto& lt : link_type_filter) {
        req.add_link_type_filter(lt);
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
        VersionPath path;
        path.total_depth = pb_path.total_depth();
        for (const auto& pb_step : pb_path.steps()) {
            PathStep step;
            step.version_kref = pb_step.version_kref().uri();
            step.link_type = pb_step.link_type();
            step.depth = pb_step.depth();
            path.steps.push_back(step);
        }
        result.paths.push_back(path);
    }

    return result;
}

ImpactAnalysisResult Client::analyzeImpact(
    const Kref& version_kref,
    const std::vector<std::string>& link_type_filter,
    int max_depth,
    int limit
) {
    ::kumiho::ImpactAnalysisRequest req;
    *req.mutable_version_kref() = version_kref.toPb();
    for (const auto& lt : link_type_filter) {
        req.add_link_type_filter(lt);
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

    // Convert impacted versions
    for (const auto& pb_iv : res.impacted_versions()) {
        ImpactedVersion iv;
        iv.version_kref = pb_iv.version_kref().uri();
        iv.product_kref = pb_iv.product_kref().uri();
        iv.impact_depth = pb_iv.impact_depth();
        for (const auto& pt : pb_iv.impact_path_types()) {
            iv.impact_path_types.push_back(pt);
        }
        result.impacted_versions.push_back(iv);
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

// --- Collection Operations ---

std::shared_ptr<Collection> Client::createCollection(const std::string& parent_path, const std::string& name) {
    ::kumiho::CreateCollectionRequest req;
    req.set_parent_path(parent_path);
    req.set_collection_name(name);

    ::kumiho::ProductResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->CreateCollection(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("CreateCollection failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Collection>(res, this);
}

std::shared_ptr<Collection> Client::createCollection(const Kref& parent_kref, const std::string& name) {
    // Convert Kref to path (Kref format: kref://project/path/to/group)
    std::string path = "/" + parent_kref.getPath();
    return createCollection(path, name);
}

std::shared_ptr<Collection> Client::getCollection(const std::string& parent_path, const std::string& name) {
    // Collection is a product with type "collection"
    ::kumiho::GetProductRequest req;
    req.set_parent_path(parent_path);
    req.set_product_name(name);
    req.set_product_type("collection");

    ::kumiho::ProductResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetProduct(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            throw NotFoundError("Collection not found: " + parent_path + "/" + name + ".collection");
        }
        throw RpcError("GetProduct failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
    return std::make_shared<Collection>(res, this);
}

void Client::addCollectionMember(const Kref& collection_kref, const Kref& product_kref) {
    ::kumiho::AddCollectionMemberRequest req;
    *req.mutable_collection_kref() = collection_kref.toPb();
    *req.mutable_member_product_kref() = product_kref.toPb();

    ::kumiho::AddCollectionMemberResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->AddCollectionMember(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("AddCollectionMember failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

void Client::removeCollectionMember(const Kref& collection_kref, const Kref& product_kref) {
    ::kumiho::RemoveCollectionMemberRequest req;
    *req.mutable_collection_kref() = collection_kref.toPb();
    *req.mutable_member_product_kref() = product_kref.toPb();

    ::kumiho::RemoveCollectionMemberResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->RemoveCollectionMember(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("RemoveCollectionMember failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }
}

std::vector<CollectionMember> Client::getCollectionMembers(const Kref& collection_kref) {
    ::kumiho::GetCollectionMembersRequest req;
    *req.mutable_collection_kref() = collection_kref.toPb();

    ::kumiho::GetCollectionMembersResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetCollectionMembers(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetCollectionMembers failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<CollectionMember> members;
    for (const auto& pb : res.members()) {
        CollectionMember member;
        member.product_kref = Kref(pb.product_kref().uri());
        member.added_at = pb.added_at();
        member.added_by = pb.added_by();
        member.added_by_username = pb.added_by_username();
        member.added_in_version = pb.added_in_version();
        members.push_back(member);
    }
    return members;
}

std::vector<CollectionVersionHistory> Client::getCollectionHistory(const Kref& collection_kref) {
    ::kumiho::GetCollectionHistoryRequest req;
    *req.mutable_collection_kref() = collection_kref.toPb();

    ::kumiho::GetCollectionHistoryResponse res;
    grpc::ClientContext context; configureContext(context);
    grpc::Status status = stub_->GetCollectionHistory(&context, req, &res);

    if (!status.ok()) {
        throw RpcError("GetCollectionHistory failed: " + status.error_message(), static_cast<int>(status.error_code()));
    }

    std::vector<CollectionVersionHistory> history;
    for (const auto& pb : res.history()) {
        CollectionVersionHistory entry;
        entry.version_number = pb.version_number();
        entry.action = pb.action();
        if (pb.has_member_product_kref()) {
            entry.member_product_kref = Kref(pb.member_product_kref().uri());
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

std::shared_ptr<Group> createGroup(std::shared_ptr<Client> client, const std::string& path) {
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
    std::shared_ptr<Group> group;

    for (const auto& p : parts) {
        current_path += p;
        try {
            group = client->getGroup(current_path);
        } catch (const NotFoundError&) {
            // Group doesn't exist, create it
            std::string parent_path = current_path.substr(0, current_path.length() - p.length());
            if (parent_path.empty()) parent_path = "/";
            group = client->createGroup(parent_path, p);
        }
        current_path += "/";
    }

    return group;
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
