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
    ASSERT_EQ(results.size(), 1);
    EXPECT_EQ(results[0]->getKref().uri(), "kref://projectA/seqA/001/kumiho.model");
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

    // Expect GetItems call for Project::getItems
    EXPECT_CALL(*mock_stub, GetItems(_, _, _))
        .WillOnce(DoAll(
            SetArgPointee<2>(response_pb),
            Return(grpc::Status::OK)
        ));

    // Test Project::getItems
    auto project = std::make_shared<kumiho::Project>(client, "p1", "demo", "", "", "", false);
    auto results = project->getItems(2);

    // Verify response
    EXPECT_EQ(results.items.size(), 2);
    EXPECT_EQ(results.next_cursor, "cursor_123");
    EXPECT_EQ(results.total_count, 10);
    EXPECT_EQ(results.items[0]->getName(), "i1");

    // Expect GetItems call for Space::getItems
    EXPECT_CALL(*mock_stub, GetItems(_, _, _))
        .WillOnce(DoAll(
            SetArgPointee<2>(response_pb),
            Return(grpc::Status::OK)
        ));

    auto space = std::make_shared<kumiho::Space>(client, "p1/s1");
    auto results_page2 = space->getItems(2, "cursor_123");

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

// --- Integration Test Fixture ---
class KumihoApiTest : public ::testing::Test {
protected:
    void SetUp() override {
        auto channel = grpc::CreateChannel("localhost:8080", grpc::InsecureChannelCredentials());
        client = std::make_unique<kumiho::api::Client>(channel);
        
        // Try to load token from standard location first
        auto token = kumiho::api::loadBearerToken();
        if (token) {
            client->setAuthToken(*token);
        } else {
            // Fallback to environment variable if standard loading fails
            const char* env_token = std::getenv("KUMIHO_AUTH_TOKEN");
            if (env_token) {
                client->setAuthToken(env_token);
            } else {
                std::cerr << "WARNING: No auth token found. Integration tests may fail." << std::endl;
            }
        }
    }

    void TearDown() override {
        std::cout << "TearDown: Starting cleanup of " 
                  << created_artifacts.size() << " artifacts, "
                  << created_revisions.size() << " revisions, "
                  << created_items.size() << " items, "
                  << created_spaces.size() << " spaces, "
                  << created_projects.size() << " projects" << std::endl;
        
        // Clean up created objects in reverse dependency order: artifacts -> revisions -> items -> spaces -> projects
        for (auto it = created_artifacts.rbegin(); it != created_artifacts.rend(); ++it) {
            try {
                std::cout << "Deleting artifact: " << (*it)->getKref().uri() << std::endl;
                (*it)->deleteArtifact(true);
                std::cout << "Successfully deleted artifact" << std::endl;
            } catch (const std::exception& e) {
                std::cout << "ERROR: Failed to cleanup artifact: " << e.what() << std::endl;
            }
        }
        created_artifacts.clear();

        for (auto it = created_revisions.rbegin(); it != created_revisions.rend(); ++it) {
            try {
                std::cout << "Deleting revision: " << (*it)->getKref().uri() << std::endl;
                (*it)->deleteRevision(true);
                std::cout << "Successfully deleted revision" << std::endl;
            } catch (const std::exception& e) {
                std::cout << "ERROR: Failed to cleanup revision: " << e.what() << std::endl;
            }
        }
        created_revisions.clear();

        for (auto it = created_items.rbegin(); it != created_items.rend(); ++it) {
            try {
                std::cout << "Deleting item: " << (*it)->getKref().uri() << std::endl;
                (*it)->deleteItem(true);
                std::cout << "Successfully deleted item" << std::endl;
            } catch (const std::exception& e) {
                std::cout << "ERROR: Failed to cleanup item: " << e.what() << std::endl;
            }
        }
        created_items.clear();

        for (auto it = created_spaces.rbegin(); it != created_spaces.rend(); ++it) {
            try {
                std::cout << "Deleting space: " << (*it)->getPath() << std::endl;
                (*it)->deleteSpace(true);
                std::cout << "Successfully deleted space" << std::endl;
            } catch (const std::exception& e) {
                std::cout << "ERROR: Failed to cleanup space: " << e.what() << std::endl;
            }
        }
        created_spaces.clear();

        for (auto it = created_projects.rbegin(); it != created_projects.rend(); ++it) {
            try {
                std::cout << "Deleting project: " << (*it)->getName() << std::endl;
                (*it)->deleteProject(true);
                std::cout << "Successfully deleted project" << std::endl;
            } catch (const std::exception& e) {
                std::cout << "ERROR: Failed to cleanup project: " << e.what() << std::endl;
            }
        }
        created_projects.clear();
        
        std::cout << "TearDown: Cleanup completed" << std::endl;
    }

    std::unique_ptr<kumiho::api::Client> client;
    std::vector<std::shared_ptr<kumiho::api::Project>> created_projects;
    std::vector<std::shared_ptr<kumiho::api::Space>> created_spaces;
    std::vector<std::shared_ptr<kumiho::api::Item>> created_items;
    std::vector<std::shared_ptr<kumiho::api::Revision>> created_revisions;
    std::vector<std::shared_ptr<kumiho::api::Artifact>> created_artifacts;
};


// --- Integration Tests ---
TEST_F(KumihoApiTest, FullCreationWorkflow) {
    std::string project_name = unique_name("smoke_test_project");
    std::string asset_name = unique_name("smoke_test_asset");

    auto project = client->createProject(project_name);
    created_projects.push_back(project);

    auto space = project->createSpace("main");
    ASSERT_NE(space, nullptr);
    EXPECT_EQ(space->getPath(), "/" + project_name + "/main");
    created_spaces.push_back(space);

    auto item = space->createItem(asset_name, "model");
    ASSERT_NE(item, nullptr);
    EXPECT_EQ(item->getKref().uri(), "kref://" + project_name + "/main/" + asset_name + ".model");
    created_items.push_back(item);

    auto revision = item->createRevision();
    ASSERT_NE(revision, nullptr);
    EXPECT_TRUE(revision->getKref().uri().find("?r=1") != std::string::npos);
    created_revisions.push_back(revision);

    auto artifact = revision->createArtifact("data", "/path/to/smoke_test.dat");
    ASSERT_NE(artifact, nullptr);
    EXPECT_TRUE(artifact->getKref().uri().find("&a=data") != std::string::npos);
    EXPECT_EQ(artifact->getLocation(), "/path/to/smoke_test.dat");
    created_artifacts.push_back(artifact);
}

TEST_F(KumihoApiTest, RevisionByTagAndTime) {
    // Tests getting revisions by tag, by time, and by combined tag+time.
    // The combined tag+time query is essential for reproducible builds:
    // "What was the published version of this asset on June 1st?"
    
    std::string project_name = unique_name("tag_time_test_project");
    std::string asset_name = unique_name("tag_time_test_asset");

    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem(asset_name, "item");
    created_items.push_back(item);
    auto revision1 = item->createRevision();
    created_revisions.push_back(revision1);
    auto revision2 = item->createRevision();
    created_revisions.push_back(revision2);

    // Tag revision1 with a custom tag
    revision1->tag("hello");
    
    // Tag revision1 as published (simulating a milestone)
    revision1->tag("published");
    
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // Capture the time after tagging revision1 (ISO 8601 format)
    auto now = std::chrono::system_clock::now();
    auto time_t_now = std::chrono::system_clock::to_time_t(now);
    std::tm tm_now;
#ifdef _WIN32
    gmtime_s(&tm_now, &time_t_now);
#else
    gmtime_r(&time_t_now, &tm_now);
#endif
    std::ostringstream time_after_tag1_ss;
    time_after_tag1_ss << std::put_time(&tm_now, "%Y-%m-%dT%H:%M:%SZ");
    std::string time_after_tag1 = time_after_tag1_ss.str();

    // Test: get revision by tag
    auto tag_revision = item->getRevisionByTag("hello");
    ASSERT_NE(tag_revision, nullptr);
    EXPECT_EQ(tag_revision->getRevisionNumber(), revision1->getRevisionNumber());

    // Test: get revision by time only
    auto time_revision = item->getRevisionByTime(*revision1->getCreatedAt());
    ASSERT_NE(time_revision, nullptr);
    
    // Test: get revision by combined tag+time
    // This answers: "What was the published version at this point in time?"
    auto published_at_time = item->getRevisionByTagAndTime("published", time_after_tag1);
    ASSERT_NE(published_at_time, nullptr);
    EXPECT_EQ(published_at_time->getRevisionNumber(), revision1->getRevisionNumber());
    
    // Small delay to ensure timestamps are distinguishable
    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    // Now tag revision2 as published (superseding revision1)
    revision2->tag("published");

    std::this_thread::sleep_for(std::chrono::seconds(1));
    
    // Query for published at time_after_tag1 should still return revision1
    // (because at that time, revision1 was the published one)
    auto historical_published = item->getRevisionByTagAndTime("published", time_after_tag1);
    ASSERT_NE(historical_published, nullptr);
    EXPECT_EQ(historical_published->getRevisionNumber(), revision1->getRevisionNumber());
    
    // Query for published NOW should return revision2
    auto now2 = std::chrono::system_clock::now();
    auto current_published = item->getRevisionByTagAndTime("published", now2);
    ASSERT_NE(current_published, nullptr);
    EXPECT_EQ(current_published->getRevisionNumber(), revision2->getRevisionNumber());
}

TEST_F(KumihoApiTest, GetArtifactsByLocation) {
    std::string project_name = unique_name("loc_test_project");
    std::string asset_name = unique_name("loc_test_asset");
    std::string shared_location = "/mnt/data/test_data/" + unique_name("loc_test") + ".vdb";

    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem(asset_name, "model");
    created_items.push_back(item);
    auto v1 = item->createRevision();
    created_revisions.push_back(v1);
    std::this_thread::sleep_for(std::chrono::seconds(1));
    auto v2 = item->createRevision();
    created_revisions.push_back(v2);

    auto res1 = v1->createArtifact("model_data", shared_location);
    created_artifacts.push_back(res1);
    auto res2 = v2->createArtifact("model_data", shared_location);
    created_artifacts.push_back(res2);

    auto found_artifacts = client->getArtifactsByLocation(shared_location);
    ASSERT_GE(found_artifacts.size(), 2);

    auto newest_res = found_artifacts[0].get();
    auto oldest_res = found_artifacts[1].get();

    EXPECT_EQ(newest_res->getKref(), res2->getKref());
    EXPECT_EQ(newest_res->getRevisionKref(), v2->getKref());
    EXPECT_EQ(newest_res->getItemKref(), item->getKref());

    EXPECT_EQ(oldest_res->getKref(), res1->getKref());
    EXPECT_EQ(oldest_res->getRevisionKref(), v1->getKref());
    EXPECT_EQ(oldest_res->getItemKref(), item->getKref());
}

TEST_F(KumihoApiTest, EdgeWorkflow) {
    std::string project_name = unique_name("edge_proj");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    
    auto model_item = space->createItem("character_model", "model");
    created_items.push_back(model_item);
    auto texture_item = space->createItem("character_textures", "texture");
    created_items.push_back(texture_item);

    auto model_v1 = model_item->createRevision();
    created_revisions.push_back(model_v1);
    auto texture_v1 = texture_item->createRevision();
    created_revisions.push_back(texture_v1);

    auto edge = client->createEdge(texture_v1->getKref(), model_v1->getKref(), "TEXTURE_FOR");
    ASSERT_NE(edge, nullptr);
    EXPECT_EQ(edge->getSourceKref(), texture_v1->getKref());
    EXPECT_EQ(edge->getTargetKref(), model_v1->getKref());
    
    auto source_edges = client->getEdges(texture_v1->getKref());
    ASSERT_GE(source_edges.size(), 1);
    EXPECT_EQ(source_edges[0]->getTargetKref(), model_v1->getKref());
    EXPECT_EQ(source_edges[0]->getEdgeType(), "TEXTURE_FOR");
}

TEST_F(KumihoApiTest, PeekNextRevision) {
    std::string project_name = unique_name("peek_test_project");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem(unique_name("peek_test_asset"), "rig");
    created_items.push_back(item);

    EXPECT_EQ(item->peekNextRevision(), 1);
    auto v1 = item->createRevision();
    created_revisions.push_back(v1);
    EXPECT_EQ(v1->getRevisionNumber(), 1);
    EXPECT_EQ(item->peekNextRevision(), 2);
    auto v2 = item->createRevision();
    created_revisions.push_back(v2);
    EXPECT_EQ(v2->getRevisionNumber(), 2);
    EXPECT_EQ(item->peekNextRevision(), 3);
}

TEST_F(KumihoApiTest, MetadataUpdateWorkflow) {
    std::string project_name = unique_name("meta_proj");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem(unique_name("asset"), "model");
    created_items.push_back(item);
    auto revision = item->createRevision();
    created_revisions.push_back(revision);
    auto artifact = revision->createArtifact("geo", "/path/to/file.abc");
    created_artifacts.push_back(artifact);

    // auto updated_space = space->setMetadata({{"status", "active"}});
    auto updated_item = item->setMetadata({{"pipeline_step", "modeling"}});
    auto updated_revision = revision->setMetadata({{"approved_by", "lead"}});
    auto updated_artifact = artifact->setMetadata({{"format", "alembic"}});

    // ASSERT_EQ(updated_space->getMetadata().at("status"), "active");
    ASSERT_EQ(updated_item->getMetadata().at("pipeline_step"), "modeling");
    ASSERT_EQ(updated_revision->getMetadata().at("approved_by"), "lead");
    ASSERT_EQ(updated_artifact->getMetadata().at("format"), "alembic");
}

TEST_F(KumihoApiTest, SpaceDeletionLogic) {
    auto project = client->createProject(unique_name("del_logic_proj"));
    created_projects.push_back(project);

    auto proj = project->createSpace("del_proj");
    auto item = proj->createItem("asset", "model");
    auto empty_space = project->createSpace("del_empty");

    // 1. Fail to delete non-empty space without force
    EXPECT_THROW(proj->deleteSpace(), std::runtime_error);

    // 2. Succeed in deleting non-empty space with force
    EXPECT_NO_THROW(proj->deleteSpace(true));
    EXPECT_THROW(client->getSpace(proj->getPath()), std::runtime_error);

    // 3. Succeed in deleting empty space without force
    EXPECT_NO_THROW(empty_space->deleteSpace());
    EXPECT_THROW(client->getSpace(empty_space->getPath()), std::runtime_error);
}

TEST_F(KumihoApiTest, ItemDeprecationAndDeletion) {
    std::string project_name = unique_name("dep_proj");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem("char", "rig");
    created_items.push_back(item);
    
    // 1. Deprecate the item (soft delete)
    item->deleteItem();
    auto item_reloaded = space->getItem("char", "rig");
    ASSERT_TRUE(item_reloaded->isDeprecated());
    
    // 2. Re-creating it should un-deprecate it
    auto item_new = space->createItem("char", "rig");
    created_items.push_back(item_new);
    ASSERT_FALSE(item_new->isDeprecated());
    
    // 3. Hard-delete with force
    item_new->deleteItem(true);
    
    // 4. Verify it's gone
    EXPECT_THROW(space->getItem("char", "rig"), std::runtime_error);
}


TEST_F(KumihoApiTest, RevisionTaggingWorkflow) {
    std::string project_name = unique_name("tag_proj");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem("fx", "cache");
    created_items.push_back(item);
    auto v1 = item->createRevision();
    created_revisions.push_back(v1);

    ASSERT_FALSE(v1->hasTag("approved"));
    
    v1->tag("approved");
    ASSERT_TRUE(v1->hasTag("approved"));
    ASSERT_TRUE(v1->wasTagged("approved"));

    v1->untag("approved");
    ASSERT_FALSE(v1->hasTag("approved"));
    ASSERT_TRUE(v1->wasTagged("approved"));
}

TEST_F(KumihoApiTest, PublishedRevisionImmutability) {
    std::string project_name = unique_name("immutable_proj");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem("shot", "comp");
    created_items.push_back(item);
    auto v1 = item->createRevision();
    created_revisions.push_back(v1);
    auto res = v1->createArtifact("main", "/path/to/exr_seq");
    created_artifacts.push_back(res);

    v1->tag(PUBLISHED_TAG);
    auto v1_reloaded = item->getRevision(1);
    ASSERT_TRUE(v1_reloaded->isPublished());

    EXPECT_THROW(v1->setMetadata({{"new_key", "new_val"}}), std::runtime_error);
    EXPECT_THROW(res->setMetadata({{"new_key", "new_val"}}), std::runtime_error);
    EXPECT_THROW(v1->untag(PUBLISHED_TAG), std::runtime_error);
    EXPECT_THROW(v1->deleteRevision(), std::runtime_error);
    EXPECT_THROW(res->deleteArtifact(), std::runtime_error);
    EXPECT_THROW(v1->createArtifact("mask", "/path/to/mask.png"), std::runtime_error);
}

TEST_F(KumihoApiTest, GetArtifactAndLocations) {
    std::string project_name = unique_name("res_proj");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem("set", "env");
    created_items.push_back(item);
    auto v = item->createRevision();
    created_revisions.push_back(v);
    auto res1 = v->createArtifact("hdri", "/loc/hdri.exr");
    created_artifacts.push_back(res1);
    auto res2 = v->createArtifact("lidar", "/loc/lidar.obj");
    created_artifacts.push_back(res2);

    auto artifacts = v->getArtifacts();
    ASSERT_EQ(artifacts.size(), 2);
    
    auto lidar_res = v->getArtifact("lidar");
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

TEST_F(KumihoApiTest, GetItemByKref) {
    std::string project_name = unique_name("kref_test_project");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem(unique_name("kref_test_asset"), "model");
    created_items.push_back(item);
    
    // Test getting item by kref
    auto retrieved_item = client->getItemByKref(item->getKref().uri());
    ASSERT_NE(retrieved_item, nullptr);
    EXPECT_EQ(retrieved_item->getKref().uri(), item->getKref().uri());
}

TEST_F(KumihoApiTest, GetLatestRevision) {
    std::string project_name = unique_name("latest_test_project");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    auto space = project->createSpace("main");
    created_spaces.push_back(space);
    auto item = space->createItem(unique_name("latest_test_asset"), "model");
    created_items.push_back(item);
    
    // Create multiple revisions
    auto v1 = item->createRevision();
    created_revisions.push_back(v1);
    auto v2 = item->createRevision();
    created_revisions.push_back(v2);
    auto v3 = item->createRevision();
    created_revisions.push_back(v3);
    
    // Debug: Check all revisions
    auto all_revisions = item->getRevisions();
    std::cout << "Total revisions: " << all_revisions.size() << std::endl;
    for (const auto& v : all_revisions) {
        std::cout << "Revision " << v->getRevisionNumber() << ": " << v->getKref().uri() 
                  << " latest=" << v->isLatest() << " tags=[";
        auto tags = v->getTags();
        for (size_t i = 0; i < tags.size(); ++i) {
            std::cout << tags[i];
            if (i < tags.size() - 1) std::cout << ",";
        }
        std::cout << "]" << std::endl;
    }
    
    // Test getting latest revision
    auto latest = item->getLatestRevision();
    ASSERT_NE(latest, nullptr);
    std::cout << "Latest revision: " << latest->getRevisionNumber() << " kref: " << latest->getKref().uri() << std::endl;
    
    // The latest revision should be v3
    EXPECT_EQ(latest->getRevisionNumber(), 3);
    EXPECT_EQ(latest->getKref().uri(), v3->getKref().uri());
}

// Test navigation methods
TEST_F(KumihoApiTest, NavigationMethods) {
    // Create a space
    std::string project_name = unique_name("test_nav");
    auto project = client->createProject(project_name);
    created_projects.push_back(project);
    
    std::cout << "Created project: " << project->getName() << std::endl;

    auto space = project->createSpace("main");
    ASSERT_NE(space, nullptr);
    std::cout << "Created space: " << space->getPath() << std::endl;
    
    // Create an item in the space
    auto item = space->createItem("test_item", "model");
    ASSERT_NE(item, nullptr);
    
    // Create a revision
    auto revision = item->createRevision();
    ASSERT_NE(revision, nullptr);
    
    // Test Revision::getItem()
    auto item_from_revision = revision->getItem();
    ASSERT_NE(item_from_revision, nullptr);
    EXPECT_EQ(item_from_revision->getKref().uri(), item->getKref().uri());
    
    // Test Revision::getSpace()
    auto space_from_revision = revision->getSpace();
    ASSERT_NE(space_from_revision, nullptr);
    EXPECT_EQ(space_from_revision->getPath(), space->getPath());
    
    // Test Item::getSpace()
    auto space_from_item = item->getSpace();
    ASSERT_NE(space_from_item, nullptr);
    EXPECT_EQ(space_from_item->getPath(), space->getPath());
    
    // Create a subspace to test parent navigation
    auto subspace = space->createSpace("subspace");
    ASSERT_NE(subspace, nullptr);
    std::cout << "Created subspace: " << subspace->getPath() << std::endl;
    
    // Test Space::getParentSpace() for subspace
    std::cout << "Getting parent of subspace..." << std::endl;
    auto parent_of_subspace = subspace->getParentSpace();
    ASSERT_NE(parent_of_subspace, nullptr);
    std::cout << "Parent of subspace: " << parent_of_subspace->getPath() << std::endl;
    EXPECT_EQ(parent_of_subspace->getPath(), space->getPath());
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}