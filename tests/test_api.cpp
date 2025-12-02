#include <grpcpp/grpcpp.h>
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <kumiho/kumiho.hpp>
#include <kumiho.pb.h>
#include <kumiho.grpc.pb.h>
#include <memory>
#include <chrono>
#include <thread>
#include <string>
#include <cstdlib> // For getenv

using ::testing::_;
using ::testing::Return;
using ::testing::SetArgPointee;
using ::testing::DoAll;

// --- Constants ---
const std::string ADMIN_USER = "kaveone";
const std::string PUBLISHED_TAG = "published";

// --- Helper Functions ---
std::string unique_name(const std::string& prefix) {
    auto now = std::chrono::high_resolution_clock::now();
    auto nanos = std::chrono::duration_cast<std::chrono::nanoseconds>(now.time_since_epoch()).count();
    return prefix + "_" + std::to_string(nanos);
}

// --- Mock Stub for Unit Tests ---
class MockKumihoStub : public kumiho::KumihoService::StubInterface {
public:
    // Project methods
    MOCK_METHOD(grpc::Status, CreateProject, (grpc::ClientContext* context, const kumiho::CreateProjectRequest& request, kumiho::ProjectResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetProjects, (grpc::ClientContext* context, const kumiho::GetProjectsRequest& request, kumiho::GetProjectsResponse* response), (override));
    MOCK_METHOD(grpc::Status, UpdateProject, (grpc::ClientContext* context, const kumiho::UpdateProjectRequest& request, kumiho::ProjectResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteProject, (grpc::ClientContext* context, const kumiho::DeleteProjectRequest& request, kumiho::StatusResponse* response), (override));

    // Group methods
    MOCK_METHOD(grpc::Status, CreateGroup, (grpc::ClientContext* context, const kumiho::CreateGroupRequest& request, kumiho::GroupResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetGroup, (grpc::ClientContext* context, const kumiho::GetGroupRequest& request, kumiho::GroupResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetChildGroups, (grpc::ClientContext* context, const kumiho::GetChildGroupsRequest& request, kumiho::GetChildGroupsResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteGroup, (grpc::ClientContext* context, const kumiho::DeleteGroupRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, UpdateGroupMetadata, (grpc::ClientContext* context, const kumiho::UpdateMetadataRequest& request, kumiho::GroupResponse* response), (override));

    // Product methods
    MOCK_METHOD(grpc::Status, CreateProduct, (grpc::ClientContext* context, const kumiho::CreateProductRequest& request, kumiho::ProductResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetProduct, (grpc::ClientContext* context, const kumiho::GetProductRequest& request, kumiho::ProductResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetProducts, (grpc::ClientContext* context, const kumiho::GetProductsRequest& request, kumiho::GetProductsResponse* response), (override));
    MOCK_METHOD(grpc::Status, ProductSearch, (grpc::ClientContext* context, const kumiho::ProductSearchRequest& request, kumiho::GetProductsResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteProduct, (grpc::ClientContext* context, const kumiho::DeleteProductRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, UpdateProductMetadata, (grpc::ClientContext* context, const kumiho::UpdateMetadataRequest& request, kumiho::ProductResponse* response), (override));

    // Version methods
    MOCK_METHOD(grpc::Status, ResolveKref, (grpc::ClientContext* context, const kumiho::ResolveKrefRequest& request, kumiho::VersionResponse* response), (override));
    MOCK_METHOD(grpc::Status, ResolveLocation, (grpc::ClientContext* context, const kumiho::ResolveLocationRequest& request, kumiho::ResolveLocationResponse* response), (override));
    MOCK_METHOD(grpc::Status, CreateVersion, (grpc::ClientContext* context, const kumiho::CreateVersionRequest& request, kumiho::VersionResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetVersion, (grpc::ClientContext* context, const kumiho::KrefRequest& request, kumiho::VersionResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetVersions, (grpc::ClientContext* context, const kumiho::GetVersionsRequest& request, kumiho::GetVersionsResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteVersion, (grpc::ClientContext* context, const kumiho::DeleteVersionRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, PeekNextVersion, (grpc::ClientContext* context, const kumiho::PeekNextVersionRequest& request, kumiho::PeekNextVersionResponse* response), (override));
    MOCK_METHOD(grpc::Status, UpdateVersionMetadata, (grpc::ClientContext* context, const kumiho::UpdateMetadataRequest& request, kumiho::VersionResponse* response), (override));
    MOCK_METHOD(grpc::Status, TagVersion, (grpc::ClientContext* context, const kumiho::TagVersionRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, UnTagVersion, (grpc::ClientContext* context, const kumiho::UnTagVersionRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, HasTag, (grpc::ClientContext* context, const kumiho::HasTagRequest& request, kumiho::HasTagResponse* response), (override));
    MOCK_METHOD(grpc::Status, WasTagged, (grpc::ClientContext* context, const kumiho::WasTaggedRequest& request, kumiho::WasTaggedResponse* response), (override));
    MOCK_METHOD(grpc::Status, SetDefaultResource, (grpc::ClientContext* context, const kumiho::SetDefaultResourceRequest& request, kumiho::StatusResponse* response), (override));

    // Resource methods
    MOCK_METHOD(grpc::Status, CreateResource, (grpc::ClientContext* context, const kumiho::CreateResourceRequest& request, kumiho::ResourceResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetResource, (grpc::ClientContext* context, const kumiho::GetResourceRequest& request, kumiho::ResourceResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetResources, (grpc::ClientContext* context, const kumiho::GetResourcesRequest& request, kumiho::GetResourcesResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetResourcesByLocation, (grpc::ClientContext* context, const kumiho::GetResourcesByLocationRequest& request, kumiho::GetResourcesByLocationResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteResource, (grpc::ClientContext* context, const kumiho::DeleteResourceRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, UpdateResourceMetadata, (grpc::ClientContext* context, const kumiho::UpdateMetadataRequest& request, kumiho::ResourceResponse* response), (override));

    // Attribute methods
    MOCK_METHOD(grpc::Status, SetAttribute, (grpc::ClientContext* context, const kumiho::SetAttributeRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetAttribute, (grpc::ClientContext* context, const kumiho::GetAttributeRequest& request, kumiho::GetAttributeResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteAttribute, (grpc::ClientContext* context, const kumiho::DeleteAttributeRequest& request, kumiho::StatusResponse* response), (override));

    // Link methods
    MOCK_METHOD(grpc::Status, CreateLink, (grpc::ClientContext* context, const kumiho::CreateLinkRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetLinks, (grpc::ClientContext* context, const kumiho::GetLinksRequest& request, kumiho::GetLinksResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteLink, (grpc::ClientContext* context, const kumiho::DeleteLinkRequest& request, kumiho::StatusResponse* response), (override));

    // Graph traversal methods
    MOCK_METHOD(grpc::Status, TraverseLinks, (grpc::ClientContext* context, const kumiho::TraverseLinksRequest& request, kumiho::TraverseLinksResponse* response), (override));
    MOCK_METHOD(grpc::Status, FindShortestPath, (grpc::ClientContext* context, const kumiho::ShortestPathRequest& request, kumiho::ShortestPathResponse* response), (override));
    MOCK_METHOD(grpc::Status, AnalyzeImpact, (grpc::ClientContext* context, const kumiho::ImpactAnalysisRequest& request, kumiho::ImpactAnalysisResponse* response), (override));

    // Collection methods
    MOCK_METHOD(grpc::Status, CreateCollection, (grpc::ClientContext* context, const kumiho::CreateCollectionRequest& request, kumiho::ProductResponse* response), (override));
    MOCK_METHOD(grpc::Status, AddCollectionMember, (grpc::ClientContext* context, const kumiho::AddCollectionMemberRequest& request, kumiho::AddCollectionMemberResponse* response), (override));
    MOCK_METHOD(grpc::Status, RemoveCollectionMember, (grpc::ClientContext* context, const kumiho::RemoveCollectionMemberRequest& request, kumiho::RemoveCollectionMemberResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetCollectionMembers, (grpc::ClientContext* context, const kumiho::GetCollectionMembersRequest& request, kumiho::GetCollectionMembersResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetCollectionHistory, (grpc::ClientContext* context, const kumiho::GetCollectionHistoryRequest& request, kumiho::GetCollectionHistoryResponse* response), (override));

    // Tenant methods
    MOCK_METHOD(grpc::Status, GetTenantUsage, (grpc::ClientContext* context, const kumiho::GetTenantUsageRequest& request, kumiho::TenantUsageResponse* response), (override));

    // Deprecation methods
    MOCK_METHOD(grpc::Status, SetDeprecated, (grpc::ClientContext* context, const kumiho::SetDeprecatedRequest& request, kumiho::StatusResponse* response), (override));

    // Mock streaming methods
    MOCK_METHOD(grpc::ClientReaderInterface<kumiho::Event>*, EventStreamRaw, (grpc::ClientContext* context, const kumiho::EventStreamRequest& request), (override));
    
    // Boilerplate for async methods that we don't use in tests
    // Project async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProjectResponse>* AsyncCreateProjectRaw(grpc::ClientContext*, const kumiho::CreateProjectRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProjectResponse>* PrepareAsyncCreateProjectRaw(grpc::ClientContext*, const kumiho::CreateProjectRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetProjectsResponse>* AsyncGetProjectsRaw(grpc::ClientContext*, const kumiho::GetProjectsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetProjectsResponse>* PrepareAsyncGetProjectsRaw(grpc::ClientContext*, const kumiho::GetProjectsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProjectResponse>* AsyncUpdateProjectRaw(grpc::ClientContext*, const kumiho::UpdateProjectRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProjectResponse>* PrepareAsyncUpdateProjectRaw(grpc::ClientContext*, const kumiho::UpdateProjectRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteProjectRaw(grpc::ClientContext*, const kumiho::DeleteProjectRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteProjectRaw(grpc::ClientContext*, const kumiho::DeleteProjectRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Group async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::GroupResponse>* AsyncCreateGroupRaw(grpc::ClientContext*, const kumiho::CreateGroupRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GroupResponse>* PrepareAsyncCreateGroupRaw(grpc::ClientContext*, const kumiho::CreateGroupRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GroupResponse>* AsyncGetGroupRaw(grpc::ClientContext*, const kumiho::GetGroupRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GroupResponse>* PrepareAsyncGetGroupRaw(grpc::ClientContext*, const kumiho::GetGroupRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetChildGroupsResponse>* AsyncGetChildGroupsRaw(grpc::ClientContext*, const kumiho::GetChildGroupsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetChildGroupsResponse>* PrepareAsyncGetChildGroupsRaw(grpc::ClientContext*, const kumiho::GetChildGroupsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteGroupRaw(grpc::ClientContext*, const kumiho::DeleteGroupRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteGroupRaw(grpc::ClientContext*, const kumiho::DeleteGroupRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GroupResponse>* AsyncUpdateGroupMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GroupResponse>* PrepareAsyncUpdateGroupMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Product async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProductResponse>* AsyncCreateProductRaw(grpc::ClientContext*, const kumiho::CreateProductRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProductResponse>* PrepareAsyncCreateProductRaw(grpc::ClientContext*, const kumiho::CreateProductRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProductResponse>* AsyncGetProductRaw(grpc::ClientContext*, const kumiho::GetProductRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProductResponse>* PrepareAsyncGetProductRaw(grpc::ClientContext*, const kumiho::GetProductRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetProductsResponse>* AsyncGetProductsRaw(grpc::ClientContext*, const kumiho::GetProductsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetProductsResponse>* PrepareAsyncGetProductsRaw(grpc::ClientContext*, const kumiho::GetProductsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetProductsResponse>* AsyncProductSearchRaw(grpc::ClientContext*, const kumiho::ProductSearchRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetProductsResponse>* PrepareAsyncProductSearchRaw(grpc::ClientContext*, const kumiho::ProductSearchRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteProductRaw(grpc::ClientContext*, const kumiho::DeleteProductRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteProductRaw(grpc::ClientContext*, const kumiho::DeleteProductRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProductResponse>* AsyncUpdateProductMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProductResponse>* PrepareAsyncUpdateProductMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Version async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::VersionResponse>* AsyncResolveKrefRaw(grpc::ClientContext*, const kumiho::ResolveKrefRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::VersionResponse>* PrepareAsyncResolveKrefRaw(grpc::ClientContext*, const kumiho::ResolveKrefRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ResolveLocationResponse>* AsyncResolveLocationRaw(grpc::ClientContext*, const kumiho::ResolveLocationRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ResolveLocationResponse>* PrepareAsyncResolveLocationRaw(grpc::ClientContext*, const kumiho::ResolveLocationRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::VersionResponse>* AsyncCreateVersionRaw(grpc::ClientContext*, const kumiho::CreateVersionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::VersionResponse>* PrepareAsyncCreateVersionRaw(grpc::ClientContext*, const kumiho::CreateVersionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::VersionResponse>* AsyncGetVersionRaw(grpc::ClientContext*, const kumiho::KrefRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::VersionResponse>* PrepareAsyncGetVersionRaw(grpc::ClientContext*, const kumiho::KrefRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetVersionsResponse>* AsyncGetVersionsRaw(grpc::ClientContext*, const kumiho::GetVersionsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetVersionsResponse>* PrepareAsyncGetVersionsRaw(grpc::ClientContext*, const kumiho::GetVersionsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteVersionRaw(grpc::ClientContext*, const kumiho::DeleteVersionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteVersionRaw(grpc::ClientContext*, const kumiho::DeleteVersionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::PeekNextVersionResponse>* AsyncPeekNextVersionRaw(grpc::ClientContext*, const kumiho::PeekNextVersionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::PeekNextVersionResponse>* PrepareAsyncPeekNextVersionRaw(grpc::ClientContext*, const kumiho::PeekNextVersionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::VersionResponse>* AsyncUpdateVersionMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::VersionResponse>* PrepareAsyncUpdateVersionMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncTagVersionRaw(grpc::ClientContext*, const kumiho::TagVersionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncTagVersionRaw(grpc::ClientContext*, const kumiho::TagVersionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncUnTagVersionRaw(grpc::ClientContext*, const kumiho::UnTagVersionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncUnTagVersionRaw(grpc::ClientContext*, const kumiho::UnTagVersionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::HasTagResponse>* AsyncHasTagRaw(grpc::ClientContext*, const kumiho::HasTagRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::HasTagResponse>* PrepareAsyncHasTagRaw(grpc::ClientContext*, const kumiho::HasTagRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::WasTaggedResponse>* AsyncWasTaggedRaw(grpc::ClientContext*, const kumiho::WasTaggedRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::WasTaggedResponse>* PrepareAsyncWasTaggedRaw(grpc::ClientContext*, const kumiho::WasTaggedRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncSetDefaultResourceRaw(grpc::ClientContext*, const kumiho::SetDefaultResourceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncSetDefaultResourceRaw(grpc::ClientContext*, const kumiho::SetDefaultResourceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Resource async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::ResourceResponse>* AsyncCreateResourceRaw(grpc::ClientContext*, const kumiho::CreateResourceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ResourceResponse>* PrepareAsyncCreateResourceRaw(grpc::ClientContext*, const kumiho::CreateResourceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ResourceResponse>* AsyncGetResourceRaw(grpc::ClientContext*, const kumiho::GetResourceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ResourceResponse>* PrepareAsyncGetResourceRaw(grpc::ClientContext*, const kumiho::GetResourceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetResourcesResponse>* AsyncGetResourcesRaw(grpc::ClientContext*, const kumiho::GetResourcesRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetResourcesResponse>* PrepareAsyncGetResourcesRaw(grpc::ClientContext*, const kumiho::GetResourcesRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetResourcesByLocationResponse>* AsyncGetResourcesByLocationRaw(grpc::ClientContext*, const kumiho::GetResourcesByLocationRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetResourcesByLocationResponse>* PrepareAsyncGetResourcesByLocationRaw(grpc::ClientContext*, const kumiho::GetResourcesByLocationRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteResourceRaw(grpc::ClientContext*, const kumiho::DeleteResourceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteResourceRaw(grpc::ClientContext*, const kumiho::DeleteResourceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ResourceResponse>* AsyncUpdateResourceMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ResourceResponse>* PrepareAsyncUpdateResourceMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Attribute async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncSetAttributeRaw(grpc::ClientContext*, const kumiho::SetAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncSetAttributeRaw(grpc::ClientContext*, const kumiho::SetAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetAttributeResponse>* AsyncGetAttributeRaw(grpc::ClientContext*, const kumiho::GetAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetAttributeResponse>* PrepareAsyncGetAttributeRaw(grpc::ClientContext*, const kumiho::GetAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteAttributeRaw(grpc::ClientContext*, const kumiho::DeleteAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteAttributeRaw(grpc::ClientContext*, const kumiho::DeleteAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Link async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncCreateLinkRaw(grpc::ClientContext*, const kumiho::CreateLinkRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncCreateLinkRaw(grpc::ClientContext*, const kumiho::CreateLinkRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetLinksResponse>* AsyncGetLinksRaw(grpc::ClientContext*, const kumiho::GetLinksRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetLinksResponse>* PrepareAsyncGetLinksRaw(grpc::ClientContext*, const kumiho::GetLinksRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteLinkRaw(grpc::ClientContext*, const kumiho::DeleteLinkRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteLinkRaw(grpc::ClientContext*, const kumiho::DeleteLinkRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Graph traversal async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::TraverseLinksResponse>* AsyncTraverseLinksRaw(grpc::ClientContext*, const kumiho::TraverseLinksRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::TraverseLinksResponse>* PrepareAsyncTraverseLinksRaw(grpc::ClientContext*, const kumiho::TraverseLinksRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ShortestPathResponse>* AsyncFindShortestPathRaw(grpc::ClientContext*, const kumiho::ShortestPathRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ShortestPathResponse>* PrepareAsyncFindShortestPathRaw(grpc::ClientContext*, const kumiho::ShortestPathRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ImpactAnalysisResponse>* AsyncAnalyzeImpactRaw(grpc::ClientContext*, const kumiho::ImpactAnalysisRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ImpactAnalysisResponse>* PrepareAsyncAnalyzeImpactRaw(grpc::ClientContext*, const kumiho::ImpactAnalysisRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Collection async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProductResponse>* AsyncCreateCollectionRaw(grpc::ClientContext*, const kumiho::CreateCollectionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ProductResponse>* PrepareAsyncCreateCollectionRaw(grpc::ClientContext*, const kumiho::CreateCollectionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::AddCollectionMemberResponse>* AsyncAddCollectionMemberRaw(grpc::ClientContext*, const kumiho::AddCollectionMemberRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::AddCollectionMemberResponse>* PrepareAsyncAddCollectionMemberRaw(grpc::ClientContext*, const kumiho::AddCollectionMemberRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RemoveCollectionMemberResponse>* AsyncRemoveCollectionMemberRaw(grpc::ClientContext*, const kumiho::RemoveCollectionMemberRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RemoveCollectionMemberResponse>* PrepareAsyncRemoveCollectionMemberRaw(grpc::ClientContext*, const kumiho::RemoveCollectionMemberRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetCollectionMembersResponse>* AsyncGetCollectionMembersRaw(grpc::ClientContext*, const kumiho::GetCollectionMembersRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetCollectionMembersResponse>* PrepareAsyncGetCollectionMembersRaw(grpc::ClientContext*, const kumiho::GetCollectionMembersRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetCollectionHistoryResponse>* AsyncGetCollectionHistoryRaw(grpc::ClientContext*, const kumiho::GetCollectionHistoryRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetCollectionHistoryResponse>* PrepareAsyncGetCollectionHistoryRaw(grpc::ClientContext*, const kumiho::GetCollectionHistoryRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Tenant async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::TenantUsageResponse>* AsyncGetTenantUsageRaw(grpc::ClientContext*, const kumiho::GetTenantUsageRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::TenantUsageResponse>* PrepareAsyncGetTenantUsageRaw(grpc::ClientContext*, const kumiho::GetTenantUsageRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Deprecation async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncSetDeprecatedRaw(grpc::ClientContext*, const kumiho::SetDeprecatedRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncSetDeprecatedRaw(grpc::ClientContext*, const kumiho::SetDeprecatedRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Event streaming async methods
    grpc::ClientAsyncReaderInterface<kumiho::Event>* AsyncEventStreamRaw(grpc::ClientContext*, const kumiho::EventStreamRequest&, grpc::CompletionQueue*, void*) override { return nullptr; }
    grpc::ClientAsyncReaderInterface<kumiho::Event>* PrepareAsyncEventStreamRaw(grpc::ClientContext*, const kumiho::EventStreamRequest&, grpc::CompletionQueue*) override { return nullptr; }
};


// --- Unit Test Fixture ---
class KumihoUnitTest : public ::testing::Test {
protected:
    void SetUp() override {
        auto mock_stub_ptr = std::make_unique<MockKumihoStub>();
        mock_stub = mock_stub_ptr.get(); // Get raw pointer before moving ownership
        client = std::make_unique<kumiho::api::Client>(std::move(mock_stub_ptr));
    }

    std::unique_ptr<kumiho::api::Client> client;
    MockKumihoStub* mock_stub;
};

// --- Unit Tests ---
TEST_F(KumihoUnitTest, CreateGroup) {
    kumiho::GroupResponse fake_response;
    fake_response.set_path("/projectA/seqA");
    EXPECT_CALL(*mock_stub, CreateGroup(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(fake_response), Return(grpc::Status::OK)));

    auto group = client->createGroup("/projectA", "seqA");
    ASSERT_NE(group, nullptr);
    EXPECT_EQ(group->getPath(), "/projectA/seqA");
}

TEST_F(KumihoUnitTest, GetGroupFromPath) {
    kumiho::GroupResponse fake_response;
    fake_response.set_path("/projectA/seqA");
    EXPECT_CALL(*mock_stub, GetGroup(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(fake_response), Return(grpc::Status::OK)));
    
    auto group = client->getGroup("projectA/seqA");
    ASSERT_NE(group, nullptr);
    EXPECT_EQ(group->getPath(), "/projectA/seqA");
}

TEST_F(KumihoUnitTest, ProductSearchWithContext) {
    kumiho::GetProductsResponse fake_response;
    auto* product_res = fake_response.add_products();
    product_res->mutable_kref()->set_uri("kref://projectA/seqA/001/kumiho.model");

    EXPECT_CALL(*mock_stub, ProductSearch(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(fake_response), Return(grpc::Status::OK)));

    auto results = client->productSearch("projectA/seqA", "", "model");
    ASSERT_EQ(results.size(), 1);
    EXPECT_EQ(results[0]->getKref().uri(), "kref://projectA/seqA/001/kumiho.model");
}

TEST_F(KumihoUnitTest, ResolveKrefWithTime) {
    kumiho::VersionResponse fake_response;
    fake_response.mutable_kref()->set_uri("kref://obj1?v=2");
    fake_response.set_number(2);

    EXPECT_CALL(*mock_stub, ResolveKref(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(fake_response), Return(grpc::Status::OK)));
    
    auto resolved = client->resolveKref("kref://obj1", "", "202510131200");
    ASSERT_NE(resolved, nullptr);
    EXPECT_EQ(resolved->getVersionNumber(), 2);
}

TEST_F(KumihoUnitTest, ResolveKrefWithTagAndTime) {
    kumiho::VersionResponse fake_response;
    fake_response.mutable_kref()->set_uri("kref://obj1?v=1");
    fake_response.set_number(1);

    EXPECT_CALL(*mock_stub, ResolveKref(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(fake_response), Return(grpc::Status::OK)));

    auto resolved = client->resolveKref("kref://obj1", "published", "202510101000");
    ASSERT_NE(resolved, nullptr);
    EXPECT_EQ(resolved->getVersionNumber(), 1);
}

TEST_F(KumihoUnitTest, ResolveKrefInvalidTimeFormat) {
    EXPECT_THROW(client->resolveKref("kref://some_id", "", "2025-10-13 12:00:00"), std::invalid_argument);
}

TEST_F(KumihoUnitTest, ResolveProductKrefFallbackToFirstResource) {
    // Setup: Product KREF, no default_resource, but one resource exists
    kumiho::ProductResponse product_response;
    product_response.mutable_kref()->set_uri("kref://group1/prod1.type");
    EXPECT_CALL(*mock_stub, GetProduct(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(product_response), Return(grpc::Status::OK)));

    kumiho::VersionResponse version_response;
    version_response.mutable_kref()->set_uri("kref://group1/prod1.type?v=1");
    version_response.set_number(1);
    // No default_resource set
    kumiho::GetVersionsResponse versions_response;
    auto* v = versions_response.add_versions();
    *v = version_response;
    EXPECT_CALL(*mock_stub, GetVersions(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(versions_response), Return(grpc::Status::OK)));

    kumiho::ResourceResponse resource_response;
    resource_response.set_location("/path/to/resource1");
    kumiho::GetResourcesResponse resources_response;
    auto* r = resources_response.add_resources();
    *r = resource_response;
    EXPECT_CALL(*mock_stub, GetResources(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(resources_response), Return(grpc::Status::OK)));

    auto location = client->resolve("kref://group1/prod1.type");
    ASSERT_TRUE(location.has_value());
    EXPECT_EQ(location.value(), "/path/to/resource1");
}

// --- Integration Test Fixture ---
class KumihoApiTest : public ::testing::Test {
protected:
    void SetUp() override {
        auto channel = grpc::CreateChannel("localhost:8080", grpc::InsecureChannelCredentials());
        client = std::make_unique<kumiho::api::Client>(channel);
    }

    void TearDown() override {
        std::cout << "TearDown: Starting cleanup of " 
                  << created_resources.size() << " resources, "
                  << created_versions.size() << " versions, "
                  << created_products.size() << " products, "
                  << created_groups.size() << " groups" << std::endl;
        
        // Clean up created objects in reverse dependency order: resources -> versions -> products -> groups
        for (auto it = created_resources.rbegin(); it != created_resources.rend(); ++it) {
            try {
                std::cout << "Deleting resource: " << (*it)->getKref().uri() << std::endl;
                (*it)->deleteResource(true);
                std::cout << "Successfully deleted resource" << std::endl;
            } catch (const std::exception& e) {
                std::cout << "ERROR: Failed to cleanup resource: " << e.what() << std::endl;
            }
        }
        created_resources.clear();

        for (auto it = created_versions.rbegin(); it != created_versions.rend(); ++it) {
            try {
                std::cout << "Deleting version: " << (*it)->getKref().uri() << std::endl;
                (*it)->deleteVersion(true);
                std::cout << "Successfully deleted version" << std::endl;
            } catch (const std::exception& e) {
                std::cout << "ERROR: Failed to cleanup version: " << e.what() << std::endl;
            }
        }
        created_versions.clear();

        for (auto it = created_products.rbegin(); it != created_products.rend(); ++it) {
            try {
                std::cout << "Deleting product: " << (*it)->getKref().uri() << std::endl;
                (*it)->deleteProduct(true);
                std::cout << "Successfully deleted product" << std::endl;
            } catch (const std::exception& e) {
                std::cout << "ERROR: Failed to cleanup product: " << e.what() << std::endl;
            }
        }
        created_products.clear();

        for (auto it = created_groups.rbegin(); it != created_groups.rend(); ++it) {
            try {
                std::cout << "Deleting group: " << (*it)->getPath() << std::endl;
                (*it)->deleteGroup(true);
                std::cout << "Successfully deleted group" << std::endl;
            } catch (const std::exception& e) {
                std::cout << "ERROR: Failed to cleanup group: " << e.what() << std::endl;
            }
        }
        created_groups.clear();
        
        std::cout << "TearDown: Cleanup completed" << std::endl;
    }

    std::unique_ptr<kumiho::api::Client> client;
    std::vector<std::shared_ptr<kumiho::api::Group>> created_groups;
    std::vector<std::shared_ptr<kumiho::api::Product>> created_products;
    std::vector<std::shared_ptr<kumiho::api::Version>> created_versions;
    std::vector<std::shared_ptr<kumiho::api::Resource>> created_resources;
};


// --- Integration Tests ---
TEST_F(KumihoApiTest, FullCreationWorkflow) {
    std::string project_name = unique_name("smoke_test_project");
    std::string asset_name = unique_name("smoke_test_asset");

    auto group = client->createGroup("/", project_name);
    ASSERT_NE(group, nullptr);
    EXPECT_EQ(group->getPath(), "/" + project_name);
    created_groups.push_back(group);

    auto product = group->createProduct(asset_name, "model");
    ASSERT_NE(product, nullptr);
    EXPECT_EQ(product->getKref().uri(), "kref://" + project_name + "/" + asset_name + ".model");
    created_products.push_back(product);

    auto version = product->createVersion();
    ASSERT_NE(version, nullptr);
    EXPECT_TRUE(version->getKref().uri().find("?v=1") != std::string::npos);
    created_versions.push_back(version);

    auto resource = version->createResource("data", "/path/to/smoke_test.dat");
    ASSERT_NE(resource, nullptr);
    EXPECT_TRUE(resource->getKref().uri().find("&r=data") != std::string::npos);
    EXPECT_EQ(resource->getLocation(), "/path/to/smoke_test.dat");
    created_resources.push_back(resource);
}

TEST_F(KumihoApiTest, VersionByTagAndTime) {
    std::string project_name = unique_name("tag_time_test_project");
    std::string asset_name = unique_name("tag_time_test_asset");

    auto group = client->createGroup("/", project_name);
    created_groups.push_back(group);
    auto product = group->createProduct(asset_name, "item");
    created_products.push_back(product);
    auto version1 = product->createVersion();
    created_versions.push_back(version1);
    auto version2 = product->createVersion();
    created_versions.push_back(version2);

    version1->tag("hello");

    auto tag_version = product->getVersionByTag("hello");
    ASSERT_NE(tag_version, nullptr);

    auto time_version = product->getVersionByTime(*version1->getCreatedAt());
    ASSERT_NE(time_version, nullptr);
}

TEST_F(KumihoApiTest, GetResourcesByLocation) {
    std::string project_name = unique_name("loc_test_project");
    std::string asset_name = unique_name("loc_test_asset");
    std::string shared_location = "/mnt/data/test_data/" + unique_name("loc_test") + ".vdb";

    auto group = client->createGroup("/", project_name);
    created_groups.push_back(group);
    auto product = group->createProduct(asset_name, "model");
    created_products.push_back(product);
    auto v1 = product->createVersion();
    created_versions.push_back(v1);
    std::this_thread::sleep_for(std::chrono::seconds(1));
    auto v2 = product->createVersion();
    created_versions.push_back(v2);

    auto res1 = v1->createResource("model_data", shared_location);
    created_resources.push_back(res1);
    auto res2 = v2->createResource("model_data", shared_location);
    created_resources.push_back(res2);

    auto found_resources = client->getResourcesByLocation(shared_location);
    ASSERT_GE(found_resources.size(), 2);

    auto newest_res = found_resources[0].get();
    auto oldest_res = found_resources[1].get();

    EXPECT_EQ(newest_res->getKref(), res2->getKref());
    EXPECT_EQ(newest_res->getVersionKref(), v2->getKref());
    EXPECT_EQ(newest_res->getProductKref(), product->getKref());

    EXPECT_EQ(oldest_res->getKref(), res1->getKref());
    EXPECT_EQ(oldest_res->getVersionKref(), v1->getKref());
    EXPECT_EQ(oldest_res->getProductKref(), product->getKref());
}

TEST_F(KumihoApiTest, LinkingWorkflow) {
    auto group = client->createGroup("/", unique_name("link_proj"));
    created_groups.push_back(group);
    
    auto model_product = group->createProduct("character_model", "model");
    created_products.push_back(model_product);
    auto texture_product = group->createProduct("character_textures", "texture");
    created_products.push_back(texture_product);

    auto model_v1 = model_product->createVersion();
    created_versions.push_back(model_v1);
    auto texture_v1 = texture_product->createVersion();
    created_versions.push_back(texture_v1);

    auto link = client->createLink(texture_v1->getKref(), model_v1->getKref(), "texture_for");
    ASSERT_NE(link, nullptr);
    EXPECT_EQ(link->getSourceKref(), texture_v1->getKref());
    EXPECT_EQ(link->getTargetKref(), model_v1->getKref());
    
    auto source_links = client->getLinks(texture_v1->getKref());
    ASSERT_GE(source_links.size(), 1);
    EXPECT_EQ(source_links[0]->getTargetKref(), model_v1->getKref());
    EXPECT_EQ(source_links[0]->getLinkType(), "texture_for");
}

TEST_F(KumihoApiTest, PeekNextVersion) {
    auto group = client->createGroup("/", unique_name("peek_test_project"));
    created_groups.push_back(group);
    auto product = group->createProduct(unique_name("peek_test_asset"), "rig");
    created_products.push_back(product);

    EXPECT_EQ(product->peekNextVersion(), 1);
    auto v1 = product->createVersion();
    created_versions.push_back(v1);
    EXPECT_EQ(v1->getVersionNumber(), 1);
    EXPECT_EQ(product->peekNextVersion(), 2);
    auto v2 = product->createVersion();
    created_versions.push_back(v2);
    EXPECT_EQ(v2->getVersionNumber(), 2);
    EXPECT_EQ(product->peekNextVersion(), 3);
}

TEST_F(KumihoApiTest, MetadataUpdateWorkflow) {
    auto group = client->createGroup("/", unique_name("meta_proj"));
    created_groups.push_back(group);
    auto product = group->createProduct(unique_name("asset"), "model");
    created_products.push_back(product);
    auto version = product->createVersion();
    created_versions.push_back(version);
    auto resource = version->createResource("geo", "/path/to/file.abc");
    created_resources.push_back(resource);

    auto updated_group = group->setMetadata({{"status", "active"}});
    auto updated_product = product->setMetadata({{"pipeline_step", "modeling"}});
    auto updated_version = version->setMetadata({{"approved_by", "lead"}});
    auto updated_resource = resource->setMetadata({{"format", "alembic"}});

    ASSERT_EQ(updated_group->getMetadata().at("status"), "active");
    ASSERT_EQ(updated_product->getMetadata().at("pipeline_step"), "modeling");
    ASSERT_EQ(updated_version->getMetadata().at("approved_by"), "lead");
    ASSERT_EQ(updated_resource->getMetadata().at("format"), "alembic");
}

TEST_F(KumihoApiTest, GroupDeletionLogic) {
    auto proj = client->createGroup("/", unique_name("del_proj"));
    auto prod = proj->createProduct("asset", "model");
    auto empty_group = client->createGroup("/", unique_name("del_empty"));

    // 1. Fail to delete non-empty group without force
    EXPECT_THROW(proj->deleteGroup(), std::runtime_error);

    // 2. Succeed in deleting non-empty group with force
    EXPECT_NO_THROW(proj->deleteGroup(true));
    EXPECT_THROW(client->getGroup(proj->getPath()), std::runtime_error);

    // 3. Succeed in deleting empty group without force
    EXPECT_NO_THROW(empty_group->deleteGroup());
    EXPECT_THROW(client->getGroup(empty_group->getPath()), std::runtime_error);
}

TEST_F(KumihoApiTest, ProductDeprecationAndDeletion) {
    auto group = client->createGroup("/", unique_name("dep_proj"));
    created_groups.push_back(group);
    auto prod = group->createProduct("char", "rig");
    created_products.push_back(prod);
    
    // 1. Deprecate the product (soft delete)
    prod->deleteProduct();
    auto prod_reloaded = group->getProduct("char", "rig");
    ASSERT_TRUE(prod_reloaded->isDeprecated());
    
    // 2. Re-creating it should un-deprecate it
    auto prod_new = group->createProduct("char", "rig");
    created_products.push_back(prod_new);
    ASSERT_FALSE(prod_new->isDeprecated());
    
    // 3. Hard-delete with force
    prod_new->deleteProduct(true);
    
    // 4. Verify it's gone
    EXPECT_THROW(group->getProduct("char", "rig"), std::runtime_error);
}


TEST_F(KumihoApiTest, VersionTaggingWorkflow) {
    auto group = client->createGroup("/", unique_name("tag_proj"));
    created_groups.push_back(group);
    auto prod = group->createProduct("fx", "cache");
    created_products.push_back(prod);
    auto v1 = prod->createVersion();
    created_versions.push_back(v1);

    ASSERT_FALSE(v1->hasTag("approved"));
    
    v1->tag("approved");
    ASSERT_TRUE(v1->hasTag("approved"));
    ASSERT_TRUE(v1->wasTagged("approved"));

    v1->untag("approved");
    ASSERT_FALSE(v1->hasTag("approved"));
    ASSERT_TRUE(v1->wasTagged("approved"));
}

TEST_F(KumihoApiTest, PublishedVersionImmutability) {
    auto group = client->createGroup("/", unique_name("immutable_proj"));
    created_groups.push_back(group);
    auto prod = group->createProduct("shot", "comp");
    created_products.push_back(prod);
    auto v1 = prod->createVersion();
    created_versions.push_back(v1);
    auto res = v1->createResource("main", "/path/to/exr_seq");
    created_resources.push_back(res);

    v1->tag(PUBLISHED_TAG);
    auto v1_reloaded = prod->getVersion(1);
    ASSERT_TRUE(v1_reloaded->isPublished());

    EXPECT_THROW(v1->setMetadata({{"new_key", "new_val"}}), std::runtime_error);
    EXPECT_THROW(res->setMetadata({{"new_key", "new_val"}}), std::runtime_error);
    EXPECT_THROW(v1->untag(PUBLISHED_TAG), std::runtime_error);
    EXPECT_THROW(v1->deleteVersion(), std::runtime_error);
    EXPECT_THROW(res->deleteResource(), std::runtime_error);
    EXPECT_THROW(v1->createResource("mask", "/path/to/mask.png"), std::runtime_error);
}

TEST_F(KumihoApiTest, GetResourceAndLocations) {
    auto group = client->createGroup("/", unique_name("res_proj"));
    created_groups.push_back(group);
    auto prod = group->createProduct("set", "env");
    created_products.push_back(prod);
    auto v = prod->createVersion();
    created_versions.push_back(v);
    auto res1 = v->createResource("hdri", "/loc/hdri.exr");
    created_resources.push_back(res1);
    auto res2 = v->createResource("lidar", "/loc/lidar.obj");
    created_resources.push_back(res2);

    auto resources = v->getResources();
    ASSERT_EQ(resources.size(), 2);
    
    auto lidar_res = v->getResource("lidar");
    ASSERT_EQ(lidar_res->getKref(), res2->getKref());
    ASSERT_EQ(lidar_res->getLocation(), "/loc/lidar.obj");

    auto locations = v->getLocations();
    ASSERT_EQ(locations.size(), 2);
    bool found_hdri = false;
    bool found_lidar = false;
    for (const auto& loc : locations) {
        if (loc == "/loc/hdri.exr") found_hdri = true;
        if (loc == "/loc/lidar.obj") found_lidar = true;
    }
    ASSERT_TRUE(found_hdri && found_lidar);
}

TEST_F(KumihoApiTest, GetProductByKref) {
    auto group = client->createGroup("/", unique_name("kref_test_project"));
    created_groups.push_back(group);
    auto product = group->createProduct(unique_name("kref_test_asset"), "model");
    created_products.push_back(product);
    
    // Test getting product by kref
    auto retrieved_product = client->getProductByKref(product->getKref().uri());
    ASSERT_NE(retrieved_product, nullptr);
    EXPECT_EQ(retrieved_product->getKref().uri(), product->getKref().uri());
}

TEST_F(KumihoApiTest, GetLatestVersion) {
    auto group = client->createGroup("/", unique_name("latest_test_project"));
    created_groups.push_back(group);
    auto product = group->createProduct(unique_name("latest_test_asset"), "model");
    created_products.push_back(product);
    
    // Create multiple versions
    auto v1 = product->createVersion();
    created_versions.push_back(v1);
    auto v2 = product->createVersion();
    created_versions.push_back(v2);
    auto v3 = product->createVersion();
    created_versions.push_back(v3);
    
    // Debug: Check all versions
    auto all_versions = product->getVersions();
    std::cout << "Total versions: " << all_versions.size() << std::endl;
    for (const auto& v : all_versions) {
        std::cout << "Version " << v->getVersionNumber() << ": " << v->getKref().uri() 
                  << " latest=" << v->isLatest() << " tags=[";
        auto tags = v->getTags();
        for (size_t i = 0; i < tags.size(); ++i) {
            std::cout << tags[i];
            if (i < tags.size() - 1) std::cout << ",";
        }
        std::cout << "]" << std::endl;
    }
    
    // Test getting latest version
    auto latest = product->getLatestVersion();
    ASSERT_NE(latest, nullptr);
    std::cout << "Latest version: " << latest->getVersionNumber() << " kref: " << latest->getKref().uri() << std::endl;
    
    // The latest version should be v3
    EXPECT_EQ(latest->getVersionNumber(), 3);
    EXPECT_EQ(latest->getKref().uri(), v3->getKref().uri());
}

// Test navigation methods
TEST_F(KumihoApiTest, NavigationMethods) {
    // Create a group
    auto group = client->createGroup("/", unique_name("test_nav"));
    ASSERT_NE(group, nullptr);
    
    // Create a product in the group
    auto product = group->createProduct("test_product", "model");
    ASSERT_NE(product, nullptr);
    
    // Create a version
    auto version = product->createVersion();
    ASSERT_NE(version, nullptr);
    
    // Test Version::getProduct()
    auto product_from_version = version->getProduct();
    ASSERT_NE(product_from_version, nullptr);
    EXPECT_EQ(product_from_version->getKref().uri(), product->getKref().uri());
    
    // Test Version::getGroup()
    auto group_from_version = version->getGroup();
    ASSERT_NE(group_from_version, nullptr);
    EXPECT_EQ(group_from_version->getPath(), group->getPath());
    
    // Test Product::getGroup()
    auto group_from_product = product->getGroup();
    ASSERT_NE(group_from_product, nullptr);
    EXPECT_EQ(group_from_product->getPath(), group->getPath());
    
    // Test Group::getParentGroup() - should return nullptr for root-level group
    auto parent_group = group->getParentGroup();
    EXPECT_EQ(parent_group, nullptr);
    
    // Create a subgroup to test parent navigation
    auto subgroup = group->createGroup("subgroup");
    ASSERT_NE(subgroup, nullptr);
    
    // Test Group::getParentGroup() for subgroup
    auto parent_of_subgroup = subgroup->getParentGroup();
    ASSERT_NE(parent_of_subgroup, nullptr);
    EXPECT_EQ(parent_of_subgroup->getPath(), group->getPath());
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}