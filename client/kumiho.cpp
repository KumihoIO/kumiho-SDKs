#include "kumiho.h"
#include <grpcpp/grpcpp.h>
#include <stdexcept>
#include <google/protobuf/util/time_util.h>
#include <regex>
#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <sstream>
#include <fstream>
#include <cctype>
#include <cstdlib>

/**
 * @file kumiho.cpp
 * @brief Implementation of the Kumiho Digital Asset Management API.
 *
 * This file contains the C++ implementations for all classes defined in kumiho.h.
 * It handles gRPC communication with the Kumiho server, error handling, and data conversion.
 *
 * Error Handling:
 * - All gRPC calls check the status and throw std::runtime_error on failure.
 * - Specific error codes (e.g., NOT_FOUND) are handled appropriately.
 * - Input validation is performed where necessary (e.g., time format).
 */

namespace kumiho {
namespace api {

// --- Kref Implementation ---
Kref::Kref(const std::string& uri) : std::string(uri) {}

/**
 * Extracts the path component from the Kref URI.
 * The path is the part after "kumiho://" and before any query parameters.
 */
std::string Kref::getPath() const {
    size_t start = find("://");
    if (start == std::string::npos) return *this;
    start += 3;
    size_t end = find('?', start);
    return substr(start, end - start);
}

/**
 * Extracts the resource name from the query parameter "r=".
 */
std::string Kref::getResourceName() const {
    size_t pos = find("&r=");
    if (pos != std::string::npos) {
        return substr(pos + 3);
    }
    return "";
}

/**
 * Extracts the group name from the URI path.
 */
std::string Kref::getGroup() const {
    std::string path = getPath();
    size_t pos = path.find('/');
    if (pos == std::string::npos) {
        return path;
    }
    return path.substr(0, pos);
}

/**
 * Extracts the product name (including type) from the URI path.
 */
std::string Kref::getProductName() const {
    std::string path = getPath();
    size_t pos = path.find('/');
    if (pos == std::string::npos) {
        return "";
    }
    return path.substr(pos + 1);
}

/**
 * Extracts the product type from the URI path.
 */
std::string Kref::getType() const {
    std::string product_name = getProductName();
    size_t pos = product_name.find('.');
    if (pos == std::string::npos) {
        return "";
    }
    return product_name.substr(pos + 1);
}

/**
 * Extracts the version number from the URI query string.
 */
int Kref::getVersion() const {
    size_t pos = find("?v=");
    if (pos != std::string::npos) {
        try {
            return std::stoi(substr(pos + 3));
        } catch (...) {
            return 1;
        }
    }
    return 1;
}

/**
 * Converts the Kref to its protobuf representation.
 */
::kumiho::Kref Kref::toPb() const {
    ::kumiho::Kref pb_kref;
    pb_kref.set_uri(*this);
    return pb_kref;
}

// --- Client Implementation ---

/**
 * Constructs a Client with a gRPC channel.
 * Creates the gRPC stub internally.
 */
Client::Client(std::shared_ptr<grpc::Channel> channel)
    : stub_(std::shared_ptr<kumiho::KumihoService::StubInterface>(::kumiho::KumihoService::NewStub(channel))) {}

/**
 * Constructs a Client with a pre-existing stub.
 * Useful for testing or advanced configurations.
 */
Client::Client(std::shared_ptr<kumiho::KumihoService::StubInterface> stub)
    : stub_(std::move(stub)) {}

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
        throw std::invalid_argument("Kumiho endpoint cannot be empty");
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
        throw std::invalid_argument("Invalid Kumiho endpoint: " + raw);
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
    std::transform(flag.begin(), flag.end(), flag.begin(), [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    return flag == "1" || flag == "true" || flag == "yes";
}

std::string ReadFileContents(const char* path) {
    if (path == nullptr || *path == '\0') {
        return {};
    }
    std::ifstream stream(path, std::ios::binary);
    if (!stream) {
        throw std::runtime_error(std::string("Failed to open CA bundle: ") + path);
    }
    std::stringstream buffer;
    buffer << stream.rdbuf();
    return buffer.str();
}

}  // namespace

/**
 * Creates a Client connected to the server endpoint defined by environment
 * variables. The lookup order is:
 *   1. KUMIHO_SERVER_ENDPOINT (preferred)
 *   2. KUMIHO_SERVER_ADDRESS (legacy)
 *   3. localhost:50051
 */
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
    return std::make_shared<Client>(channel);
}

/**
 * Creates a new group under the specified parent path.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Group> Client::createGroup(const std::string& parent_path, const std::string& name) {
    ::kumiho::CreateGroupRequest req;
    req.set_parent_path(parent_path);
    req.set_group_name(name);

    ::kumiho::GroupResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->CreateGroup(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Group>(res, this);
}

/**
 * Retrieves a group by its path or Kref.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Group> Client::getGroup(const std::string& path) {
    ::kumiho::GetGroupRequest req;
    req.set_path_or_kref(path);

    ::kumiho::GroupResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->GetGroup(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Group>(res, this);
}

/**
 * Retrieves child groups of a parent group.
 * If parent_path is empty, returns root-level groups.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::vector<std::shared_ptr<Group>> Client::getChildGroups(const std::string& parent_path) {
    ::kumiho::GetChildGroupsRequest req;
    req.set_parent_path(parent_path);

    ::kumiho::GetChildGroupsResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->GetChildGroups(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }

    std::vector<std::shared_ptr<Group>> groups;
    for (const auto& group_pb : res.groups()) {
        groups.push_back(std::make_shared<Group>(group_pb, this));
    }
    return groups;
}

/**
 * Searches for products with optional filters.
 * Returns all matching products.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::vector<std::shared_ptr<Product>> Client::productSearch(const std::string& context_filter, const std::string& name_filter, const std::string& ptype_filter) {
    ::kumiho::ProductSearchRequest req;
    req.set_context_filter(context_filter);
    req.set_product_name_filter(name_filter);
    req.set_product_type_filter(ptype_filter);

    ::kumiho::GetProductsResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->ProductSearch(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }

    std::vector<std::shared_ptr<Product>> products;
    for (const auto& prod_pb : res.products()) {
        products.push_back(std::make_shared<Product>(prod_pb, this));
    }
    return products;
}

/**
 * Creates a new product in the specified group.
 * @param parent_path The path of the parent group.
 * @param name The name of the product.
 * @param ptype The type of the product (e.g., "model", "texture").
 * @return A shared pointer to the created Product.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Product> Client::createProduct(const std::string& parent_path, const std::string& name, const std::string& ptype) {
    ::kumiho::CreateProductRequest req;
    req.set_parent_path(parent_path);
    req.set_product_name(name);
    req.set_product_type(ptype);

    ::kumiho::ProductResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->CreateProduct(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }

    return std::make_shared<Product>(res, this);
}

/**
 * Gets a product by its parent path, name, and type.
 * @param parent_path The path of the parent group.
 * @param name The name of the product.
 * @param ptype The type of the product.
 * @return A shared pointer to the Product.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Product> Client::getProduct(const std::string& parent_path, const std::string& name, const std::string& ptype) {
    ::kumiho::GetProductRequest req;
    req.set_parent_path(parent_path);
    req.set_product_name(name);
    req.set_product_type(ptype);

    ::kumiho::ProductResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->GetProduct(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }

    return std::make_shared<Product>(res, this);
}

/**
 * Gets a product by its kref URI.
 * Parses the kref to extract parent path, name, and type, then calls getProduct.
 * @param kref_uri The kref URI of the product.
 * @return A shared pointer to the Product.
 * @throws std::runtime_error if the kref format is invalid or gRPC call fails.
 */
std::shared_ptr<Product> Client::getProductByKref(const std::string& kref_uri) {
    api::Kref kref(kref_uri);
    std::string product_path = kref.getPath();
    
    size_t slash_pos = product_path.find('/');
    if (slash_pos == std::string::npos) {
        throw std::runtime_error("Invalid product kref format: " + kref_uri);
    }
    
    std::string group_path = product_path.substr(0, slash_pos);
    std::string product_name_type = product_path.substr(slash_pos + 1);
    
    size_t dot_pos = product_name_type.find('.');
    if (dot_pos == std::string::npos) {
        throw std::runtime_error("Invalid product name.type format: " + product_name_type);
    }
    
    std::string product_name = product_name_type.substr(0, dot_pos);
    std::string product_type = product_name_type.substr(dot_pos + 1);
    std::string parent_path = "/" + group_path;
    
    return getProduct(parent_path, product_name, product_type);
}

/**
 * Creates a new version for a product.
 * @param product_kref The kref of the product.
 * @param metadata Optional metadata for the version.
 * @param number Specific version number (0 for auto-increment).
 * @return A shared pointer to the created Version.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Version> Client::createVersion(const api::Kref& product_kref, const std::map<std::string, std::string>& metadata, int number) {
    ::kumiho::CreateVersionRequest req;
    *req.mutable_product_kref() = product_kref.toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }
    req.set_number(number);

    ::kumiho::VersionResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->CreateVersion(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }

    return std::make_shared<Version>(res, this);
}

/**
 * Gets a version by its kref URI, with optional tag/time resolution.
 * @param kref_uri The kref URI of the version. Can include ?t=tag or ?time=timestamp.
 * @return A shared pointer to the Version.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Version> Client::getVersion(const std::string& kref_uri) {
    // Parse kref_uri for tag/time parameters
    std::string base_kref = kref_uri;
    std::string tag;
    std::string time;
    
    size_t query_pos = kref_uri.find('?');
    if (query_pos != std::string::npos) {
        base_kref = kref_uri.substr(0, query_pos);
        std::string params = kref_uri.substr(query_pos + 1);
        
        size_t pos = 0;
        while ((pos = params.find('&')) != std::string::npos) {
            std::string param = params.substr(0, pos);
            if (param.substr(0, 2) == "t=") {
                tag = param.substr(2);
            } else if (param.substr(0, 5) == "time=") {
                time = param.substr(5);
            }
            params = params.substr(pos + 1);
        }
        // Handle last parameter
        if (params.substr(0, 2) == "t=") {
            tag = params.substr(2);
        } else if (params.substr(0, 5) == "time=") {
            time = params.substr(5);
        }
    }
    
    // If tag or time is specified, use resolve_kref
    if (!tag.empty() || !time.empty()) {
        auto resolved = resolveKref(base_kref, tag, time);
        if (!resolved) {
            throw std::runtime_error("Version not found");
        }
        // Use the resolved version
        return resolved;
    }
    
    ::kumiho::KrefRequest req;
    req.mutable_kref()->set_uri(kref_uri);
    
    ::kumiho::VersionResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->GetVersion(&context, req, &res);
    
    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    
    return std::make_shared<Version>(res, this);
}

/**
 * Resolves a Kref to a Version, optionally filtering by tag or time.
 * Validates time format if provided.
 * Returns nullptr if not found (NOT_FOUND status).
 * @throws std::invalid_argument if time format is invalid.
 * @throws std::runtime_error for other gRPC failures.
 */
std::shared_ptr<Version> Client::resolveKref(const std::string& kref_uri, const std::string& tag, const std::string& time) {
    if (!time.empty()) {
        // Validate time format: exactly 12 digits (YYYYMMDDHHMM)
        std::regex time_regex("^\\d{12}$");
        if (!std::regex_match(time, time_regex)) {
            throw std::invalid_argument("time must be in YYYYMMDDHHMM format");
        }
    }

    ::kumiho::ResolveKrefRequest req;
    req.set_kref(kref_uri);
    if (!tag.empty()) req.set_tag(tag);
    if (!time.empty()) req.set_time(time);

    ::kumiho::VersionResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->ResolveKref(&context, req, &res);

    if (!status.ok()) {
        if (status.error_code() == grpc::StatusCode::NOT_FOUND) {
            return nullptr;  // Version not found, return nullptr
        }
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Version>(res, this);
}

std::optional<std::string> Client::resolve(const std::string& kref_uri) {
    Kref kref(kref_uri);
    std::string path = kref.getPath();
    std::vector<std::string> parts;
    std::stringstream ss(path);
    std::string part;
    while (std::getline(ss, part, '/')) {
        parts.push_back(part);
    }

    if (parts.size() == 2 && kref.uri().find('.') != std::string::npos) {
        // Product KREF: group/product.type
        try {
            auto product = getProductByKref(kref_uri);
            auto latest_version = product->getLatestVersion();
            if (latest_version) {
                if (latest_version->getDefaultResource()) {
                    auto resource = latest_version->getResource(*latest_version->getDefaultResource());
                    return resource->getLocation();
                } else {
                    // Fallback: use first available resource
                    auto resources = latest_version->getResources();
                    if (!resources.empty()) {
                        return resources[0]->getLocation();
                    }
                }
            }
        } catch (const std::exception&) {
            return std::nullopt;
        }
    } else if (parts.size() == 2 && kref.uri().find('?') != std::string::npos) {
        // Version KREF: group/product.type?v=123
        try {
            auto version = getVersion(kref_uri);
            if (version) {
                if (version->getDefaultResource()) {
                    auto resource = version->getResource(*version->getDefaultResource());
                    return resource->getLocation();
                } else {
                    // Fallback: use first available resource
                    auto resources = version->getResources();
                    if (!resources.empty()) {
                        return resources[0]->getLocation();
                    }
                }
            }
        } catch (const std::exception&) {
            return std::nullopt;
        }
    } else if (parts.size() == 3) {
        // Resource KREF: group/product.type/resource_name?v=123
        try {
            std::string resource_name = parts[2];
            if (resource_name.find('?') != std::string::npos) {
                resource_name = resource_name.substr(0, resource_name.find('?'));
            }
            std::string version_kref_str = "kumiho://" + parts[0] + "/" + parts[1];
            if (kref.uri().find('?') != std::string::npos) {
                version_kref_str += kref.uri().substr(kref.uri().find('?'));
            }
            auto version = getVersion(version_kref_str);
            if (version) {
                auto resource = version->getResource(resource_name);
                return resource->getLocation();
            }
        } catch (const std::exception&) {
            return std::nullopt;
        }
    }

    return std::nullopt;

    return std::nullopt;
}

std::shared_ptr<Link> Client::createLink(const api::Kref& source_kref, const api::Kref& target_kref, const std::string& link_type, const std::map<std::string, std::string>& metadata) {
    ::kumiho::CreateLinkRequest req;
    *req.mutable_source_version_kref() = source_kref.toPb();
    *req.mutable_target_version_kref() = target_kref.toPb();
    req.set_link_type(link_type);
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::StatusResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->CreateLink(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    
    ::kumiho::Link link_pb;
    *link_pb.mutable_source_kref() = source_kref.toPb();
    *link_pb.mutable_target_kref() = target_kref.toPb();
    link_pb.set_link_type(link_type);
    for(const auto& pair : metadata) {
        (*link_pb.mutable_metadata())[pair.first] = pair.second;
    }

    return std::make_shared<Link>(link_pb, this);
}

std::vector<std::shared_ptr<Link>> Client::getLinks(const Kref& kref, const std::string& link_type_filter) {
    ::kumiho::GetLinksRequest req;
    *req.mutable_kref() = kref.toPb();
    req.set_link_type_filter(link_type_filter);

    ::kumiho::GetLinksResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->GetLinks(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }

    std::vector<std::shared_ptr<Link>> links;
    for (const auto& link_pb : res.links()) {
        links.push_back(std::make_shared<Link>(link_pb, this));
    }
    return links;
}

std::vector<std::shared_ptr<Resource>> Client::getResourcesByLocation(const std::string& location) {
    ::kumiho::GetResourcesByLocationRequest req;
    req.set_location(location);

    ::kumiho::GetResourcesByLocationResponse res;
    grpc::ClientContext context;
    grpc::Status status = stub_->GetResourcesByLocation(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }

    std::vector<std::shared_ptr<Resource>> resources;
    for (const auto& res_pb : res.resources()) {
        resources.push_back(std::make_shared<Resource>(res_pb, this));
    }
    return resources;
}

std::shared_ptr<EventStream> Client::eventStream(const std::string& routing_key_filter, const std::string& kref_filter) {
    ::kumiho::EventStreamRequest request;
    request.set_routing_key_filter(routing_key_filter);
    request.set_kref_filter(kref_filter);
    
    context_ = std::make_shared<grpc::ClientContext>();

    std::unique_ptr<grpc::ClientReaderInterface<::kumiho::Event>> reader = stub_->EventStream(context_.get(), request);
    return std::make_shared<EventStream>(std::move(reader));
}

// --- Group Implementation ---
Group::Group(const ::kumiho::GroupResponse& response, Client* client) : response_(response), client_(client) {}

std::string Group::getPath() const { return response_.path(); }
api::Kref Group::getKref() const { return api::Kref(response_.path()); }
std::map<std::string, std::string> Group::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::shared_ptr<Group> Group::createGroup(const std::string& name) {
    return client_->createGroup(response_.path(), name);
}

std::shared_ptr<Product> Group::createProduct(const std::string& name, const std::string& ptype) {
    ::kumiho::CreateProductRequest req;
    req.set_parent_path(response_.path());
    req.set_product_name(name);
    req.set_product_type(ptype);

    ::kumiho::ProductResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->CreateProduct(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Product>(res, client_);
}

std::shared_ptr<Product> Group::getProduct(const std::string& name, const std::string& ptype) {
    ::kumiho::GetProductRequest req;
    req.set_parent_path(response_.path());
    req.set_product_name(name);
    req.set_product_type(ptype);

    ::kumiho::ProductResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->GetProduct(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Product>(res, client_);
}

std::shared_ptr<Group> Group::setMetadata(const std::map<std::string, std::string>& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    req.mutable_kref()->set_uri(this->getPath());
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::GroupResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->UpdateGroupMetadata(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Group>(res, client_);
}

void Group::deleteGroup(bool force, const std::string& user_permission) {
    ::kumiho::DeleteGroupRequest req;
    req.set_path(response_.path());
    req.set_force(force);
    req.set_user_permission(user_permission);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->DeleteGroup(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
}

void Group::deleteGroup(bool force) {
    std::string user_permission = force ? api::getCurrentUser() : "";
    deleteGroup(force, user_permission);
}

/**
 * Gets the parent group of this group.
 * @return The parent Group object, or nullptr if this is a root group.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Group> Group::getParentGroup() {
    std::string path = response_.path();
    if (path == "/") {
        return nullptr;
    }
    
    // Split path and remove empty strings
    std::vector<std::string> parts;
    std::stringstream ss(path);
    std::string part;
    while (std::getline(ss, part, '/')) {
        if (!part.empty()) {
            parts.push_back(part);
        }
    }
    
    if (parts.size() <= 1) {
        return nullptr;  // This is a root-level group
    }
    
    // Remove the last component to get parent path
    parts.pop_back();
    
    std::string parent_path;
    if (parts.empty()) {
        parent_path = "/";
    } else {
        parent_path = "/";
        for (size_t i = 0; i < parts.size(); ++i) {
            if (i > 0) parent_path += "/";
            parent_path += parts[i];
        }
    }
    
    return client_->getGroup(parent_path);
}

/**
 * Gets the child groups of this group.
 * @return A vector of Group objects that are direct children of this group.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::vector<std::shared_ptr<Group>> Group::getChildGroups() {
    return client_->getChildGroups(response_.path());
}

// --- Product Implementation ---
Product::Product(const ::kumiho::ProductResponse& response, Client* client) : response_(response), client_(client) {}

Kref Product::getKref() const { return Kref(response_.kref().uri()); }
std::map<std::string, std::string> Product::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}
bool Product::isDeprecated() const { return response_.deprecated(); }

/**
 * Creates a new version for this product with optional metadata.
 * The version number is automatically assigned by the server.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Version> Product::createVersion(const std::map<std::string, std::string>& metadata) {
    ::kumiho::CreateVersionRequest req;
    *req.mutable_product_kref() = this->getKref().toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }

    ::kumiho::VersionResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->CreateVersion(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Version>(res, client_);
}

/**
 * Retrieves a specific version by its number.
 * Constructs the Kref URI with the version query parameter.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Version> Product::getVersion(int version_number) {
    ::kumiho::KrefRequest req;
    req.mutable_kref()->set_uri(getKref().uri() + "?v=" + std::to_string(version_number));
    
    ::kumiho::VersionResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->GetVersion(&context, req, &res);

    if(!status.ok()){
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Version>(res, client_);
}

/**
 * Retrieves a version by its tag.
 * Delegates to Client::resolveKref with the tag parameter.
 * Returns nullptr if no version with the tag is found.
 */
std::shared_ptr<Version> Product::getVersionByTag(const std::string& tag) {
    return client_->resolveKref(getKref().uri(), tag, "");
}

/**
 * Retrieves a version by its creation time.
 * Delegates to Client::resolveKref with the time parameter.
 * Time must be in YYYYMMDDHHMM format.
 * Returns nullptr if no version at that time is found.
 */
std::shared_ptr<Version> Product::getVersionByTime(const std::string& time) {
    return client_->resolveKref(getKref().uri(), "", time);
}

/**
 * Retrieves the latest version of this product.
 * Gets all versions and finds the one marked as latest, or the highest numbered version if none is marked as latest.
 * Returns nullptr if no versions exist.
 */
std::shared_ptr<Version> Product::getLatestVersion() {
    auto versions = getVersions();
    if (versions.empty()) {
        return nullptr;
    }
    
    // Find versions marked as latest
    std::vector<std::shared_ptr<Version>> latest_versions;
    for (const auto& version : versions) {
        if (version->isLatest()) {
            latest_versions.push_back(version);
        }
    }
    
    if (!latest_versions.empty()) {
        return latest_versions[0];
    }
    
    // Fallback to highest version number
    return *std::max_element(versions.begin(), versions.end(), 
        [](const std::shared_ptr<Version>& a, const std::shared_ptr<Version>& b) {
            return a->getVersionNumber() < b->getVersionNumber();
        });
}

/**
 * Retrieves all versions of this product.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::vector<std::shared_ptr<Version>> Product::getVersions() {
    ::kumiho::GetVersionsRequest req;
    *req.mutable_product_kref() = getKref().toPb();
    
    ::kumiho::GetVersionsResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->GetVersions(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    
    std::vector<std::shared_ptr<Version>> versions;
    for (const auto& ver_pb : res.versions()) {
        versions.push_back(std::make_shared<Version>(ver_pb, client_));
    }
    return versions;
}

/**
 * Peeks at the next version number that would be assigned.
 * Useful for planning or validation before creating a version.
 * @throws std::runtime_error if the gRPC call fails.
 */
int Product::peekNextVersion() {
    ::kumiho::PeekNextVersionRequest req;
    *req.mutable_product_kref() = getKref().toPb();
    
    ::kumiho::PeekNextVersionResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->PeekNextVersion(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return res.number();
}

/**
 * Updates the metadata for this product.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Product> Product::setMetadata(const std::map<std::string, std::string>& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    *req.mutable_kref() = getKref().toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }
    
    ::kumiho::ProductResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->UpdateProductMetadata(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Product>(res, client_);
}

void Product::deleteProduct(bool force, const std::string& user_permission) {
    ::kumiho::DeleteProductRequest req;
    *req.mutable_kref() = getKref().toPb();
    req.set_force(force);
    req.set_user_permission(user_permission);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->DeleteProduct(&context, req, &res);
    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
}

void Product::deleteProduct(bool force) {
    std::string user_permission = force ? api::getCurrentUser() : "";
    deleteProduct(force, user_permission);
}

/**
 * Gets the leaf group that contains this product.
 * @return The Group object that contains this product.
 * @throws std::runtime_error if the gRPC call fails.
 */
std::shared_ptr<Group> Product::getGroup() {
    std::string group_path = "/" + getKref().getGroup();
    return client_->getGroup(group_path);
}

// --- Version Implementation ---
Version::Version(const ::kumiho::VersionResponse& response, Client* client) : response_(response), client_(client) {}

Kref Version::getKref() const { return Kref(response_.kref().uri()); }
Kref Version::getProductKref() const { return Kref(response_.product_kref().uri()); }
int Version::getVersionNumber() const { return response_.number(); }
bool Version::isPublished() const { return response_.published(); }
bool Version::isLatest() const { return response_.latest(); }
std::map<std::string, std::string> Version::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}
std::vector<std::string> Version::getTags() const {
    return {response_.tags().begin(), response_.tags().end()};
}

std::optional<std::string> Version::getCreatedAt() const {
    // created_at is now a string field in RFC3339 format
    std::string created_at = response_.created_at();
    if (!created_at.empty()) {
        // Parse RFC3339 and convert to YYYYMMDDHHMM format
        // RFC3339 format: 2023-01-01T12:00:00Z
        // We need to extract date/time components and format as YYYYMMDDHHMM

        // Simple parsing - find positions of key characters
        size_t t_pos = created_at.find('T');
        if (t_pos != std::string::npos) {
            std::string date_part = created_at.substr(0, t_pos);  // YYYY-MM-DD
            std::string time_part = created_at.substr(t_pos + 1); // HH:MM:SSZ

            // Remove hyphens and colons, remove Z suffix
            date_part.erase(std::remove(date_part.begin(), date_part.end(), '-'), date_part.end());
            size_t z_pos = time_part.find('Z');
            if (z_pos != std::string::npos) {
                time_part = time_part.substr(0, z_pos);
            }
            time_part.erase(std::remove(time_part.begin(), time_part.end(), ':'), time_part.end());

            // Combine date and time (first 4 chars of time for HHMM)
            std::string result = date_part + time_part.substr(0, 4);
            return result;
        }
    }
    return std::nullopt;
}

std::string Version::getAuthor() const { return response_.author(); }
bool Version::isDeprecated() const { return response_.deprecated(); }
std::string Version::getUsername() const { return response_.username(); }

std::shared_ptr<Resource> Version::createResource(const std::string& name, const std::string& location) {
    ::kumiho::CreateResourceRequest req;
    *req.mutable_version_kref() = this->getKref().toPb();
    req.set_name(name);
    req.set_location(location);

    ::kumiho::ResourceResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->CreateResource(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Resource>(res, client_);
}

std::shared_ptr<Resource> Version::getResource(const std::string& name) {
    ::kumiho::GetResourceRequest req;
    *req.mutable_version_kref() = this->getKref().toPb();
    req.set_name(name);

    ::kumiho::ResourceResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->GetResource(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Resource>(res, client_);
}

std::vector<std::shared_ptr<Resource>> Version::getResources() {
    ::kumiho::GetResourcesRequest req;
    *req.mutable_version_kref() = getKref().toPb();

    ::kumiho::GetResourcesResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->GetResources(&context, req, &res);
    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }

    std::vector<std::shared_ptr<Resource>> resources;
    for (const auto& res_pb : res.resources()) {
        resources.push_back(std::make_shared<Resource>(res_pb, client_));
    }
    return resources;
}

std::vector<std::string> Version::getLocations() {
    auto resources = getResources();
    std::vector<std::string> locations;
    for (auto& res : resources) {
        locations.push_back(res->getLocation());
    }
    return locations;
}

std::optional<std::string> Version::getDefaultResource() const {
    std::string default_res = response_.default_resource();
    if (!default_res.empty()) {
        return default_res;
    }
    return std::nullopt;
}

void Version::setDefaultResource(const std::string& resource_name) {
    ::kumiho::SetDefaultResourceRequest req;
    *req.mutable_version_kref() = getKref().toPb();
    req.set_resource_name(resource_name);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->SetDefaultResource(&context, req, &res);
    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    // Update local response
    response_.set_default_resource(resource_name);
}

/**
 * Gets the parent product of this version.
 * @return A shared pointer to the Product.
 */
std::shared_ptr<Product> Version::getProduct() {
    return client_->getProductByKref(getProductKref().uri());
}

/**
 * Gets the leaf group that contains this version's product.
 * @return A shared pointer to the Group.
 */
std::shared_ptr<Group> Version::getGroup() {
    std::string group_path = "/" + getProductKref().getGroup();
    return client_->getGroup(group_path);
}

std::shared_ptr<Version> Version::setMetadata(const std::map<std::string, std::string>& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    *req.mutable_kref() = getKref().toPb();
     for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }
    
    ::kumiho::VersionResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->UpdateVersionMetadata(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Version>(res, client_);
}

void Version::tag(const std::string& tag) {
    ::kumiho::TagVersionRequest req;
    *req.mutable_kref() = getKref().toPb();
    req.set_tag(tag);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->TagVersion(&context, req, &res);
    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
}

void Version::untag(const std::string& tag) {
    ::kumiho::UnTagVersionRequest req;
    *req.mutable_kref() = getKref().toPb();
    req.set_tag(tag);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->UnTagVersion(&context, req, &res);
    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
}

bool Version::hasTag(const std::string& tag) {
    ::kumiho::HasTagRequest req;
    *req.mutable_kref() = getKref().toPb();
    req.set_tag(tag);
    
    ::kumiho::HasTagResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->HasTag(&context, req, &res);
    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return res.has_tag();
}

bool Version::wasTagged(const std::string& tag) {
    ::kumiho::WasTaggedRequest req;
    *req.mutable_kref() = getKref().toPb();
    req.set_tag(tag);

    ::kumiho::WasTaggedResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->WasTagged(&context, req, &res);
    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return res.was_tagged();
}

void Version::deleteVersion(bool force, const std::string& user_permission) {
    ::kumiho::DeleteVersionRequest req;
    *req.mutable_kref() = getKref().toPb();
    req.set_force(force);
    req.set_user_permission(user_permission);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->DeleteVersion(&context, req, &res);
    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
}

void Version::deleteVersion(bool force) {
    std::string user_permission = force ? api::getCurrentUser() : "";
    deleteVersion(force, user_permission);
}


// --- Resource Implementation ---
Resource::Resource(const ::kumiho::ResourceResponse& response, Client* client) : response_(response), client_(client) {}

Kref Resource::getKref() const { return Kref(response_.kref().uri()); }
std::string Resource::getLocation() const { return response_.location(); }
api::Kref Resource::getVersionKref() const { return api::Kref(response_.version_kref().uri()); }
api::Kref Resource::getProductKref() const { return api::Kref(response_.product_kref().uri()); }
std::map<std::string, std::string> Resource::getMetadata() const {
    return {response_.metadata().begin(), response_.metadata().end()};
}

std::shared_ptr<Resource> Resource::setMetadata(const std::map<std::string, std::string>& metadata) {
    ::kumiho::UpdateMetadataRequest req;
    *req.mutable_kref() = getKref().toPb();
    for (const auto& pair : metadata) {
        (*req.mutable_metadata())[pair.first] = pair.second;
    }
    
    ::kumiho::ResourceResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->UpdateResourceMetadata(&context, req, &res);

    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
    return std::make_shared<Resource>(res, client_);
}

void Resource::deleteResource(bool force, const std::string& user_permission) {
    ::kumiho::DeleteResourceRequest req;
    *req.mutable_kref() = getKref().toPb();
    req.set_force(force);
    req.set_user_permission(user_permission);

    ::kumiho::StatusResponse res;
    grpc::ClientContext context;
    grpc::Status status = client_->getStub()->DeleteResource(&context, req, &res);
    if (!status.ok()) {
        throw std::runtime_error("RPC failed: " + status.error_message());
    }
}

void Resource::deleteResource(bool force) {
    std::string user_permission = force ? api::getCurrentUser() : "";
    deleteResource(force, user_permission);
}


// --- Link Implementation ---
Link::Link(const ::kumiho::Link& link, Client* client) : link_(link), client_(client) {}

Kref Link::getSourceKref() const { return Kref(link_.source_kref().uri()); }
Kref Link::getTargetKref() const { return Kref(link_.target_kref().uri()); }
std::string Link::getLinkType() const { return link_.link_type(); }
std::map<std::string, std::string> Link::getMetadata() const {
    return {link_.metadata().begin(), link_.metadata().end()};
}

// --- Event Implementation ---
Event::Event(const ::kumiho::Event& event) : event_(event) {}

std::string Event::getRoutingKey() const { return event_.routing_key(); }
Kref Event::getKref() const { return Kref(event_.kref().uri()); }
std::map<std::string, std::string> Event::getDetails() const {
    return {event_.details().begin(), event_.details().end()};
}


// --- EventStream Implementation ---
EventStream::EventStream(std::unique_ptr<grpc::ClientReaderInterface<::kumiho::Event>> reader)
    : reader_(std::move(reader)) {}

bool EventStream::readNext(Event& event) {
    ::kumiho::Event event_pb;
    if (reader_->Read(&event_pb)) {
        event = Event(event_pb);
        return true;
    }
    return false;
}

// --- Convenience Functions ---

/**
 * Creates nested groups from a path (e.g., "projectA/seqA/shot100").
 * Creates intermediate groups if they don't exist.
 */
std::shared_ptr<Group> api::createGroup(std::shared_ptr<Client> client, const std::string& path) {
    std::vector<std::string> parts;
    std::stringstream ss(path);
    std::string part;
    
    while (std::getline(ss, part, '/')) {
        if (!part.empty()) {
            parts.push_back(part);
        }
    }
    
    if (parts.empty()) {
        throw std::invalid_argument("Invalid path: " + path);
    }
    
    std::string current_path = "/";
    std::shared_ptr<Group> group;
    
    for (const auto& part : parts) {
        current_path += part;
        try {
            group = client->getGroup(current_path);
        } catch (const std::runtime_error&) {
            // Group doesn't exist, create it
            std::string parent_path = current_path.substr(0, current_path.length() - part.length());
            if (parent_path.empty()) parent_path = "/";
            group = client->createGroup(parent_path, part);
        }
        current_path += "/";
    }
    
    return group;
}

/**
 * Gets the current username from environment variables.
 */
std::string api::getCurrentUser() {
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
#endif
    return "unknown";
}

} 
}
