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

import 'package:grpc/service_api.dart' as $grpc;
import 'package:protobuf/protobuf.dart' as $pb;

import 'kumiho.pb.dart' as $0;

export 'kumiho.pb.dart';

/// The Kumiho service definition.
@$pb.GrpcServiceName('kumiho.KumihoService')
class KumihoServiceClient extends $grpc.Client {
  /// The hostname for this service.
  static const $core.String defaultHost = '';

  /// OAuth scopes needed for the client.
  static const $core.List<$core.String> oauthScopes = [
    '',
  ];

  KumihoServiceClient(super.channel, {super.options, super.interceptors});

  /// Project methods
  $grpc.ResponseFuture<$0.ProjectResponse> createProject(
    $0.CreateProjectRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$createProject, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetProjectsResponse> getProjects(
    $0.GetProjectsRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getProjects, request, options: options);
  }

  $grpc.ResponseFuture<$0.ProjectResponse> updateProject(
    $0.UpdateProjectRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$updateProject, request, options: options);
  }

  $grpc.ResponseFuture<$0.StatusResponse> deleteProject(
    $0.DeleteProjectRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$deleteProject, request, options: options);
  }

  /// Space methods
  $grpc.ResponseFuture<$0.SpaceResponse> createSpace(
    $0.CreateSpaceRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$createSpace, request, options: options);
  }

  $grpc.ResponseFuture<$0.SpaceResponse> getSpace(
    $0.GetSpaceRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getSpace, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetChildSpacesResponse> getChildSpaces(
    $0.GetChildSpacesRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getChildSpaces, request, options: options);
  }

  $grpc.ResponseFuture<$0.StatusResponse> deleteSpace(
    $0.DeleteSpaceRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$deleteSpace, request, options: options);
  }

  $grpc.ResponseFuture<$0.SpaceResponse> updateSpaceMetadata(
    $0.UpdateMetadataRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$updateSpaceMetadata, request, options: options);
  }

  /// Item methods
  $grpc.ResponseFuture<$0.ItemResponse> createItem(
    $0.CreateItemRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$createItem, request, options: options);
  }

  $grpc.ResponseFuture<$0.ItemResponse> getItem(
    $0.GetItemRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getItem, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetItemsResponse> getItems(
    $0.GetItemsRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getItems, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetItemsResponse> itemSearch(
    $0.ItemSearchRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$itemSearch, request, options: options);
  }

  $grpc.ResponseFuture<$0.StatusResponse> deleteItem(
    $0.DeleteItemRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$deleteItem, request, options: options);
  }

  $grpc.ResponseFuture<$0.ItemResponse> updateItemMetadata(
    $0.UpdateMetadataRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$updateItemMetadata, request, options: options);
  }

  /// Revision methods
  $grpc.ResponseFuture<$0.RevisionResponse> resolveKref(
    $0.ResolveKrefRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$resolveKref, request, options: options);
  }

  $grpc.ResponseFuture<$0.ResolveLocationResponse> resolveLocation(
    $0.ResolveLocationRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$resolveLocation, request, options: options);
  }

  $grpc.ResponseFuture<$0.RevisionResponse> createRevision(
    $0.CreateRevisionRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$createRevision, request, options: options);
  }

  $grpc.ResponseFuture<$0.RevisionResponse> getRevision(
    $0.KrefRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getRevision, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetRevisionsResponse> getRevisions(
    $0.GetRevisionsRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getRevisions, request, options: options);
  }

  $grpc.ResponseFuture<$0.StatusResponse> deleteRevision(
    $0.DeleteRevisionRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$deleteRevision, request, options: options);
  }

  $grpc.ResponseFuture<$0.PeekNextRevisionResponse> peekNextRevision(
    $0.PeekNextRevisionRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$peekNextRevision, request, options: options);
  }

  $grpc.ResponseFuture<$0.RevisionResponse> updateRevisionMetadata(
    $0.UpdateMetadataRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$updateRevisionMetadata, request,
        options: options);
  }

  $grpc.ResponseFuture<$0.StatusResponse> tagRevision(
    $0.TagRevisionRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$tagRevision, request, options: options);
  }

  $grpc.ResponseFuture<$0.StatusResponse> unTagRevision(
    $0.UnTagRevisionRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$unTagRevision, request, options: options);
  }

  $grpc.ResponseFuture<$0.HasTagResponse> hasTag(
    $0.HasTagRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$hasTag, request, options: options);
  }

  $grpc.ResponseFuture<$0.WasTaggedResponse> wasTagged(
    $0.WasTaggedRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$wasTagged, request, options: options);
  }

  $grpc.ResponseFuture<$0.StatusResponse> setDefaultArtifact(
    $0.SetDefaultArtifactRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$setDefaultArtifact, request, options: options);
  }

  /// Artifact methods
  $grpc.ResponseFuture<$0.ArtifactResponse> createArtifact(
    $0.CreateArtifactRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$createArtifact, request, options: options);
  }

  $grpc.ResponseFuture<$0.ArtifactResponse> getArtifact(
    $0.GetArtifactRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getArtifact, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetArtifactsResponse> getArtifacts(
    $0.GetArtifactsRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getArtifacts, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetArtifactsByLocationResponse>
      getArtifactsByLocation(
    $0.GetArtifactsByLocationRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getArtifactsByLocation, request,
        options: options);
  }

  $grpc.ResponseFuture<$0.StatusResponse> deleteArtifact(
    $0.DeleteArtifactRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$deleteArtifact, request, options: options);
  }

  $grpc.ResponseFuture<$0.ArtifactResponse> updateArtifactMetadata(
    $0.UpdateMetadataRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$updateArtifactMetadata, request,
        options: options);
  }

  /// Attribute methods (granular metadata operations)
  /// These work on any entity type (Revision, Item, Artifact, Space) identified by kref
  $grpc.ResponseFuture<$0.StatusResponse> setAttribute(
    $0.SetAttributeRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$setAttribute, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetAttributeResponse> getAttribute(
    $0.GetAttributeRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getAttribute, request, options: options);
  }

  $grpc.ResponseFuture<$0.StatusResponse> deleteAttribute(
    $0.DeleteAttributeRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$deleteAttribute, request, options: options);
  }

  /// Edge methods
  $grpc.ResponseFuture<$0.StatusResponse> createEdge(
    $0.CreateEdgeRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$createEdge, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetEdgesResponse> getEdges(
    $0.GetEdgesRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getEdges, request, options: options);
  }

  $grpc.ResponseFuture<$0.StatusResponse> deleteEdge(
    $0.DeleteEdgeRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$deleteEdge, request, options: options);
  }

  /// Graph Traversal methods
  $grpc.ResponseFuture<$0.TraverseEdgesResponse> traverseEdges(
    $0.TraverseEdgesRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$traverseEdges, request, options: options);
  }

  $grpc.ResponseFuture<$0.ShortestPathResponse> findShortestPath(
    $0.ShortestPathRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$findShortestPath, request, options: options);
  }

  $grpc.ResponseFuture<$0.ImpactAnalysisResponse> analyzeImpact(
    $0.ImpactAnalysisRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$analyzeImpact, request, options: options);
  }

  /// Bundle methods
  $grpc.ResponseFuture<$0.ItemResponse> createBundle(
    $0.CreateBundleRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$createBundle, request, options: options);
  }

  $grpc.ResponseFuture<$0.AddBundleMemberResponse> addBundleMember(
    $0.AddBundleMemberRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$addBundleMember, request, options: options);
  }

  $grpc.ResponseFuture<$0.RemoveBundleMemberResponse> removeBundleMember(
    $0.RemoveBundleMemberRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$removeBundleMember, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetBundleMembersResponse> getBundleMembers(
    $0.GetBundleMembersRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getBundleMembers, request, options: options);
  }

  $grpc.ResponseFuture<$0.GetBundleHistoryResponse> getBundleHistory(
    $0.GetBundleHistoryRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getBundleHistory, request, options: options);
  }

  /// Tenant methods
  $grpc.ResponseFuture<$0.TenantUsageResponse> getTenantUsage(
    $0.GetTenantUsageRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getTenantUsage, request, options: options);
  }

  /// Event Streaming
  $grpc.ResponseStream<$0.Event> eventStream(
    $0.EventStreamRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createStreamingCall(
        _$eventStream, $async.Stream.fromIterable([request]),
        options: options);
  }

  /// Get event streaming capabilities for the authenticated tenant's tier
  $grpc.ResponseFuture<$0.EventCapabilities> getEventCapabilities(
    $0.GetEventCapabilitiesRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$getEventCapabilities, request, options: options);
  }

  /// Deprecation methods
  $grpc.ResponseFuture<$0.StatusResponse> setDeprecated(
    $0.SetDeprecatedRequest request, {
    $grpc.CallOptions? options,
  }) {
    return $createUnaryCall(_$setDeprecated, request, options: options);
  }

  // method descriptors

  static final _$createProject =
      $grpc.ClientMethod<$0.CreateProjectRequest, $0.ProjectResponse>(
          '/kumiho.KumihoService/CreateProject',
          ($0.CreateProjectRequest value) => value.writeToBuffer(),
          $0.ProjectResponse.fromBuffer);
  static final _$getProjects =
      $grpc.ClientMethod<$0.GetProjectsRequest, $0.GetProjectsResponse>(
          '/kumiho.KumihoService/GetProjects',
          ($0.GetProjectsRequest value) => value.writeToBuffer(),
          $0.GetProjectsResponse.fromBuffer);
  static final _$updateProject =
      $grpc.ClientMethod<$0.UpdateProjectRequest, $0.ProjectResponse>(
          '/kumiho.KumihoService/UpdateProject',
          ($0.UpdateProjectRequest value) => value.writeToBuffer(),
          $0.ProjectResponse.fromBuffer);
  static final _$deleteProject =
      $grpc.ClientMethod<$0.DeleteProjectRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/DeleteProject',
          ($0.DeleteProjectRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$createSpace =
      $grpc.ClientMethod<$0.CreateSpaceRequest, $0.SpaceResponse>(
          '/kumiho.KumihoService/CreateSpace',
          ($0.CreateSpaceRequest value) => value.writeToBuffer(),
          $0.SpaceResponse.fromBuffer);
  static final _$getSpace =
      $grpc.ClientMethod<$0.GetSpaceRequest, $0.SpaceResponse>(
          '/kumiho.KumihoService/GetSpace',
          ($0.GetSpaceRequest value) => value.writeToBuffer(),
          $0.SpaceResponse.fromBuffer);
  static final _$getChildSpaces =
      $grpc.ClientMethod<$0.GetChildSpacesRequest, $0.GetChildSpacesResponse>(
          '/kumiho.KumihoService/GetChildSpaces',
          ($0.GetChildSpacesRequest value) => value.writeToBuffer(),
          $0.GetChildSpacesResponse.fromBuffer);
  static final _$deleteSpace =
      $grpc.ClientMethod<$0.DeleteSpaceRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/DeleteSpace',
          ($0.DeleteSpaceRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$updateSpaceMetadata =
      $grpc.ClientMethod<$0.UpdateMetadataRequest, $0.SpaceResponse>(
          '/kumiho.KumihoService/UpdateSpaceMetadata',
          ($0.UpdateMetadataRequest value) => value.writeToBuffer(),
          $0.SpaceResponse.fromBuffer);
  static final _$createItem =
      $grpc.ClientMethod<$0.CreateItemRequest, $0.ItemResponse>(
          '/kumiho.KumihoService/CreateItem',
          ($0.CreateItemRequest value) => value.writeToBuffer(),
          $0.ItemResponse.fromBuffer);
  static final _$getItem =
      $grpc.ClientMethod<$0.GetItemRequest, $0.ItemResponse>(
          '/kumiho.KumihoService/GetItem',
          ($0.GetItemRequest value) => value.writeToBuffer(),
          $0.ItemResponse.fromBuffer);
  static final _$getItems =
      $grpc.ClientMethod<$0.GetItemsRequest, $0.GetItemsResponse>(
          '/kumiho.KumihoService/GetItems',
          ($0.GetItemsRequest value) => value.writeToBuffer(),
          $0.GetItemsResponse.fromBuffer);
  static final _$itemSearch =
      $grpc.ClientMethod<$0.ItemSearchRequest, $0.GetItemsResponse>(
          '/kumiho.KumihoService/ItemSearch',
          ($0.ItemSearchRequest value) => value.writeToBuffer(),
          $0.GetItemsResponse.fromBuffer);
  static final _$deleteItem =
      $grpc.ClientMethod<$0.DeleteItemRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/DeleteItem',
          ($0.DeleteItemRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$updateItemMetadata =
      $grpc.ClientMethod<$0.UpdateMetadataRequest, $0.ItemResponse>(
          '/kumiho.KumihoService/UpdateItemMetadata',
          ($0.UpdateMetadataRequest value) => value.writeToBuffer(),
          $0.ItemResponse.fromBuffer);
  static final _$resolveKref =
      $grpc.ClientMethod<$0.ResolveKrefRequest, $0.RevisionResponse>(
          '/kumiho.KumihoService/ResolveKref',
          ($0.ResolveKrefRequest value) => value.writeToBuffer(),
          $0.RevisionResponse.fromBuffer);
  static final _$resolveLocation =
      $grpc.ClientMethod<$0.ResolveLocationRequest, $0.ResolveLocationResponse>(
          '/kumiho.KumihoService/ResolveLocation',
          ($0.ResolveLocationRequest value) => value.writeToBuffer(),
          $0.ResolveLocationResponse.fromBuffer);
  static final _$createRevision =
      $grpc.ClientMethod<$0.CreateRevisionRequest, $0.RevisionResponse>(
          '/kumiho.KumihoService/CreateRevision',
          ($0.CreateRevisionRequest value) => value.writeToBuffer(),
          $0.RevisionResponse.fromBuffer);
  static final _$getRevision =
      $grpc.ClientMethod<$0.KrefRequest, $0.RevisionResponse>(
          '/kumiho.KumihoService/GetRevision',
          ($0.KrefRequest value) => value.writeToBuffer(),
          $0.RevisionResponse.fromBuffer);
  static final _$getRevisions =
      $grpc.ClientMethod<$0.GetRevisionsRequest, $0.GetRevisionsResponse>(
          '/kumiho.KumihoService/GetRevisions',
          ($0.GetRevisionsRequest value) => value.writeToBuffer(),
          $0.GetRevisionsResponse.fromBuffer);
  static final _$deleteRevision =
      $grpc.ClientMethod<$0.DeleteRevisionRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/DeleteRevision',
          ($0.DeleteRevisionRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$peekNextRevision = $grpc.ClientMethod<
          $0.PeekNextRevisionRequest, $0.PeekNextRevisionResponse>(
      '/kumiho.KumihoService/PeekNextRevision',
      ($0.PeekNextRevisionRequest value) => value.writeToBuffer(),
      $0.PeekNextRevisionResponse.fromBuffer);
  static final _$updateRevisionMetadata =
      $grpc.ClientMethod<$0.UpdateMetadataRequest, $0.RevisionResponse>(
          '/kumiho.KumihoService/UpdateRevisionMetadata',
          ($0.UpdateMetadataRequest value) => value.writeToBuffer(),
          $0.RevisionResponse.fromBuffer);
  static final _$tagRevision =
      $grpc.ClientMethod<$0.TagRevisionRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/TagRevision',
          ($0.TagRevisionRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$unTagRevision =
      $grpc.ClientMethod<$0.UnTagRevisionRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/UnTagRevision',
          ($0.UnTagRevisionRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$hasTag =
      $grpc.ClientMethod<$0.HasTagRequest, $0.HasTagResponse>(
          '/kumiho.KumihoService/HasTag',
          ($0.HasTagRequest value) => value.writeToBuffer(),
          $0.HasTagResponse.fromBuffer);
  static final _$wasTagged =
      $grpc.ClientMethod<$0.WasTaggedRequest, $0.WasTaggedResponse>(
          '/kumiho.KumihoService/WasTagged',
          ($0.WasTaggedRequest value) => value.writeToBuffer(),
          $0.WasTaggedResponse.fromBuffer);
  static final _$setDefaultArtifact =
      $grpc.ClientMethod<$0.SetDefaultArtifactRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/SetDefaultArtifact',
          ($0.SetDefaultArtifactRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$createArtifact =
      $grpc.ClientMethod<$0.CreateArtifactRequest, $0.ArtifactResponse>(
          '/kumiho.KumihoService/CreateArtifact',
          ($0.CreateArtifactRequest value) => value.writeToBuffer(),
          $0.ArtifactResponse.fromBuffer);
  static final _$getArtifact =
      $grpc.ClientMethod<$0.GetArtifactRequest, $0.ArtifactResponse>(
          '/kumiho.KumihoService/GetArtifact',
          ($0.GetArtifactRequest value) => value.writeToBuffer(),
          $0.ArtifactResponse.fromBuffer);
  static final _$getArtifacts =
      $grpc.ClientMethod<$0.GetArtifactsRequest, $0.GetArtifactsResponse>(
          '/kumiho.KumihoService/GetArtifacts',
          ($0.GetArtifactsRequest value) => value.writeToBuffer(),
          $0.GetArtifactsResponse.fromBuffer);
  static final _$getArtifactsByLocation = $grpc.ClientMethod<
          $0.GetArtifactsByLocationRequest, $0.GetArtifactsByLocationResponse>(
      '/kumiho.KumihoService/GetArtifactsByLocation',
      ($0.GetArtifactsByLocationRequest value) => value.writeToBuffer(),
      $0.GetArtifactsByLocationResponse.fromBuffer);
  static final _$deleteArtifact =
      $grpc.ClientMethod<$0.DeleteArtifactRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/DeleteArtifact',
          ($0.DeleteArtifactRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$updateArtifactMetadata =
      $grpc.ClientMethod<$0.UpdateMetadataRequest, $0.ArtifactResponse>(
          '/kumiho.KumihoService/UpdateArtifactMetadata',
          ($0.UpdateMetadataRequest value) => value.writeToBuffer(),
          $0.ArtifactResponse.fromBuffer);
  static final _$setAttribute =
      $grpc.ClientMethod<$0.SetAttributeRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/SetAttribute',
          ($0.SetAttributeRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$getAttribute =
      $grpc.ClientMethod<$0.GetAttributeRequest, $0.GetAttributeResponse>(
          '/kumiho.KumihoService/GetAttribute',
          ($0.GetAttributeRequest value) => value.writeToBuffer(),
          $0.GetAttributeResponse.fromBuffer);
  static final _$deleteAttribute =
      $grpc.ClientMethod<$0.DeleteAttributeRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/DeleteAttribute',
          ($0.DeleteAttributeRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$createEdge =
      $grpc.ClientMethod<$0.CreateEdgeRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/CreateEdge',
          ($0.CreateEdgeRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$getEdges =
      $grpc.ClientMethod<$0.GetEdgesRequest, $0.GetEdgesResponse>(
          '/kumiho.KumihoService/GetEdges',
          ($0.GetEdgesRequest value) => value.writeToBuffer(),
          $0.GetEdgesResponse.fromBuffer);
  static final _$deleteEdge =
      $grpc.ClientMethod<$0.DeleteEdgeRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/DeleteEdge',
          ($0.DeleteEdgeRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
  static final _$traverseEdges =
      $grpc.ClientMethod<$0.TraverseEdgesRequest, $0.TraverseEdgesResponse>(
          '/kumiho.KumihoService/TraverseEdges',
          ($0.TraverseEdgesRequest value) => value.writeToBuffer(),
          $0.TraverseEdgesResponse.fromBuffer);
  static final _$findShortestPath =
      $grpc.ClientMethod<$0.ShortestPathRequest, $0.ShortestPathResponse>(
          '/kumiho.KumihoService/FindShortestPath',
          ($0.ShortestPathRequest value) => value.writeToBuffer(),
          $0.ShortestPathResponse.fromBuffer);
  static final _$analyzeImpact =
      $grpc.ClientMethod<$0.ImpactAnalysisRequest, $0.ImpactAnalysisResponse>(
          '/kumiho.KumihoService/AnalyzeImpact',
          ($0.ImpactAnalysisRequest value) => value.writeToBuffer(),
          $0.ImpactAnalysisResponse.fromBuffer);
  static final _$createBundle =
      $grpc.ClientMethod<$0.CreateBundleRequest, $0.ItemResponse>(
          '/kumiho.KumihoService/CreateBundle',
          ($0.CreateBundleRequest value) => value.writeToBuffer(),
          $0.ItemResponse.fromBuffer);
  static final _$addBundleMember =
      $grpc.ClientMethod<$0.AddBundleMemberRequest, $0.AddBundleMemberResponse>(
          '/kumiho.KumihoService/AddBundleMember',
          ($0.AddBundleMemberRequest value) => value.writeToBuffer(),
          $0.AddBundleMemberResponse.fromBuffer);
  static final _$removeBundleMember = $grpc.ClientMethod<
          $0.RemoveBundleMemberRequest, $0.RemoveBundleMemberResponse>(
      '/kumiho.KumihoService/RemoveBundleMember',
      ($0.RemoveBundleMemberRequest value) => value.writeToBuffer(),
      $0.RemoveBundleMemberResponse.fromBuffer);
  static final _$getBundleMembers = $grpc.ClientMethod<
          $0.GetBundleMembersRequest, $0.GetBundleMembersResponse>(
      '/kumiho.KumihoService/GetBundleMembers',
      ($0.GetBundleMembersRequest value) => value.writeToBuffer(),
      $0.GetBundleMembersResponse.fromBuffer);
  static final _$getBundleHistory = $grpc.ClientMethod<
          $0.GetBundleHistoryRequest, $0.GetBundleHistoryResponse>(
      '/kumiho.KumihoService/GetBundleHistory',
      ($0.GetBundleHistoryRequest value) => value.writeToBuffer(),
      $0.GetBundleHistoryResponse.fromBuffer);
  static final _$getTenantUsage =
      $grpc.ClientMethod<$0.GetTenantUsageRequest, $0.TenantUsageResponse>(
          '/kumiho.KumihoService/GetTenantUsage',
          ($0.GetTenantUsageRequest value) => value.writeToBuffer(),
          $0.TenantUsageResponse.fromBuffer);
  static final _$eventStream =
      $grpc.ClientMethod<$0.EventStreamRequest, $0.Event>(
          '/kumiho.KumihoService/EventStream',
          ($0.EventStreamRequest value) => value.writeToBuffer(),
          $0.Event.fromBuffer);
  static final _$getEventCapabilities =
      $grpc.ClientMethod<$0.GetEventCapabilitiesRequest, $0.EventCapabilities>(
          '/kumiho.KumihoService/GetEventCapabilities',
          ($0.GetEventCapabilitiesRequest value) => value.writeToBuffer(),
          $0.EventCapabilities.fromBuffer);
  static final _$setDeprecated =
      $grpc.ClientMethod<$0.SetDeprecatedRequest, $0.StatusResponse>(
          '/kumiho.KumihoService/SetDeprecated',
          ($0.SetDeprecatedRequest value) => value.writeToBuffer(),
          $0.StatusResponse.fromBuffer);
}

@$pb.GrpcServiceName('kumiho.KumihoService')
abstract class KumihoServiceBase extends $grpc.Service {
  $core.String get $name => 'kumiho.KumihoService';

  KumihoServiceBase() {
    $addMethod($grpc.ServiceMethod<$0.CreateProjectRequest, $0.ProjectResponse>(
        'CreateProject',
        createProject_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.CreateProjectRequest.fromBuffer(value),
        ($0.ProjectResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.GetProjectsRequest, $0.GetProjectsResponse>(
            'GetProjects',
            getProjects_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.GetProjectsRequest.fromBuffer(value),
            ($0.GetProjectsResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.UpdateProjectRequest, $0.ProjectResponse>(
        'UpdateProject',
        updateProject_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.UpdateProjectRequest.fromBuffer(value),
        ($0.ProjectResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.DeleteProjectRequest, $0.StatusResponse>(
        'DeleteProject',
        deleteProject_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.DeleteProjectRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.CreateSpaceRequest, $0.SpaceResponse>(
        'CreateSpace',
        createSpace_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.CreateSpaceRequest.fromBuffer(value),
        ($0.SpaceResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.GetSpaceRequest, $0.SpaceResponse>(
        'GetSpace',
        getSpace_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.GetSpaceRequest.fromBuffer(value),
        ($0.SpaceResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.GetChildSpacesRequest,
            $0.GetChildSpacesResponse>(
        'GetChildSpaces',
        getChildSpaces_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.GetChildSpacesRequest.fromBuffer(value),
        ($0.GetChildSpacesResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.DeleteSpaceRequest, $0.StatusResponse>(
        'DeleteSpace',
        deleteSpace_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.DeleteSpaceRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.UpdateMetadataRequest, $0.SpaceResponse>(
        'UpdateSpaceMetadata',
        updateSpaceMetadata_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.UpdateMetadataRequest.fromBuffer(value),
        ($0.SpaceResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.CreateItemRequest, $0.ItemResponse>(
        'CreateItem',
        createItem_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.CreateItemRequest.fromBuffer(value),
        ($0.ItemResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.GetItemRequest, $0.ItemResponse>(
        'GetItem',
        getItem_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.GetItemRequest.fromBuffer(value),
        ($0.ItemResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.GetItemsRequest, $0.GetItemsResponse>(
        'GetItems',
        getItems_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.GetItemsRequest.fromBuffer(value),
        ($0.GetItemsResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.ItemSearchRequest, $0.GetItemsResponse>(
        'ItemSearch',
        itemSearch_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.ItemSearchRequest.fromBuffer(value),
        ($0.GetItemsResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.DeleteItemRequest, $0.StatusResponse>(
        'DeleteItem',
        deleteItem_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.DeleteItemRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.UpdateMetadataRequest, $0.ItemResponse>(
        'UpdateItemMetadata',
        updateItemMetadata_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.UpdateMetadataRequest.fromBuffer(value),
        ($0.ItemResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.ResolveKrefRequest, $0.RevisionResponse>(
        'ResolveKref',
        resolveKref_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.ResolveKrefRequest.fromBuffer(value),
        ($0.RevisionResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.ResolveLocationRequest,
            $0.ResolveLocationResponse>(
        'ResolveLocation',
        resolveLocation_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.ResolveLocationRequest.fromBuffer(value),
        ($0.ResolveLocationResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.CreateRevisionRequest, $0.RevisionResponse>(
            'CreateRevision',
            createRevision_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.CreateRevisionRequest.fromBuffer(value),
            ($0.RevisionResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.KrefRequest, $0.RevisionResponse>(
        'GetRevision',
        getRevision_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.KrefRequest.fromBuffer(value),
        ($0.RevisionResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.GetRevisionsRequest, $0.GetRevisionsResponse>(
            'GetRevisions',
            getRevisions_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.GetRevisionsRequest.fromBuffer(value),
            ($0.GetRevisionsResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.DeleteRevisionRequest, $0.StatusResponse>(
        'DeleteRevision',
        deleteRevision_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.DeleteRevisionRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.PeekNextRevisionRequest,
            $0.PeekNextRevisionResponse>(
        'PeekNextRevision',
        peekNextRevision_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.PeekNextRevisionRequest.fromBuffer(value),
        ($0.PeekNextRevisionResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.UpdateMetadataRequest, $0.RevisionResponse>(
            'UpdateRevisionMetadata',
            updateRevisionMetadata_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.UpdateMetadataRequest.fromBuffer(value),
            ($0.RevisionResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.TagRevisionRequest, $0.StatusResponse>(
        'TagRevision',
        tagRevision_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.TagRevisionRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.UnTagRevisionRequest, $0.StatusResponse>(
        'UnTagRevision',
        unTagRevision_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.UnTagRevisionRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.HasTagRequest, $0.HasTagResponse>(
        'HasTag',
        hasTag_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.HasTagRequest.fromBuffer(value),
        ($0.HasTagResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.WasTaggedRequest, $0.WasTaggedResponse>(
        'WasTagged',
        wasTagged_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.WasTaggedRequest.fromBuffer(value),
        ($0.WasTaggedResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.SetDefaultArtifactRequest, $0.StatusResponse>(
            'SetDefaultArtifact',
            setDefaultArtifact_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.SetDefaultArtifactRequest.fromBuffer(value),
            ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.CreateArtifactRequest, $0.ArtifactResponse>(
            'CreateArtifact',
            createArtifact_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.CreateArtifactRequest.fromBuffer(value),
            ($0.ArtifactResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.GetArtifactRequest, $0.ArtifactResponse>(
        'GetArtifact',
        getArtifact_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.GetArtifactRequest.fromBuffer(value),
        ($0.ArtifactResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.GetArtifactsRequest, $0.GetArtifactsResponse>(
            'GetArtifacts',
            getArtifacts_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.GetArtifactsRequest.fromBuffer(value),
            ($0.GetArtifactsResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.GetArtifactsByLocationRequest,
            $0.GetArtifactsByLocationResponse>(
        'GetArtifactsByLocation',
        getArtifactsByLocation_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.GetArtifactsByLocationRequest.fromBuffer(value),
        ($0.GetArtifactsByLocationResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.DeleteArtifactRequest, $0.StatusResponse>(
        'DeleteArtifact',
        deleteArtifact_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.DeleteArtifactRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.UpdateMetadataRequest, $0.ArtifactResponse>(
            'UpdateArtifactMetadata',
            updateArtifactMetadata_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.UpdateMetadataRequest.fromBuffer(value),
            ($0.ArtifactResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.SetAttributeRequest, $0.StatusResponse>(
        'SetAttribute',
        setAttribute_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.SetAttributeRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.GetAttributeRequest, $0.GetAttributeResponse>(
            'GetAttribute',
            getAttribute_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.GetAttributeRequest.fromBuffer(value),
            ($0.GetAttributeResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.DeleteAttributeRequest, $0.StatusResponse>(
            'DeleteAttribute',
            deleteAttribute_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.DeleteAttributeRequest.fromBuffer(value),
            ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.CreateEdgeRequest, $0.StatusResponse>(
        'CreateEdge',
        createEdge_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.CreateEdgeRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.GetEdgesRequest, $0.GetEdgesResponse>(
        'GetEdges',
        getEdges_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.GetEdgesRequest.fromBuffer(value),
        ($0.GetEdgesResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.DeleteEdgeRequest, $0.StatusResponse>(
        'DeleteEdge',
        deleteEdge_Pre,
        false,
        false,
        ($core.List<$core.int> value) => $0.DeleteEdgeRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.TraverseEdgesRequest, $0.TraverseEdgesResponse>(
            'TraverseEdges',
            traverseEdges_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.TraverseEdgesRequest.fromBuffer(value),
            ($0.TraverseEdgesResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.ShortestPathRequest, $0.ShortestPathResponse>(
            'FindShortestPath',
            findShortestPath_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.ShortestPathRequest.fromBuffer(value),
            ($0.ShortestPathResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.ImpactAnalysisRequest,
            $0.ImpactAnalysisResponse>(
        'AnalyzeImpact',
        analyzeImpact_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.ImpactAnalysisRequest.fromBuffer(value),
        ($0.ImpactAnalysisResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.CreateBundleRequest, $0.ItemResponse>(
        'CreateBundle',
        createBundle_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.CreateBundleRequest.fromBuffer(value),
        ($0.ItemResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.AddBundleMemberRequest,
            $0.AddBundleMemberResponse>(
        'AddBundleMember',
        addBundleMember_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.AddBundleMemberRequest.fromBuffer(value),
        ($0.AddBundleMemberResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.RemoveBundleMemberRequest,
            $0.RemoveBundleMemberResponse>(
        'RemoveBundleMember',
        removeBundleMember_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.RemoveBundleMemberRequest.fromBuffer(value),
        ($0.RemoveBundleMemberResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.GetBundleMembersRequest,
            $0.GetBundleMembersResponse>(
        'GetBundleMembers',
        getBundleMembers_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.GetBundleMembersRequest.fromBuffer(value),
        ($0.GetBundleMembersResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.GetBundleHistoryRequest,
            $0.GetBundleHistoryResponse>(
        'GetBundleHistory',
        getBundleHistory_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.GetBundleHistoryRequest.fromBuffer(value),
        ($0.GetBundleHistoryResponse value) => value.writeToBuffer()));
    $addMethod(
        $grpc.ServiceMethod<$0.GetTenantUsageRequest, $0.TenantUsageResponse>(
            'GetTenantUsage',
            getTenantUsage_Pre,
            false,
            false,
            ($core.List<$core.int> value) =>
                $0.GetTenantUsageRequest.fromBuffer(value),
            ($0.TenantUsageResponse value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.EventStreamRequest, $0.Event>(
        'EventStream',
        eventStream_Pre,
        false,
        true,
        ($core.List<$core.int> value) =>
            $0.EventStreamRequest.fromBuffer(value),
        ($0.Event value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.GetEventCapabilitiesRequest,
            $0.EventCapabilities>(
        'GetEventCapabilities',
        getEventCapabilities_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.GetEventCapabilitiesRequest.fromBuffer(value),
        ($0.EventCapabilities value) => value.writeToBuffer()));
    $addMethod($grpc.ServiceMethod<$0.SetDeprecatedRequest, $0.StatusResponse>(
        'SetDeprecated',
        setDeprecated_Pre,
        false,
        false,
        ($core.List<$core.int> value) =>
            $0.SetDeprecatedRequest.fromBuffer(value),
        ($0.StatusResponse value) => value.writeToBuffer()));
  }

  $async.Future<$0.ProjectResponse> createProject_Pre($grpc.ServiceCall $call,
      $async.Future<$0.CreateProjectRequest> $request) async {
    return createProject($call, await $request);
  }

  $async.Future<$0.ProjectResponse> createProject(
      $grpc.ServiceCall call, $0.CreateProjectRequest request);

  $async.Future<$0.GetProjectsResponse> getProjects_Pre($grpc.ServiceCall $call,
      $async.Future<$0.GetProjectsRequest> $request) async {
    return getProjects($call, await $request);
  }

  $async.Future<$0.GetProjectsResponse> getProjects(
      $grpc.ServiceCall call, $0.GetProjectsRequest request);

  $async.Future<$0.ProjectResponse> updateProject_Pre($grpc.ServiceCall $call,
      $async.Future<$0.UpdateProjectRequest> $request) async {
    return updateProject($call, await $request);
  }

  $async.Future<$0.ProjectResponse> updateProject(
      $grpc.ServiceCall call, $0.UpdateProjectRequest request);

  $async.Future<$0.StatusResponse> deleteProject_Pre($grpc.ServiceCall $call,
      $async.Future<$0.DeleteProjectRequest> $request) async {
    return deleteProject($call, await $request);
  }

  $async.Future<$0.StatusResponse> deleteProject(
      $grpc.ServiceCall call, $0.DeleteProjectRequest request);

  $async.Future<$0.SpaceResponse> createSpace_Pre($grpc.ServiceCall $call,
      $async.Future<$0.CreateSpaceRequest> $request) async {
    return createSpace($call, await $request);
  }

  $async.Future<$0.SpaceResponse> createSpace(
      $grpc.ServiceCall call, $0.CreateSpaceRequest request);

  $async.Future<$0.SpaceResponse> getSpace_Pre($grpc.ServiceCall $call,
      $async.Future<$0.GetSpaceRequest> $request) async {
    return getSpace($call, await $request);
  }

  $async.Future<$0.SpaceResponse> getSpace(
      $grpc.ServiceCall call, $0.GetSpaceRequest request);

  $async.Future<$0.GetChildSpacesResponse> getChildSpaces_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.GetChildSpacesRequest> $request) async {
    return getChildSpaces($call, await $request);
  }

  $async.Future<$0.GetChildSpacesResponse> getChildSpaces(
      $grpc.ServiceCall call, $0.GetChildSpacesRequest request);

  $async.Future<$0.StatusResponse> deleteSpace_Pre($grpc.ServiceCall $call,
      $async.Future<$0.DeleteSpaceRequest> $request) async {
    return deleteSpace($call, await $request);
  }

  $async.Future<$0.StatusResponse> deleteSpace(
      $grpc.ServiceCall call, $0.DeleteSpaceRequest request);

  $async.Future<$0.SpaceResponse> updateSpaceMetadata_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.UpdateMetadataRequest> $request) async {
    return updateSpaceMetadata($call, await $request);
  }

  $async.Future<$0.SpaceResponse> updateSpaceMetadata(
      $grpc.ServiceCall call, $0.UpdateMetadataRequest request);

  $async.Future<$0.ItemResponse> createItem_Pre($grpc.ServiceCall $call,
      $async.Future<$0.CreateItemRequest> $request) async {
    return createItem($call, await $request);
  }

  $async.Future<$0.ItemResponse> createItem(
      $grpc.ServiceCall call, $0.CreateItemRequest request);

  $async.Future<$0.ItemResponse> getItem_Pre($grpc.ServiceCall $call,
      $async.Future<$0.GetItemRequest> $request) async {
    return getItem($call, await $request);
  }

  $async.Future<$0.ItemResponse> getItem(
      $grpc.ServiceCall call, $0.GetItemRequest request);

  $async.Future<$0.GetItemsResponse> getItems_Pre($grpc.ServiceCall $call,
      $async.Future<$0.GetItemsRequest> $request) async {
    return getItems($call, await $request);
  }

  $async.Future<$0.GetItemsResponse> getItems(
      $grpc.ServiceCall call, $0.GetItemsRequest request);

  $async.Future<$0.GetItemsResponse> itemSearch_Pre($grpc.ServiceCall $call,
      $async.Future<$0.ItemSearchRequest> $request) async {
    return itemSearch($call, await $request);
  }

  $async.Future<$0.GetItemsResponse> itemSearch(
      $grpc.ServiceCall call, $0.ItemSearchRequest request);

  $async.Future<$0.StatusResponse> deleteItem_Pre($grpc.ServiceCall $call,
      $async.Future<$0.DeleteItemRequest> $request) async {
    return deleteItem($call, await $request);
  }

  $async.Future<$0.StatusResponse> deleteItem(
      $grpc.ServiceCall call, $0.DeleteItemRequest request);

  $async.Future<$0.ItemResponse> updateItemMetadata_Pre($grpc.ServiceCall $call,
      $async.Future<$0.UpdateMetadataRequest> $request) async {
    return updateItemMetadata($call, await $request);
  }

  $async.Future<$0.ItemResponse> updateItemMetadata(
      $grpc.ServiceCall call, $0.UpdateMetadataRequest request);

  $async.Future<$0.RevisionResponse> resolveKref_Pre($grpc.ServiceCall $call,
      $async.Future<$0.ResolveKrefRequest> $request) async {
    return resolveKref($call, await $request);
  }

  $async.Future<$0.RevisionResponse> resolveKref(
      $grpc.ServiceCall call, $0.ResolveKrefRequest request);

  $async.Future<$0.ResolveLocationResponse> resolveLocation_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.ResolveLocationRequest> $request) async {
    return resolveLocation($call, await $request);
  }

  $async.Future<$0.ResolveLocationResponse> resolveLocation(
      $grpc.ServiceCall call, $0.ResolveLocationRequest request);

  $async.Future<$0.RevisionResponse> createRevision_Pre($grpc.ServiceCall $call,
      $async.Future<$0.CreateRevisionRequest> $request) async {
    return createRevision($call, await $request);
  }

  $async.Future<$0.RevisionResponse> createRevision(
      $grpc.ServiceCall call, $0.CreateRevisionRequest request);

  $async.Future<$0.RevisionResponse> getRevision_Pre(
      $grpc.ServiceCall $call, $async.Future<$0.KrefRequest> $request) async {
    return getRevision($call, await $request);
  }

  $async.Future<$0.RevisionResponse> getRevision(
      $grpc.ServiceCall call, $0.KrefRequest request);

  $async.Future<$0.GetRevisionsResponse> getRevisions_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.GetRevisionsRequest> $request) async {
    return getRevisions($call, await $request);
  }

  $async.Future<$0.GetRevisionsResponse> getRevisions(
      $grpc.ServiceCall call, $0.GetRevisionsRequest request);

  $async.Future<$0.StatusResponse> deleteRevision_Pre($grpc.ServiceCall $call,
      $async.Future<$0.DeleteRevisionRequest> $request) async {
    return deleteRevision($call, await $request);
  }

  $async.Future<$0.StatusResponse> deleteRevision(
      $grpc.ServiceCall call, $0.DeleteRevisionRequest request);

  $async.Future<$0.PeekNextRevisionResponse> peekNextRevision_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.PeekNextRevisionRequest> $request) async {
    return peekNextRevision($call, await $request);
  }

  $async.Future<$0.PeekNextRevisionResponse> peekNextRevision(
      $grpc.ServiceCall call, $0.PeekNextRevisionRequest request);

  $async.Future<$0.RevisionResponse> updateRevisionMetadata_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.UpdateMetadataRequest> $request) async {
    return updateRevisionMetadata($call, await $request);
  }

  $async.Future<$0.RevisionResponse> updateRevisionMetadata(
      $grpc.ServiceCall call, $0.UpdateMetadataRequest request);

  $async.Future<$0.StatusResponse> tagRevision_Pre($grpc.ServiceCall $call,
      $async.Future<$0.TagRevisionRequest> $request) async {
    return tagRevision($call, await $request);
  }

  $async.Future<$0.StatusResponse> tagRevision(
      $grpc.ServiceCall call, $0.TagRevisionRequest request);

  $async.Future<$0.StatusResponse> unTagRevision_Pre($grpc.ServiceCall $call,
      $async.Future<$0.UnTagRevisionRequest> $request) async {
    return unTagRevision($call, await $request);
  }

  $async.Future<$0.StatusResponse> unTagRevision(
      $grpc.ServiceCall call, $0.UnTagRevisionRequest request);

  $async.Future<$0.HasTagResponse> hasTag_Pre(
      $grpc.ServiceCall $call, $async.Future<$0.HasTagRequest> $request) async {
    return hasTag($call, await $request);
  }

  $async.Future<$0.HasTagResponse> hasTag(
      $grpc.ServiceCall call, $0.HasTagRequest request);

  $async.Future<$0.WasTaggedResponse> wasTagged_Pre($grpc.ServiceCall $call,
      $async.Future<$0.WasTaggedRequest> $request) async {
    return wasTagged($call, await $request);
  }

  $async.Future<$0.WasTaggedResponse> wasTagged(
      $grpc.ServiceCall call, $0.WasTaggedRequest request);

  $async.Future<$0.StatusResponse> setDefaultArtifact_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.SetDefaultArtifactRequest> $request) async {
    return setDefaultArtifact($call, await $request);
  }

  $async.Future<$0.StatusResponse> setDefaultArtifact(
      $grpc.ServiceCall call, $0.SetDefaultArtifactRequest request);

  $async.Future<$0.ArtifactResponse> createArtifact_Pre($grpc.ServiceCall $call,
      $async.Future<$0.CreateArtifactRequest> $request) async {
    return createArtifact($call, await $request);
  }

  $async.Future<$0.ArtifactResponse> createArtifact(
      $grpc.ServiceCall call, $0.CreateArtifactRequest request);

  $async.Future<$0.ArtifactResponse> getArtifact_Pre($grpc.ServiceCall $call,
      $async.Future<$0.GetArtifactRequest> $request) async {
    return getArtifact($call, await $request);
  }

  $async.Future<$0.ArtifactResponse> getArtifact(
      $grpc.ServiceCall call, $0.GetArtifactRequest request);

  $async.Future<$0.GetArtifactsResponse> getArtifacts_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.GetArtifactsRequest> $request) async {
    return getArtifacts($call, await $request);
  }

  $async.Future<$0.GetArtifactsResponse> getArtifacts(
      $grpc.ServiceCall call, $0.GetArtifactsRequest request);

  $async.Future<$0.GetArtifactsByLocationResponse> getArtifactsByLocation_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.GetArtifactsByLocationRequest> $request) async {
    return getArtifactsByLocation($call, await $request);
  }

  $async.Future<$0.GetArtifactsByLocationResponse> getArtifactsByLocation(
      $grpc.ServiceCall call, $0.GetArtifactsByLocationRequest request);

  $async.Future<$0.StatusResponse> deleteArtifact_Pre($grpc.ServiceCall $call,
      $async.Future<$0.DeleteArtifactRequest> $request) async {
    return deleteArtifact($call, await $request);
  }

  $async.Future<$0.StatusResponse> deleteArtifact(
      $grpc.ServiceCall call, $0.DeleteArtifactRequest request);

  $async.Future<$0.ArtifactResponse> updateArtifactMetadata_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.UpdateMetadataRequest> $request) async {
    return updateArtifactMetadata($call, await $request);
  }

  $async.Future<$0.ArtifactResponse> updateArtifactMetadata(
      $grpc.ServiceCall call, $0.UpdateMetadataRequest request);

  $async.Future<$0.StatusResponse> setAttribute_Pre($grpc.ServiceCall $call,
      $async.Future<$0.SetAttributeRequest> $request) async {
    return setAttribute($call, await $request);
  }

  $async.Future<$0.StatusResponse> setAttribute(
      $grpc.ServiceCall call, $0.SetAttributeRequest request);

  $async.Future<$0.GetAttributeResponse> getAttribute_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.GetAttributeRequest> $request) async {
    return getAttribute($call, await $request);
  }

  $async.Future<$0.GetAttributeResponse> getAttribute(
      $grpc.ServiceCall call, $0.GetAttributeRequest request);

  $async.Future<$0.StatusResponse> deleteAttribute_Pre($grpc.ServiceCall $call,
      $async.Future<$0.DeleteAttributeRequest> $request) async {
    return deleteAttribute($call, await $request);
  }

  $async.Future<$0.StatusResponse> deleteAttribute(
      $grpc.ServiceCall call, $0.DeleteAttributeRequest request);

  $async.Future<$0.StatusResponse> createEdge_Pre($grpc.ServiceCall $call,
      $async.Future<$0.CreateEdgeRequest> $request) async {
    return createEdge($call, await $request);
  }

  $async.Future<$0.StatusResponse> createEdge(
      $grpc.ServiceCall call, $0.CreateEdgeRequest request);

  $async.Future<$0.GetEdgesResponse> getEdges_Pre($grpc.ServiceCall $call,
      $async.Future<$0.GetEdgesRequest> $request) async {
    return getEdges($call, await $request);
  }

  $async.Future<$0.GetEdgesResponse> getEdges(
      $grpc.ServiceCall call, $0.GetEdgesRequest request);

  $async.Future<$0.StatusResponse> deleteEdge_Pre($grpc.ServiceCall $call,
      $async.Future<$0.DeleteEdgeRequest> $request) async {
    return deleteEdge($call, await $request);
  }

  $async.Future<$0.StatusResponse> deleteEdge(
      $grpc.ServiceCall call, $0.DeleteEdgeRequest request);

  $async.Future<$0.TraverseEdgesResponse> traverseEdges_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.TraverseEdgesRequest> $request) async {
    return traverseEdges($call, await $request);
  }

  $async.Future<$0.TraverseEdgesResponse> traverseEdges(
      $grpc.ServiceCall call, $0.TraverseEdgesRequest request);

  $async.Future<$0.ShortestPathResponse> findShortestPath_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.ShortestPathRequest> $request) async {
    return findShortestPath($call, await $request);
  }

  $async.Future<$0.ShortestPathResponse> findShortestPath(
      $grpc.ServiceCall call, $0.ShortestPathRequest request);

  $async.Future<$0.ImpactAnalysisResponse> analyzeImpact_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.ImpactAnalysisRequest> $request) async {
    return analyzeImpact($call, await $request);
  }

  $async.Future<$0.ImpactAnalysisResponse> analyzeImpact(
      $grpc.ServiceCall call, $0.ImpactAnalysisRequest request);

  $async.Future<$0.ItemResponse> createBundle_Pre($grpc.ServiceCall $call,
      $async.Future<$0.CreateBundleRequest> $request) async {
    return createBundle($call, await $request);
  }

  $async.Future<$0.ItemResponse> createBundle(
      $grpc.ServiceCall call, $0.CreateBundleRequest request);

  $async.Future<$0.AddBundleMemberResponse> addBundleMember_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.AddBundleMemberRequest> $request) async {
    return addBundleMember($call, await $request);
  }

  $async.Future<$0.AddBundleMemberResponse> addBundleMember(
      $grpc.ServiceCall call, $0.AddBundleMemberRequest request);

  $async.Future<$0.RemoveBundleMemberResponse> removeBundleMember_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.RemoveBundleMemberRequest> $request) async {
    return removeBundleMember($call, await $request);
  }

  $async.Future<$0.RemoveBundleMemberResponse> removeBundleMember(
      $grpc.ServiceCall call, $0.RemoveBundleMemberRequest request);

  $async.Future<$0.GetBundleMembersResponse> getBundleMembers_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.GetBundleMembersRequest> $request) async {
    return getBundleMembers($call, await $request);
  }

  $async.Future<$0.GetBundleMembersResponse> getBundleMembers(
      $grpc.ServiceCall call, $0.GetBundleMembersRequest request);

  $async.Future<$0.GetBundleHistoryResponse> getBundleHistory_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.GetBundleHistoryRequest> $request) async {
    return getBundleHistory($call, await $request);
  }

  $async.Future<$0.GetBundleHistoryResponse> getBundleHistory(
      $grpc.ServiceCall call, $0.GetBundleHistoryRequest request);

  $async.Future<$0.TenantUsageResponse> getTenantUsage_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.GetTenantUsageRequest> $request) async {
    return getTenantUsage($call, await $request);
  }

  $async.Future<$0.TenantUsageResponse> getTenantUsage(
      $grpc.ServiceCall call, $0.GetTenantUsageRequest request);

  $async.Stream<$0.Event> eventStream_Pre($grpc.ServiceCall $call,
      $async.Future<$0.EventStreamRequest> $request) async* {
    yield* eventStream($call, await $request);
  }

  $async.Stream<$0.Event> eventStream(
      $grpc.ServiceCall call, $0.EventStreamRequest request);

  $async.Future<$0.EventCapabilities> getEventCapabilities_Pre(
      $grpc.ServiceCall $call,
      $async.Future<$0.GetEventCapabilitiesRequest> $request) async {
    return getEventCapabilities($call, await $request);
  }

  $async.Future<$0.EventCapabilities> getEventCapabilities(
      $grpc.ServiceCall call, $0.GetEventCapabilitiesRequest request);

  $async.Future<$0.StatusResponse> setDeprecated_Pre($grpc.ServiceCall $call,
      $async.Future<$0.SetDeprecatedRequest> $request) async {
    return setDeprecated($call, await $request);
  }

  $async.Future<$0.StatusResponse> setDeprecated(
      $grpc.ServiceCall call, $0.SetDeprecatedRequest request);
}
