// This is a generated file - do not edit.
//
// Generated from kumiho.proto.

// @dart = 3.3

// ignore_for_file: annotate_overrides, camel_case_types, comment_references
// ignore_for_file: constant_identifier_names
// ignore_for_file: curly_braces_in_flow_control_structures
// ignore_for_file: deprecated_member_use_from_same_package, library_prefixes
// ignore_for_file: non_constant_identifier_names, prefer_relative_imports

import 'dart:async' as $async;
import 'dart:core' as $core;

import 'package:protobuf/protobuf.dart' as $pb;

import 'kumiho.pb.dart' as $0;
import 'kumiho.pbjson.dart';

export 'kumiho.pb.dart';

abstract class KumihoServiceBase extends $pb.GeneratedService {
  $async.Future<$0.ProjectResponse> createProject(
      $pb.ServerContext ctx, $0.CreateProjectRequest request);
  $async.Future<$0.GetProjectsResponse> getProjects(
      $pb.ServerContext ctx, $0.GetProjectsRequest request);
  $async.Future<$0.ProjectResponse> updateProject(
      $pb.ServerContext ctx, $0.UpdateProjectRequest request);
  $async.Future<$0.StatusResponse> deleteProject(
      $pb.ServerContext ctx, $0.DeleteProjectRequest request);
  $async.Future<$0.SpaceResponse> createSpace(
      $pb.ServerContext ctx, $0.CreateSpaceRequest request);
  $async.Future<$0.SpaceResponse> getSpace(
      $pb.ServerContext ctx, $0.GetSpaceRequest request);
  $async.Future<$0.GetChildSpacesResponse> getChildSpaces(
      $pb.ServerContext ctx, $0.GetChildSpacesRequest request);
  $async.Future<$0.StatusResponse> deleteSpace(
      $pb.ServerContext ctx, $0.DeleteSpaceRequest request);
  $async.Future<$0.SpaceResponse> updateSpaceMetadata(
      $pb.ServerContext ctx, $0.UpdateMetadataRequest request);
  $async.Future<$0.ItemResponse> createItem(
      $pb.ServerContext ctx, $0.CreateItemRequest request);
  $async.Future<$0.ItemResponse> getItem(
      $pb.ServerContext ctx, $0.GetItemRequest request);
  $async.Future<$0.GetItemsResponse> getItems(
      $pb.ServerContext ctx, $0.GetItemsRequest request);
  $async.Future<$0.GetItemsResponse> itemSearch(
      $pb.ServerContext ctx, $0.ItemSearchRequest request);
  $async.Future<$0.StatusResponse> deleteItem(
      $pb.ServerContext ctx, $0.DeleteItemRequest request);
  $async.Future<$0.ItemResponse> updateItemMetadata(
      $pb.ServerContext ctx, $0.UpdateMetadataRequest request);
  $async.Future<$0.RevisionResponse> resolveKref(
      $pb.ServerContext ctx, $0.ResolveKrefRequest request);
  $async.Future<$0.ResolveLocationResponse> resolveLocation(
      $pb.ServerContext ctx, $0.ResolveLocationRequest request);
  $async.Future<$0.RevisionResponse> createRevision(
      $pb.ServerContext ctx, $0.CreateRevisionRequest request);
  $async.Future<$0.RevisionResponse> getRevision(
      $pb.ServerContext ctx, $0.KrefRequest request);
  $async.Future<$0.GetRevisionsResponse> getRevisions(
      $pb.ServerContext ctx, $0.GetRevisionsRequest request);
  $async.Future<$0.StatusResponse> deleteRevision(
      $pb.ServerContext ctx, $0.DeleteRevisionRequest request);
  $async.Future<$0.PeekNextRevisionResponse> peekNextRevision(
      $pb.ServerContext ctx, $0.PeekNextRevisionRequest request);
  $async.Future<$0.RevisionResponse> updateRevisionMetadata(
      $pb.ServerContext ctx, $0.UpdateMetadataRequest request);
  $async.Future<$0.StatusResponse> tagRevision(
      $pb.ServerContext ctx, $0.TagRevisionRequest request);
  $async.Future<$0.StatusResponse> unTagRevision(
      $pb.ServerContext ctx, $0.UnTagRevisionRequest request);
  $async.Future<$0.HasTagResponse> hasTag(
      $pb.ServerContext ctx, $0.HasTagRequest request);
  $async.Future<$0.WasTaggedResponse> wasTagged(
      $pb.ServerContext ctx, $0.WasTaggedRequest request);
  $async.Future<$0.StatusResponse> setDefaultArtifact(
      $pb.ServerContext ctx, $0.SetDefaultArtifactRequest request);
  $async.Future<$0.ArtifactResponse> createArtifact(
      $pb.ServerContext ctx, $0.CreateArtifactRequest request);
  $async.Future<$0.ArtifactResponse> getArtifact(
      $pb.ServerContext ctx, $0.GetArtifactRequest request);
  $async.Future<$0.GetArtifactsResponse> getArtifacts(
      $pb.ServerContext ctx, $0.GetArtifactsRequest request);
  $async.Future<$0.GetArtifactsByLocationResponse> getArtifactsByLocation(
      $pb.ServerContext ctx, $0.GetArtifactsByLocationRequest request);
  $async.Future<$0.StatusResponse> deleteArtifact(
      $pb.ServerContext ctx, $0.DeleteArtifactRequest request);
  $async.Future<$0.ArtifactResponse> updateArtifactMetadata(
      $pb.ServerContext ctx, $0.UpdateMetadataRequest request);
  $async.Future<$0.StatusResponse> setAttribute(
      $pb.ServerContext ctx, $0.SetAttributeRequest request);
  $async.Future<$0.GetAttributeResponse> getAttribute(
      $pb.ServerContext ctx, $0.GetAttributeRequest request);
  $async.Future<$0.StatusResponse> deleteAttribute(
      $pb.ServerContext ctx, $0.DeleteAttributeRequest request);
  $async.Future<$0.StatusResponse> createEdge(
      $pb.ServerContext ctx, $0.CreateEdgeRequest request);
  $async.Future<$0.GetEdgesResponse> getEdges(
      $pb.ServerContext ctx, $0.GetEdgesRequest request);
  $async.Future<$0.StatusResponse> deleteEdge(
      $pb.ServerContext ctx, $0.DeleteEdgeRequest request);
  $async.Future<$0.TraverseEdgesResponse> traverseEdges(
      $pb.ServerContext ctx, $0.TraverseEdgesRequest request);
  $async.Future<$0.ShortestPathResponse> findShortestPath(
      $pb.ServerContext ctx, $0.ShortestPathRequest request);
  $async.Future<$0.ImpactAnalysisResponse> analyzeImpact(
      $pb.ServerContext ctx, $0.ImpactAnalysisRequest request);
  $async.Future<$0.ItemResponse> createBundle(
      $pb.ServerContext ctx, $0.CreateBundleRequest request);
  $async.Future<$0.AddBundleMemberResponse> addBundleMember(
      $pb.ServerContext ctx, $0.AddBundleMemberRequest request);
  $async.Future<$0.RemoveBundleMemberResponse> removeBundleMember(
      $pb.ServerContext ctx, $0.RemoveBundleMemberRequest request);
  $async.Future<$0.GetBundleMembersResponse> getBundleMembers(
      $pb.ServerContext ctx, $0.GetBundleMembersRequest request);
  $async.Future<$0.GetBundleHistoryResponse> getBundleHistory(
      $pb.ServerContext ctx, $0.GetBundleHistoryRequest request);
  $async.Future<$0.TenantUsageResponse> getTenantUsage(
      $pb.ServerContext ctx, $0.GetTenantUsageRequest request);
  $async.Future<$0.Event> eventStream(
      $pb.ServerContext ctx, $0.EventStreamRequest request);
  $async.Future<$0.EventCapabilities> getEventCapabilities(
      $pb.ServerContext ctx, $0.GetEventCapabilitiesRequest request);
  $async.Future<$0.StatusResponse> setDeprecated(
      $pb.ServerContext ctx, $0.SetDeprecatedRequest request);

  $pb.GeneratedMessage createRequest($core.String methodName) {
    switch (methodName) {
      case 'CreateProject':
        return $0.CreateProjectRequest();
      case 'GetProjects':
        return $0.GetProjectsRequest();
      case 'UpdateProject':
        return $0.UpdateProjectRequest();
      case 'DeleteProject':
        return $0.DeleteProjectRequest();
      case 'CreateSpace':
        return $0.CreateSpaceRequest();
      case 'GetSpace':
        return $0.GetSpaceRequest();
      case 'GetChildSpaces':
        return $0.GetChildSpacesRequest();
      case 'DeleteSpace':
        return $0.DeleteSpaceRequest();
      case 'UpdateSpaceMetadata':
        return $0.UpdateMetadataRequest();
      case 'CreateItem':
        return $0.CreateItemRequest();
      case 'GetItem':
        return $0.GetItemRequest();
      case 'GetItems':
        return $0.GetItemsRequest();
      case 'ItemSearch':
        return $0.ItemSearchRequest();
      case 'DeleteItem':
        return $0.DeleteItemRequest();
      case 'UpdateItemMetadata':
        return $0.UpdateMetadataRequest();
      case 'ResolveKref':
        return $0.ResolveKrefRequest();
      case 'ResolveLocation':
        return $0.ResolveLocationRequest();
      case 'CreateRevision':
        return $0.CreateRevisionRequest();
      case 'GetRevision':
        return $0.KrefRequest();
      case 'GetRevisions':
        return $0.GetRevisionsRequest();
      case 'DeleteRevision':
        return $0.DeleteRevisionRequest();
      case 'PeekNextRevision':
        return $0.PeekNextRevisionRequest();
      case 'UpdateRevisionMetadata':
        return $0.UpdateMetadataRequest();
      case 'TagRevision':
        return $0.TagRevisionRequest();
      case 'UnTagRevision':
        return $0.UnTagRevisionRequest();
      case 'HasTag':
        return $0.HasTagRequest();
      case 'WasTagged':
        return $0.WasTaggedRequest();
      case 'SetDefaultArtifact':
        return $0.SetDefaultArtifactRequest();
      case 'CreateArtifact':
        return $0.CreateArtifactRequest();
      case 'GetArtifact':
        return $0.GetArtifactRequest();
      case 'GetArtifacts':
        return $0.GetArtifactsRequest();
      case 'GetArtifactsByLocation':
        return $0.GetArtifactsByLocationRequest();
      case 'DeleteArtifact':
        return $0.DeleteArtifactRequest();
      case 'UpdateArtifactMetadata':
        return $0.UpdateMetadataRequest();
      case 'SetAttribute':
        return $0.SetAttributeRequest();
      case 'GetAttribute':
        return $0.GetAttributeRequest();
      case 'DeleteAttribute':
        return $0.DeleteAttributeRequest();
      case 'CreateEdge':
        return $0.CreateEdgeRequest();
      case 'GetEdges':
        return $0.GetEdgesRequest();
      case 'DeleteEdge':
        return $0.DeleteEdgeRequest();
      case 'TraverseEdges':
        return $0.TraverseEdgesRequest();
      case 'FindShortestPath':
        return $0.ShortestPathRequest();
      case 'AnalyzeImpact':
        return $0.ImpactAnalysisRequest();
      case 'CreateBundle':
        return $0.CreateBundleRequest();
      case 'AddBundleMember':
        return $0.AddBundleMemberRequest();
      case 'RemoveBundleMember':
        return $0.RemoveBundleMemberRequest();
      case 'GetBundleMembers':
        return $0.GetBundleMembersRequest();
      case 'GetBundleHistory':
        return $0.GetBundleHistoryRequest();
      case 'GetTenantUsage':
        return $0.GetTenantUsageRequest();
      case 'EventStream':
        return $0.EventStreamRequest();
      case 'GetEventCapabilities':
        return $0.GetEventCapabilitiesRequest();
      case 'SetDeprecated':
        return $0.SetDeprecatedRequest();
      default:
        throw $core.ArgumentError('Unknown method: $methodName');
    }
  }

  $async.Future<$pb.GeneratedMessage> handleCall($pb.ServerContext ctx,
      $core.String methodName, $pb.GeneratedMessage request) {
    switch (methodName) {
      case 'CreateProject':
        return createProject(ctx, request as $0.CreateProjectRequest);
      case 'GetProjects':
        return getProjects(ctx, request as $0.GetProjectsRequest);
      case 'UpdateProject':
        return updateProject(ctx, request as $0.UpdateProjectRequest);
      case 'DeleteProject':
        return deleteProject(ctx, request as $0.DeleteProjectRequest);
      case 'CreateSpace':
        return createSpace(ctx, request as $0.CreateSpaceRequest);
      case 'GetSpace':
        return getSpace(ctx, request as $0.GetSpaceRequest);
      case 'GetChildSpaces':
        return getChildSpaces(ctx, request as $0.GetChildSpacesRequest);
      case 'DeleteSpace':
        return deleteSpace(ctx, request as $0.DeleteSpaceRequest);
      case 'UpdateSpaceMetadata':
        return updateSpaceMetadata(ctx, request as $0.UpdateMetadataRequest);
      case 'CreateItem':
        return createItem(ctx, request as $0.CreateItemRequest);
      case 'GetItem':
        return getItem(ctx, request as $0.GetItemRequest);
      case 'GetItems':
        return getItems(ctx, request as $0.GetItemsRequest);
      case 'ItemSearch':
        return itemSearch(ctx, request as $0.ItemSearchRequest);
      case 'DeleteItem':
        return deleteItem(ctx, request as $0.DeleteItemRequest);
      case 'UpdateItemMetadata':
        return updateItemMetadata(ctx, request as $0.UpdateMetadataRequest);
      case 'ResolveKref':
        return resolveKref(ctx, request as $0.ResolveKrefRequest);
      case 'ResolveLocation':
        return resolveLocation(ctx, request as $0.ResolveLocationRequest);
      case 'CreateRevision':
        return createRevision(ctx, request as $0.CreateRevisionRequest);
      case 'GetRevision':
        return getRevision(ctx, request as $0.KrefRequest);
      case 'GetRevisions':
        return getRevisions(ctx, request as $0.GetRevisionsRequest);
      case 'DeleteRevision':
        return deleteRevision(ctx, request as $0.DeleteRevisionRequest);
      case 'PeekNextRevision':
        return peekNextRevision(ctx, request as $0.PeekNextRevisionRequest);
      case 'UpdateRevisionMetadata':
        return updateRevisionMetadata(ctx, request as $0.UpdateMetadataRequest);
      case 'TagRevision':
        return tagRevision(ctx, request as $0.TagRevisionRequest);
      case 'UnTagRevision':
        return unTagRevision(ctx, request as $0.UnTagRevisionRequest);
      case 'HasTag':
        return hasTag(ctx, request as $0.HasTagRequest);
      case 'WasTagged':
        return wasTagged(ctx, request as $0.WasTaggedRequest);
      case 'SetDefaultArtifact':
        return setDefaultArtifact(ctx, request as $0.SetDefaultArtifactRequest);
      case 'CreateArtifact':
        return createArtifact(ctx, request as $0.CreateArtifactRequest);
      case 'GetArtifact':
        return getArtifact(ctx, request as $0.GetArtifactRequest);
      case 'GetArtifacts':
        return getArtifacts(ctx, request as $0.GetArtifactsRequest);
      case 'GetArtifactsByLocation':
        return getArtifactsByLocation(
            ctx, request as $0.GetArtifactsByLocationRequest);
      case 'DeleteArtifact':
        return deleteArtifact(ctx, request as $0.DeleteArtifactRequest);
      case 'UpdateArtifactMetadata':
        return updateArtifactMetadata(ctx, request as $0.UpdateMetadataRequest);
      case 'SetAttribute':
        return setAttribute(ctx, request as $0.SetAttributeRequest);
      case 'GetAttribute':
        return getAttribute(ctx, request as $0.GetAttributeRequest);
      case 'DeleteAttribute':
        return deleteAttribute(ctx, request as $0.DeleteAttributeRequest);
      case 'CreateEdge':
        return createEdge(ctx, request as $0.CreateEdgeRequest);
      case 'GetEdges':
        return getEdges(ctx, request as $0.GetEdgesRequest);
      case 'DeleteEdge':
        return deleteEdge(ctx, request as $0.DeleteEdgeRequest);
      case 'TraverseEdges':
        return traverseEdges(ctx, request as $0.TraverseEdgesRequest);
      case 'FindShortestPath':
        return findShortestPath(ctx, request as $0.ShortestPathRequest);
      case 'AnalyzeImpact':
        return analyzeImpact(ctx, request as $0.ImpactAnalysisRequest);
      case 'CreateBundle':
        return createBundle(ctx, request as $0.CreateBundleRequest);
      case 'AddBundleMember':
        return addBundleMember(ctx, request as $0.AddBundleMemberRequest);
      case 'RemoveBundleMember':
        return removeBundleMember(ctx, request as $0.RemoveBundleMemberRequest);
      case 'GetBundleMembers':
        return getBundleMembers(ctx, request as $0.GetBundleMembersRequest);
      case 'GetBundleHistory':
        return getBundleHistory(ctx, request as $0.GetBundleHistoryRequest);
      case 'GetTenantUsage':
        return getTenantUsage(ctx, request as $0.GetTenantUsageRequest);
      case 'EventStream':
        return eventStream(ctx, request as $0.EventStreamRequest);
      case 'GetEventCapabilities':
        return getEventCapabilities(
            ctx, request as $0.GetEventCapabilitiesRequest);
      case 'SetDeprecated':
        return setDeprecated(ctx, request as $0.SetDeprecatedRequest);
      default:
        throw $core.ArgumentError('Unknown method: $methodName');
    }
  }

  $core.Map<$core.String, $core.dynamic> get $json => KumihoServiceBase$json;
  $core.Map<$core.String, $core.Map<$core.String, $core.dynamic>>
      get $messageJson => KumihoServiceBase$messageJson;
}
