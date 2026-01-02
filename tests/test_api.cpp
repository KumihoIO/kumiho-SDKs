#include <grpcpp/grpcpp.h>
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <kumiho/kumiho.hpp>
#include <kumiho.pb.h>
#include <kumiho.grpc.pb.h>
#include <kumiho/token_loader.hpp>
#include <memory>
#include <chrono>
#include <thread>
#include <string>
#include <cstdlib> // For getenv
#include <iomanip> // For std::put_time
#include <sstream> // For std::ostringstream

using ::testing::_;
using ::testing::Return;
using ::testing::SetArgPointee;
using ::testing::DoAll;

// --- Constants ---
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

    // Space methods (formerly Group)
    MOCK_METHOD(grpc::Status, CreateSpace, (grpc::ClientContext* context, const kumiho::CreateSpaceRequest& request, kumiho::SpaceResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetSpace, (grpc::ClientContext* context, const kumiho::GetSpaceRequest& request, kumiho::SpaceResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetChildSpaces, (grpc::ClientContext* context, const kumiho::GetChildSpacesRequest& request, kumiho::GetChildSpacesResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteSpace, (grpc::ClientContext* context, const kumiho::DeleteSpaceRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, UpdateSpaceMetadata, (grpc::ClientContext* context, const kumiho::UpdateMetadataRequest& request, kumiho::SpaceResponse* response), (override));

    // Item methods (formerly Product)
    MOCK_METHOD(grpc::Status, CreateItem, (grpc::ClientContext* context, const kumiho::CreateItemRequest& request, kumiho::ItemResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetItem, (grpc::ClientContext* context, const kumiho::GetItemRequest& request, kumiho::ItemResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetItems, (grpc::ClientContext* context, const kumiho::GetItemsRequest& request, kumiho::GetItemsResponse* response), (override));
    MOCK_METHOD(grpc::Status, ItemSearch, (grpc::ClientContext* context, const kumiho::ItemSearchRequest& request, kumiho::GetItemsResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteItem, (grpc::ClientContext* context, const kumiho::DeleteItemRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, UpdateItemMetadata, (grpc::ClientContext* context, const kumiho::UpdateMetadataRequest& request, kumiho::ItemResponse* response), (override));

    // Revision methods (formerly Version)
    MOCK_METHOD(grpc::Status, ResolveKref, (grpc::ClientContext* context, const kumiho::ResolveKrefRequest& request, kumiho::RevisionResponse* response), (override));
    MOCK_METHOD(grpc::Status, ResolveLocation, (grpc::ClientContext* context, const kumiho::ResolveLocationRequest& request, kumiho::ResolveLocationResponse* response), (override));
    MOCK_METHOD(grpc::Status, CreateRevision, (grpc::ClientContext* context, const kumiho::CreateRevisionRequest& request, kumiho::RevisionResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetRevision, (grpc::ClientContext* context, const kumiho::KrefRequest& request, kumiho::RevisionResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetRevisions, (grpc::ClientContext* context, const kumiho::GetRevisionsRequest& request, kumiho::GetRevisionsResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteRevision, (grpc::ClientContext* context, const kumiho::DeleteRevisionRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, PeekNextRevision, (grpc::ClientContext* context, const kumiho::PeekNextRevisionRequest& request, kumiho::PeekNextRevisionResponse* response), (override));
    MOCK_METHOD(grpc::Status, UpdateRevisionMetadata, (grpc::ClientContext* context, const kumiho::UpdateMetadataRequest& request, kumiho::RevisionResponse* response), (override));
    MOCK_METHOD(grpc::Status, TagRevision, (grpc::ClientContext* context, const kumiho::TagRevisionRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, UnTagRevision, (grpc::ClientContext* context, const kumiho::UnTagRevisionRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, HasTag, (grpc::ClientContext* context, const kumiho::HasTagRequest& request, kumiho::HasTagResponse* response), (override));
    MOCK_METHOD(grpc::Status, WasTagged, (grpc::ClientContext* context, const kumiho::WasTaggedRequest& request, kumiho::WasTaggedResponse* response), (override));
    MOCK_METHOD(grpc::Status, SetDefaultArtifact, (grpc::ClientContext* context, const kumiho::SetDefaultArtifactRequest& request, kumiho::StatusResponse* response), (override));

    // Artifact methods (formerly Resource)
    MOCK_METHOD(grpc::Status, CreateArtifact, (grpc::ClientContext* context, const kumiho::CreateArtifactRequest& request, kumiho::ArtifactResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetArtifact, (grpc::ClientContext* context, const kumiho::GetArtifactRequest& request, kumiho::ArtifactResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetArtifacts, (grpc::ClientContext* context, const kumiho::GetArtifactsRequest& request, kumiho::GetArtifactsResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetArtifactsByLocation, (grpc::ClientContext* context, const kumiho::GetArtifactsByLocationRequest& request, kumiho::GetArtifactsByLocationResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteArtifact, (grpc::ClientContext* context, const kumiho::DeleteArtifactRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, UpdateArtifactMetadata, (grpc::ClientContext* context, const kumiho::UpdateMetadataRequest& request, kumiho::ArtifactResponse* response), (override));

    // Attribute methods
    MOCK_METHOD(grpc::Status, SetAttribute, (grpc::ClientContext* context, const kumiho::SetAttributeRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetAttribute, (grpc::ClientContext* context, const kumiho::GetAttributeRequest& request, kumiho::GetAttributeResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteAttribute, (grpc::ClientContext* context, const kumiho::DeleteAttributeRequest& request, kumiho::StatusResponse* response), (override));

    // Edge methods (formerly Link)
    MOCK_METHOD(grpc::Status, CreateEdge, (grpc::ClientContext* context, const kumiho::CreateEdgeRequest& request, kumiho::StatusResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetEdges, (grpc::ClientContext* context, const kumiho::GetEdgesRequest& request, kumiho::GetEdgesResponse* response), (override));
    MOCK_METHOD(grpc::Status, DeleteEdge, (grpc::ClientContext* context, const kumiho::DeleteEdgeRequest& request, kumiho::StatusResponse* response), (override));

    // Graph traversal methods
    MOCK_METHOD(grpc::Status, TraverseEdges, (grpc::ClientContext* context, const kumiho::TraverseEdgesRequest& request, kumiho::TraverseEdgesResponse* response), (override));
    MOCK_METHOD(grpc::Status, FindShortestPath, (grpc::ClientContext* context, const kumiho::ShortestPathRequest& request, kumiho::ShortestPathResponse* response), (override));
    MOCK_METHOD(grpc::Status, AnalyzeImpact, (grpc::ClientContext* context, const kumiho::ImpactAnalysisRequest& request, kumiho::ImpactAnalysisResponse* response), (override));

    // Bundle methods (formerly Collection)
    MOCK_METHOD(grpc::Status, CreateBundle, (grpc::ClientContext* context, const kumiho::CreateBundleRequest& request, kumiho::ItemResponse* response), (override));
    MOCK_METHOD(grpc::Status, AddBundleMember, (grpc::ClientContext* context, const kumiho::AddBundleMemberRequest& request, kumiho::AddBundleMemberResponse* response), (override));
    MOCK_METHOD(grpc::Status, RemoveBundleMember, (grpc::ClientContext* context, const kumiho::RemoveBundleMemberRequest& request, kumiho::RemoveBundleMemberResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetBundleMembers, (grpc::ClientContext* context, const kumiho::GetBundleMembersRequest& request, kumiho::GetBundleMembersResponse* response), (override));
    MOCK_METHOD(grpc::Status, GetBundleHistory, (grpc::ClientContext* context, const kumiho::GetBundleHistoryRequest& request, kumiho::GetBundleHistoryResponse* response), (override));

    // Tenant methods
    MOCK_METHOD(grpc::Status, GetTenantUsage, (grpc::ClientContext* context, const kumiho::GetTenantUsageRequest& request, kumiho::TenantUsageResponse* response), (override));

    // Event methods
    MOCK_METHOD(grpc::Status, GetEventCapabilities, (grpc::ClientContext* context, const kumiho::GetEventCapabilitiesRequest& request, kumiho::EventCapabilities* response), (override));
    MOCK_METHOD(grpc::ClientAsyncResponseReaderInterface<kumiho::EventCapabilities>*, AsyncGetEventCapabilitiesRaw, (grpc::ClientContext* context, const kumiho::GetEventCapabilitiesRequest& request, grpc::CompletionQueue* cq), (override));
    MOCK_METHOD(grpc::ClientAsyncResponseReaderInterface<kumiho::EventCapabilities>*, PrepareAsyncGetEventCapabilitiesRaw, (grpc::ClientContext* context, const kumiho::GetEventCapabilitiesRequest& request, grpc::CompletionQueue* cq), (override));

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
    
    // Space async methods (formerly Group)
    grpc::ClientAsyncResponseReaderInterface<kumiho::SpaceResponse>* AsyncCreateSpaceRaw(grpc::ClientContext*, const kumiho::CreateSpaceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::SpaceResponse>* PrepareAsyncCreateSpaceRaw(grpc::ClientContext*, const kumiho::CreateSpaceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::SpaceResponse>* AsyncGetSpaceRaw(grpc::ClientContext*, const kumiho::GetSpaceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::SpaceResponse>* PrepareAsyncGetSpaceRaw(grpc::ClientContext*, const kumiho::GetSpaceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetChildSpacesResponse>* AsyncGetChildSpacesRaw(grpc::ClientContext*, const kumiho::GetChildSpacesRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetChildSpacesResponse>* PrepareAsyncGetChildSpacesRaw(grpc::ClientContext*, const kumiho::GetChildSpacesRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteSpaceRaw(grpc::ClientContext*, const kumiho::DeleteSpaceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteSpaceRaw(grpc::ClientContext*, const kumiho::DeleteSpaceRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::SpaceResponse>* AsyncUpdateSpaceMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::SpaceResponse>* PrepareAsyncUpdateSpaceMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Item async methods (formerly Product)
    grpc::ClientAsyncResponseReaderInterface<kumiho::ItemResponse>* AsyncCreateItemRaw(grpc::ClientContext*, const kumiho::CreateItemRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ItemResponse>* PrepareAsyncCreateItemRaw(grpc::ClientContext*, const kumiho::CreateItemRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ItemResponse>* AsyncGetItemRaw(grpc::ClientContext*, const kumiho::GetItemRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ItemResponse>* PrepareAsyncGetItemRaw(grpc::ClientContext*, const kumiho::GetItemRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetItemsResponse>* AsyncGetItemsRaw(grpc::ClientContext*, const kumiho::GetItemsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetItemsResponse>* PrepareAsyncGetItemsRaw(grpc::ClientContext*, const kumiho::GetItemsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetItemsResponse>* AsyncItemSearchRaw(grpc::ClientContext*, const kumiho::ItemSearchRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetItemsResponse>* PrepareAsyncItemSearchRaw(grpc::ClientContext*, const kumiho::ItemSearchRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteItemRaw(grpc::ClientContext*, const kumiho::DeleteItemRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteItemRaw(grpc::ClientContext*, const kumiho::DeleteItemRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ItemResponse>* AsyncUpdateItemMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ItemResponse>* PrepareAsyncUpdateItemMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Revision async methods (formerly Version)
    grpc::ClientAsyncResponseReaderInterface<kumiho::RevisionResponse>* AsyncResolveKrefRaw(grpc::ClientContext*, const kumiho::ResolveKrefRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RevisionResponse>* PrepareAsyncResolveKrefRaw(grpc::ClientContext*, const kumiho::ResolveKrefRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ResolveLocationResponse>* AsyncResolveLocationRaw(grpc::ClientContext*, const kumiho::ResolveLocationRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ResolveLocationResponse>* PrepareAsyncResolveLocationRaw(grpc::ClientContext*, const kumiho::ResolveLocationRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RevisionResponse>* AsyncCreateRevisionRaw(grpc::ClientContext*, const kumiho::CreateRevisionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RevisionResponse>* PrepareAsyncCreateRevisionRaw(grpc::ClientContext*, const kumiho::CreateRevisionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RevisionResponse>* AsyncGetRevisionRaw(grpc::ClientContext*, const kumiho::KrefRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RevisionResponse>* PrepareAsyncGetRevisionRaw(grpc::ClientContext*, const kumiho::KrefRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetRevisionsResponse>* AsyncGetRevisionsRaw(grpc::ClientContext*, const kumiho::GetRevisionsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetRevisionsResponse>* PrepareAsyncGetRevisionsRaw(grpc::ClientContext*, const kumiho::GetRevisionsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteRevisionRaw(grpc::ClientContext*, const kumiho::DeleteRevisionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteRevisionRaw(grpc::ClientContext*, const kumiho::DeleteRevisionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::PeekNextRevisionResponse>* AsyncPeekNextRevisionRaw(grpc::ClientContext*, const kumiho::PeekNextRevisionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::PeekNextRevisionResponse>* PrepareAsyncPeekNextRevisionRaw(grpc::ClientContext*, const kumiho::PeekNextRevisionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RevisionResponse>* AsyncUpdateRevisionMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RevisionResponse>* PrepareAsyncUpdateRevisionMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncTagRevisionRaw(grpc::ClientContext*, const kumiho::TagRevisionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncTagRevisionRaw(grpc::ClientContext*, const kumiho::TagRevisionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncUnTagRevisionRaw(grpc::ClientContext*, const kumiho::UnTagRevisionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncUnTagRevisionRaw(grpc::ClientContext*, const kumiho::UnTagRevisionRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::HasTagResponse>* AsyncHasTagRaw(grpc::ClientContext*, const kumiho::HasTagRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::HasTagResponse>* PrepareAsyncHasTagRaw(grpc::ClientContext*, const kumiho::HasTagRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::WasTaggedResponse>* AsyncWasTaggedRaw(grpc::ClientContext*, const kumiho::WasTaggedRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::WasTaggedResponse>* PrepareAsyncWasTaggedRaw(grpc::ClientContext*, const kumiho::WasTaggedRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncSetDefaultArtifactRaw(grpc::ClientContext*, const kumiho::SetDefaultArtifactRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncSetDefaultArtifactRaw(grpc::ClientContext*, const kumiho::SetDefaultArtifactRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Artifact async methods (formerly Resource)
    grpc::ClientAsyncResponseReaderInterface<kumiho::ArtifactResponse>* AsyncCreateArtifactRaw(grpc::ClientContext*, const kumiho::CreateArtifactRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ArtifactResponse>* PrepareAsyncCreateArtifactRaw(grpc::ClientContext*, const kumiho::CreateArtifactRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ArtifactResponse>* AsyncGetArtifactRaw(grpc::ClientContext*, const kumiho::GetArtifactRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ArtifactResponse>* PrepareAsyncGetArtifactRaw(grpc::ClientContext*, const kumiho::GetArtifactRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetArtifactsResponse>* AsyncGetArtifactsRaw(grpc::ClientContext*, const kumiho::GetArtifactsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetArtifactsResponse>* PrepareAsyncGetArtifactsRaw(grpc::ClientContext*, const kumiho::GetArtifactsRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetArtifactsByLocationResponse>* AsyncGetArtifactsByLocationRaw(grpc::ClientContext*, const kumiho::GetArtifactsByLocationRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetArtifactsByLocationResponse>* PrepareAsyncGetArtifactsByLocationRaw(grpc::ClientContext*, const kumiho::GetArtifactsByLocationRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteArtifactRaw(grpc::ClientContext*, const kumiho::DeleteArtifactRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteArtifactRaw(grpc::ClientContext*, const kumiho::DeleteArtifactRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ArtifactResponse>* AsyncUpdateArtifactMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ArtifactResponse>* PrepareAsyncUpdateArtifactMetadataRaw(grpc::ClientContext*, const kumiho::UpdateMetadataRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Attribute async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncSetAttributeRaw(grpc::ClientContext*, const kumiho::SetAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncSetAttributeRaw(grpc::ClientContext*, const kumiho::SetAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetAttributeResponse>* AsyncGetAttributeRaw(grpc::ClientContext*, const kumiho::GetAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetAttributeResponse>* PrepareAsyncGetAttributeRaw(grpc::ClientContext*, const kumiho::GetAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteAttributeRaw(grpc::ClientContext*, const kumiho::DeleteAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteAttributeRaw(grpc::ClientContext*, const kumiho::DeleteAttributeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Edge async methods (formerly Link)
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncCreateEdgeRaw(grpc::ClientContext*, const kumiho::CreateEdgeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncCreateEdgeRaw(grpc::ClientContext*, const kumiho::CreateEdgeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetEdgesResponse>* AsyncGetEdgesRaw(grpc::ClientContext*, const kumiho::GetEdgesRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetEdgesResponse>* PrepareAsyncGetEdgesRaw(grpc::ClientContext*, const kumiho::GetEdgesRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* AsyncDeleteEdgeRaw(grpc::ClientContext*, const kumiho::DeleteEdgeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::StatusResponse>* PrepareAsyncDeleteEdgeRaw(grpc::ClientContext*, const kumiho::DeleteEdgeRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Graph traversal async methods
    grpc::ClientAsyncResponseReaderInterface<kumiho::TraverseEdgesResponse>* AsyncTraverseEdgesRaw(grpc::ClientContext*, const kumiho::TraverseEdgesRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::TraverseEdgesResponse>* PrepareAsyncTraverseEdgesRaw(grpc::ClientContext*, const kumiho::TraverseEdgesRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ShortestPathResponse>* AsyncFindShortestPathRaw(grpc::ClientContext*, const kumiho::ShortestPathRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ShortestPathResponse>* PrepareAsyncFindShortestPathRaw(grpc::ClientContext*, const kumiho::ShortestPathRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ImpactAnalysisResponse>* AsyncAnalyzeImpactRaw(grpc::ClientContext*, const kumiho::ImpactAnalysisRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ImpactAnalysisResponse>* PrepareAsyncAnalyzeImpactRaw(grpc::ClientContext*, const kumiho::ImpactAnalysisRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
    // Bundle async methods (formerly Collection)
    grpc::ClientAsyncResponseReaderInterface<kumiho::ItemResponse>* AsyncCreateBundleRaw(grpc::ClientContext*, const kumiho::CreateBundleRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::ItemResponse>* PrepareAsyncCreateBundleRaw(grpc::ClientContext*, const kumiho::CreateBundleRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::AddBundleMemberResponse>* AsyncAddBundleMemberRaw(grpc::ClientContext*, const kumiho::AddBundleMemberRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::AddBundleMemberResponse>* PrepareAsyncAddBundleMemberRaw(grpc::ClientContext*, const kumiho::AddBundleMemberRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RemoveBundleMemberResponse>* AsyncRemoveBundleMemberRaw(grpc::ClientContext*, const kumiho::RemoveBundleMemberRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::RemoveBundleMemberResponse>* PrepareAsyncRemoveBundleMemberRaw(grpc::ClientContext*, const kumiho::RemoveBundleMemberRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetBundleMembersResponse>* AsyncGetBundleMembersRaw(grpc::ClientContext*, const kumiho::GetBundleMembersRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetBundleMembersResponse>* PrepareAsyncGetBundleMembersRaw(grpc::ClientContext*, const kumiho::GetBundleMembersRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetBundleHistoryResponse>* AsyncGetBundleHistoryRaw(grpc::ClientContext*, const kumiho::GetBundleHistoryRequest&, grpc::CompletionQueue*) override { return nullptr; }
    grpc::ClientAsyncResponseReaderInterface<kumiho::GetBundleHistoryResponse>* PrepareAsyncGetBundleHistoryRaw(grpc::ClientContext*, const kumiho::GetBundleHistoryRequest&, grpc::CompletionQueue*) override { return nullptr; }
    
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
TEST_F(KumihoUnitTest, CreateSpace) {
    kumiho::SpaceResponse fake_response;
    fake_response.set_path("/projectA/seqA");
    EXPECT_CALL(*mock_stub, CreateSpace(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(fake_response), Return(grpc::Status::OK)));

    auto space = client->createSpace("/projectA", "seqA");
    ASSERT_NE(space, nullptr);
    EXPECT_EQ(space->getPath(), "/projectA/seqA");
}

TEST_F(KumihoUnitTest, GetSpaceFromPath) {
    kumiho::SpaceResponse fake_response;
    fake_response.set_path("/projectA/seqA");
    EXPECT_CALL(*mock_stub, GetSpace(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(fake_response), Return(grpc::Status::OK)));
    
    auto space = client->getSpace("projectA/seqA");
    ASSERT_NE(space, nullptr);
    EXPECT_EQ(space->getPath(), "/projectA/seqA");
}

TEST_F(KumihoUnitTest, ItemSearchWithContext) {
    kumiho::GetItemsResponse fake_response;
    auto* item_res = fake_response.add_items();
    item_res->mutable_kref()->set_uri("kref://projectA/seqA/001/kumiho.model");

    EXPECT_CALL(*mock_stub, ItemSearch(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(fake_response), Return(grpc::Status::OK)));

    auto results = client->itemSearch("projectA/seqA", "", "model");
    ASSERT_EQ(results.items.size(), 1);
    EXPECT_EQ(results.items[0]->getKref().uri(), "kref://projectA/seqA/001/kumiho.model");
}

TEST_F(KumihoUnitTest, Pagination) {
    // Setup mock items
    kumiho::ItemResponse item1_pb;
    item1_pb.mutable_kref()->set_uri("kref://p1/s1/i1");
    item1_pb.set_name("i1");
    item1_pb.set_item_name("i1");
    item1_pb.set_kind("model");

    kumiho::ItemResponse item2_pb;
    item2_pb.mutable_kref()->set_uri("kref://p1/s1/i2");
    item2_pb.set_name("i2");
    item2_pb.set_item_name("i2");
    item2_pb.set_kind("model");

    // Mock GetItems response with pagination
    kumiho::GetItemsResponse response_pb;
    *response_pb.add_items() = item1_pb;
    *response_pb.add_items() = item2_pb;
    
    auto* pagination = response_pb.mutable_pagination();
    pagination->set_next_cursor("cursor_123");
    pagination->set_total_count(10);

    // Expect ItemSearch call for Project::getItems
    EXPECT_CALL(*mock_stub, ItemSearch(_, _, _))
        .WillOnce(DoAll(
            SetArgPointee<2>(response_pb),
            Return(grpc::Status::OK)
        ));

    // Test Project::getItems
    kumiho::ProjectResponse project_pb;
    project_pb.set_project_id("p1");
    project_pb.set_name("p1");
    project_pb.set_description("demo");
    auto project = std::make_shared<kumiho::api::Project>(project_pb, client.get());
    auto results = project->getItems("", "model", 2);

    // Verify response
    EXPECT_EQ(results.items.size(), 2);
    EXPECT_EQ(results.next_cursor, "cursor_123");
    EXPECT_EQ(results.total_count, 10);
    EXPECT_EQ(results.items[0]->getName(), "i1");

    // Expect ItemSearch call for Space::getItems
    EXPECT_CALL(*mock_stub, ItemSearch(_, _, _))
        .WillOnce(DoAll(
            SetArgPointee<2>(response_pb),
            Return(grpc::Status::OK)
        ));

    kumiho::SpaceResponse space_pb;
    space_pb.set_path("/p1/s1");
    auto space = std::make_shared<kumiho::api::Space>(space_pb, client.get());
    auto results_page2 = space->getItems("", "model", 2, "cursor_123");

    EXPECT_EQ(results_page2.items.size(), 2);
    EXPECT_EQ(results_page2.next_cursor, "cursor_123");
}

TEST_F(KumihoUnitTest, ResolveKrefWithTime) {
    kumiho::RevisionResponse fake_response;
    fake_response.mutable_kref()->set_uri("kref://obj1?r=2");
    fake_response.set_number(2);

    EXPECT_CALL(*mock_stub, ResolveKref(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(fake_response), Return(grpc::Status::OK)));
    
    auto resolved = client->resolveKref("kref://obj1", "", "202510131200");
    ASSERT_NE(resolved, nullptr);
    EXPECT_EQ(resolved->getRevisionNumber(), 2);
}

TEST_F(KumihoUnitTest, ResolveKrefWithTagAndTime) {
    kumiho::RevisionResponse fake_response;
    fake_response.mutable_kref()->set_uri("kref://obj1?r=1");
    fake_response.set_number(1);

    EXPECT_CALL(*mock_stub, ResolveKref(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(fake_response), Return(grpc::Status::OK)));

    auto resolved = client->resolveKref("kref://obj1", "published", "202510101000");
    ASSERT_NE(resolved, nullptr);
    EXPECT_EQ(resolved->getRevisionNumber(), 1);
}

TEST_F(KumihoUnitTest, ResolveKrefInvalidTimeFormat) {
    EXPECT_THROW(client->resolveKref("kref://some_id", "", "2025-10-13 12:00:00"), kumiho::api::ValidationError);
}

TEST_F(KumihoUnitTest, ResolveItemKrefFallbackToFirstArtifact) {
    // Setup: Item KREF, no default_artifact, but one artifact exists
    // The client->resolve() method calls ResolveKref internally
    kumiho::RevisionResponse revision_response;
    revision_response.mutable_kref()->set_uri("kref://space1/item1.kind?r=1");
    revision_response.set_number(1);
    
    EXPECT_CALL(*mock_stub, ResolveKref(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(revision_response), Return(grpc::Status::OK)));

    kumiho::ArtifactResponse artifact_response;
    artifact_response.set_location("/path/to/artifact1");
    kumiho::GetArtifactsResponse artifacts_response;
    auto* r = artifacts_response.add_artifacts();
    *r = artifact_response;
    EXPECT_CALL(*mock_stub, GetArtifacts(_, _, _))
        .WillOnce(DoAll(SetArgPointee<2>(artifacts_response), Return(grpc::Status::OK)));

    auto location = client->resolve("kref://space1/item1.kind");
    ASSERT_TRUE(location.has_value());
    EXPECT_EQ(location.value(), "/path/to/artifact1");
}
int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}