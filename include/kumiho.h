#ifndef KUMIHO_H
#define KUMIHO_H

#include <grpcpp/grpcpp.h>
#include "kumiho.grpc.pb.h"
#include <string>
#include <memory>
#include <map>
#include <vector>
#include <optional>

namespace kumiho {
namespace api {

class Client;
class Group;
class Product;
class Version;
class Resource;
class Link;
class Event;
class EventStream;

class Kref : public std::string {
public:
    explicit Kref(const std::string& uri = "");
    const std::string& uri() const { return *this; }
    std::string getPath() const;
    std::string getGroup() const;
    std::string getProductName() const;
    std::string getType() const;
    int getVersion() const;
    std::string getResourceName() const;
    ::kumiho::Kref toPb() const;
    bool operator==(const Kref& other) const { return static_cast<const std::string&>(*this) == static_cast<const std::string&>(other); }
    bool operator==(const std::string& other) const { return static_cast<const std::string&>(*this) == other; }

private:
    std::string path_, name_, type_;
    std::optional<int> version_;
    std::optional<std::string> resource_;
};

class Group {
public:
    Group(const ::kumiho::GroupResponse& response, Client* client);
    std::string getPath() const;
    api::Kref getKref() const;
    std::map<std::string, std::string> getMetadata() const;
    std::shared_ptr<Group> createGroup(const std::string& name);
    std::shared_ptr<Product> createProduct(const std::string& name, const std::string& ptype);
    std::shared_ptr<Product> getProduct(const std::string& name, const std::string& ptype);
    std::vector<std::shared_ptr<Product>> getProducts(const std::string& name_filter = "", const std::string& ptype_filter = "");
    std::shared_ptr<Group> setMetadata(const std::map<std::string, std::string>& metadata);
    void deleteGroup(bool force = false, const std::string& user_permission = "");
    void deleteGroup(bool force);  // Convenience overload
    std::shared_ptr<Group> getParentGroup();
    std::vector<std::shared_ptr<Group>> getChildGroups();

private:
    ::kumiho::GroupResponse response_;
    Client* client_;
};

class Product {
public:
    Product(const ::kumiho::ProductResponse& response, Client* client);
    api::Kref getKref() const;
    std::map<std::string, std::string> getMetadata() const;
    bool isDeprecated() const;
    std::shared_ptr<Version> createVersion(const std::map<std::string, std::string>& metadata = {});
    std::shared_ptr<Version> getVersion(int version_number);
    std::vector<std::shared_ptr<Version>> getVersions();
    std::shared_ptr<Version> getVersionByTag(const std::string& tag);
    std::shared_ptr<Version> getVersionByTime(const std::string& time);
    std::shared_ptr<Version> getLatestVersion();
    int peekNextVersion();
    std::shared_ptr<Product> setMetadata(const std::map<std::string, std::string>& metadata);
    void deleteProduct(bool force = false, const std::string& user_permission = "");
    void deleteProduct(bool force);  // Convenience overload
    std::shared_ptr<Group> getGroup();

private:
    ::kumiho::ProductResponse response_;
    Client* client_;
};

class Version {
public:
    Version(const ::kumiho::VersionResponse& response, Client* client);
    api::Kref getKref() const;
    api::Kref getProductKref() const;
    int getVersionNumber() const;
    std::vector<std::string> getTags() const;
    std::map<std::string, std::string> getMetadata() const;
    std::optional<std::string> getCreatedAt() const;
    std::string getAuthor() const;
    bool isDeprecated() const;
    bool isPublished() const;
    bool isLatest() const;
    std::string getUsername() const;
    std::optional<std::string> getDefaultResource() const;
    void setDefaultResource(const std::string& resource_name);
    std::shared_ptr<Resource> createResource(const std::string& name, const std::string& location);
    std::shared_ptr<Version> setMetadata(const std::map<std::string, std::string>& metadata);
    void deleteVersion(bool force = false, const std::string& user_permission = "");
    void deleteVersion(bool force);  // Convenience overload
    bool hasTag(const std::string& tag);
    void tag(const std::string& tag);
    void untag(const std::string& tag);
    bool wasTagged(const std::string& tag);
    std::shared_ptr<Resource> getResource(const std::string& name);
    std::vector<std::shared_ptr<Resource>> getResources();
    std::vector<std::string> getLocations();
    std::shared_ptr<Product> getProduct();
    std::shared_ptr<Group> getGroup();

private:
    ::kumiho::VersionResponse response_;
    Client* client_;
};

class Resource {
public:
    Resource(const ::kumiho::ResourceResponse& response, Client* client);
    api::Kref getKref() const;
    std::string getLocation() const;
    api::Kref getVersionKref() const;
    api::Kref getProductKref() const;
    std::map<std::string, std::string> getMetadata() const;
    std::shared_ptr<Resource> setMetadata(const std::map<std::string, std::string>& metadata);
    void deleteResource(bool force = false, const std::string& user_permission = "");
    void deleteResource(bool force);  // Convenience overload
private:
    ::kumiho::ResourceResponse response_;
    Client* client_;
};

class Link {
public:
    Link(const ::kumiho::Link& link, Client* client);
    api::Kref getSourceKref() const;
    api::Kref getTargetKref() const;
    std::string getLinkType() const;
    std::map<std::string, std::string> getMetadata() const;
    
private:
    ::kumiho::Link link_;
    Client* client_;
};

class Event {
public:
    Event(const ::kumiho::Event& event = ::kumiho::Event());
    std::string getRoutingKey() const;
    api::Kref getKref() const;
    std::map<std::string, std::string> getDetails() const;

private:
    ::kumiho::Event event_;
};

class EventStream {
public:
    EventStream(std::unique_ptr<grpc::ClientReaderInterface<::kumiho::Event>> reader);
    bool readNext(Event& event); 

private:
    std::unique_ptr<grpc::ClientReaderInterface<::kumiho::Event>> reader_;
};

class Client {
public:
    Client(std::shared_ptr<grpc::Channel> channel);
    Client(std::shared_ptr<kumiho::KumihoService::StubInterface> stub);

    // Factory method that uses environment variable
    static std::shared_ptr<Client> createFromEnv();

    // Group operations
    std::shared_ptr<Group> createGroup(const std::string& parent_path, const std::string& name);
    std::shared_ptr<Group> getGroup(const std::string& path);
    std::vector<std::shared_ptr<Group>> getChildGroups(const std::string& parent_path = "");
    
    // Product operations
    std::shared_ptr<Product> createProduct(const std::string& parent_path, const std::string& name, const std::string& ptype);
    std::shared_ptr<Product> getProduct(const std::string& parent_path, const std::string& name, const std::string& ptype);
    std::shared_ptr<Product> getProductByKref(const std::string& kref_uri);
    std::vector<std::shared_ptr<Product>> productSearch(const std::string& context_filter = "", const std::string& name_filter = "", const std::string& ptype_filter = "");
    
    // Version operations
    std::shared_ptr<Version> createVersion(const api::Kref& product_kref, const std::map<std::string, std::string>& metadata = {}, int number = 0);
    std::shared_ptr<Version> getVersion(const std::string& kref_uri);
    std::shared_ptr<Version> resolveKref(const std::string& kref_uri, const std::string& tag = "", const std::string& time = "");
    std::optional<std::string> resolve(const std::string& kref_uri);
    
    // Link operations
    std::shared_ptr<Link> createLink(const api::Kref& source_kref, const api::Kref& target_kref, const std::string& link_type, const std::map<std::string, std::string>& metadata = {});
    std::vector<std::shared_ptr<Link>> getLinks(const api::Kref& kref, const std::string& link_type_filter = "");

    // Resource operations
    std::vector<std::shared_ptr<Resource>> getResourcesByLocation(const std::string& location);

    // Event Streaming
    std::shared_ptr<EventStream> eventStream(const std::string& routing_key_filter = "", const std::string& kref_filter = "");

    // Make the raw stub available for other methods if needed
    kumiho::KumihoService::StubInterface* getStub() { return stub_.get(); }

private:
    std::shared_ptr<kumiho::KumihoService::StubInterface> stub_;
    std::shared_ptr<grpc::ClientContext> context_; // For event stream
};

} 
} 

// --- Convenience Functions ---

namespace kumiho {
namespace api {

/**
 * Creates nested groups from a path (e.g., "projectA/seqA/shot100").
 * Creates intermediate groups if they don't exist.
 * @param client The client to use for creating groups.
 * @param path The full path of groups to create.
 * @return A shared pointer to the final group in the path.
 */
std::shared_ptr<Group> createGroup(std::shared_ptr<Client> client, const std::string& path);

/**
 * Gets the current username from environment variables.
 * @return The current username, or "unknown" if not found.
 */
std::string getCurrentUser();

} 
} 

#endif
