//! In-process integration tests for the Rust SDK.
//!
//! A mock `KumihoService` gRPC server is started on a loopback port and the real
//! [`kumiho::Client`] is pointed at it, exercising request construction,
//! correlation-id/metadata injection, the transient-retry interceptor and
//! response parsing — no credentials or network required.
//!
//! Gated behind the `mock-server` feature (which makes build.rs emit the server
//! stubs). Run with: `cargo test --features mock-server`.
#![cfg(feature = "mock-server")]

use std::sync::{Arc, Mutex};

use kumiho::pb;
use kumiho::pb::kumiho_service_server::{KumihoService, KumihoServiceServer};
use kumiho::Client;
use tonic::{Request, Response, Status};

#[derive(Default)]
struct Recorded {
    last_item: Option<pb::CreateItemRequest>,
    last_revision_kref: String,
    saw_correlation_id: bool,
}

#[derive(Clone, Default)]
struct FakeKumiho {
    rec: Arc<Mutex<Recorded>>,
}

fn unimpl(name: &str) -> Status {
    Status::unimplemented(format!("{name} not used in integration tests"))
}

#[tonic::async_trait]
impl KumihoService for FakeKumiho {
    // ---- methods exercised by the tests ----

    async fn create_project(
        &self,
        req: Request<pb::CreateProjectRequest>,
    ) -> Result<Response<pb::ProjectResponse>, Status> {
        if req.metadata().get("x-correlation-id").is_some() {
            self.rec.lock().unwrap().saw_correlation_id = true;
        }
        let r = req.into_inner();
        Ok(Response::new(pb::ProjectResponse {
            project_id: "proj-123".into(),
            name: r.name,
            description: r.description,
            ..Default::default()
        }))
    }

    async fn get_projects(
        &self,
        _req: Request<pb::GetProjectsRequest>,
    ) -> Result<Response<pb::GetProjectsResponse>, Status> {
        Ok(Response::new(pb::GetProjectsResponse {
            projects: vec![
                pb::ProjectResponse {
                    project_id: "p1".into(),
                    name: "alpha".into(),
                    ..Default::default()
                },
                pb::ProjectResponse {
                    project_id: "p2".into(),
                    name: "beta".into(),
                    ..Default::default()
                },
            ],
        }))
    }

    async fn create_item(
        &self,
        req: Request<pb::CreateItemRequest>,
    ) -> Result<Response<pb::ItemResponse>, Status> {
        let r = req.into_inner();
        self.rec.lock().unwrap().last_item = Some(r.clone());
        let uri = format!(
            "kref://{}/{}.{}",
            r.parent_path.trim_start_matches('/'),
            r.item_name,
            r.kind
        );
        Ok(Response::new(pb::ItemResponse {
            kref: Some(pb::Kref { uri }),
            name: format!("{}.{}", r.item_name, r.kind),
            item_name: r.item_name,
            kind: r.kind,
            ..Default::default()
        }))
    }

    async fn get_revision(
        &self,
        req: Request<pb::KrefRequest>,
    ) -> Result<Response<pb::RevisionResponse>, Status> {
        let uri = req.into_inner().kref.map(|k| k.uri).unwrap_or_default();
        self.rec.lock().unwrap().last_revision_kref = uri.clone();
        Ok(Response::new(pb::RevisionResponse {
            kref: Some(pb::Kref { uri }),
            number: 3,
            latest: true,
            ..Default::default()
        }))
    }

    async fn resolve_location(
        &self,
        req: Request<pb::ResolveLocationRequest>,
    ) -> Result<Response<pb::ResolveLocationResponse>, Status> {
        let r = req.into_inner();
        if r.kref.contains("missing") {
            return Err(Status::not_found("revision not found"));
        }
        Ok(Response::new(pb::ResolveLocationResponse {
            location: "/data/hero.fbx".into(),
            ..Default::default()
        }))
    }

    // ---- server-streaming method (unused) ----

    type EventStreamStream =
        std::pin::Pin<Box<dyn futures_core::Stream<Item = Result<pb::Event, Status>> + Send>>;
    async fn event_stream(
        &self,
        _req: Request<pb::EventStreamRequest>,
    ) -> Result<Response<Self::EventStreamStream>, Status> {
        Err(unimpl("event_stream"))
    }

    // ---- remaining methods: unimplemented stubs ----

    async fn update_project(
        &self,
        _r: Request<pb::UpdateProjectRequest>,
    ) -> Result<Response<pb::ProjectResponse>, Status> {
        Err(unimpl("update_project"))
    }
    async fn delete_project(
        &self,
        _r: Request<pb::DeleteProjectRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("delete_project"))
    }
    async fn create_space(
        &self,
        _r: Request<pb::CreateSpaceRequest>,
    ) -> Result<Response<pb::SpaceResponse>, Status> {
        Err(unimpl("create_space"))
    }
    async fn get_space(
        &self,
        _r: Request<pb::GetSpaceRequest>,
    ) -> Result<Response<pb::SpaceResponse>, Status> {
        Err(unimpl("get_space"))
    }
    async fn get_child_spaces(
        &self,
        _r: Request<pb::GetChildSpacesRequest>,
    ) -> Result<Response<pb::GetChildSpacesResponse>, Status> {
        Err(unimpl("get_child_spaces"))
    }
    async fn delete_space(
        &self,
        _r: Request<pb::DeleteSpaceRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("delete_space"))
    }
    async fn update_space_metadata(
        &self,
        _r: Request<pb::UpdateMetadataRequest>,
    ) -> Result<Response<pb::SpaceResponse>, Status> {
        Err(unimpl("update_space_metadata"))
    }
    async fn get_item(
        &self,
        _r: Request<pb::GetItemRequest>,
    ) -> Result<Response<pb::ItemResponse>, Status> {
        Err(unimpl("get_item"))
    }
    async fn get_items(
        &self,
        _r: Request<pb::GetItemsRequest>,
    ) -> Result<Response<pb::GetItemsResponse>, Status> {
        Err(unimpl("get_items"))
    }
    async fn item_search(
        &self,
        _r: Request<pb::ItemSearchRequest>,
    ) -> Result<Response<pb::GetItemsResponse>, Status> {
        Err(unimpl("item_search"))
    }
    async fn delete_item(
        &self,
        _r: Request<pb::DeleteItemRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("delete_item"))
    }
    async fn update_item_metadata(
        &self,
        _r: Request<pb::UpdateMetadataRequest>,
    ) -> Result<Response<pb::ItemResponse>, Status> {
        Err(unimpl("update_item_metadata"))
    }
    async fn search(
        &self,
        _r: Request<pb::SearchRequest>,
    ) -> Result<Response<pb::SearchResponse>, Status> {
        Err(unimpl("search"))
    }
    async fn score_revisions(
        &self,
        _r: Request<pb::ScoreRevisionsRequest>,
    ) -> Result<Response<pb::ScoreRevisionsResponse>, Status> {
        Err(unimpl("score_revisions"))
    }
    async fn resolve_kref(
        &self,
        _r: Request<pb::ResolveKrefRequest>,
    ) -> Result<Response<pb::RevisionResponse>, Status> {
        Err(unimpl("resolve_kref"))
    }
    async fn create_revision(
        &self,
        _r: Request<pb::CreateRevisionRequest>,
    ) -> Result<Response<pb::RevisionResponse>, Status> {
        Err(unimpl("create_revision"))
    }
    async fn get_revisions(
        &self,
        _r: Request<pb::GetRevisionsRequest>,
    ) -> Result<Response<pb::GetRevisionsResponse>, Status> {
        Err(unimpl("get_revisions"))
    }
    async fn batch_get_revisions(
        &self,
        _r: Request<pb::BatchGetRevisionsRequest>,
    ) -> Result<Response<pb::BatchGetRevisionsResponse>, Status> {
        Err(unimpl("batch_get_revisions"))
    }
    async fn delete_revision(
        &self,
        _r: Request<pb::DeleteRevisionRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("delete_revision"))
    }
    async fn peek_next_revision(
        &self,
        _r: Request<pb::PeekNextRevisionRequest>,
    ) -> Result<Response<pb::PeekNextRevisionResponse>, Status> {
        Err(unimpl("peek_next_revision"))
    }
    async fn update_revision_metadata(
        &self,
        _r: Request<pb::UpdateMetadataRequest>,
    ) -> Result<Response<pb::RevisionResponse>, Status> {
        Err(unimpl("update_revision_metadata"))
    }
    async fn tag_revision(
        &self,
        _r: Request<pb::TagRevisionRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("tag_revision"))
    }
    async fn un_tag_revision(
        &self,
        _r: Request<pb::UnTagRevisionRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("un_tag_revision"))
    }
    async fn has_tag(
        &self,
        _r: Request<pb::HasTagRequest>,
    ) -> Result<Response<pb::HasTagResponse>, Status> {
        Err(unimpl("has_tag"))
    }
    async fn was_tagged(
        &self,
        _r: Request<pb::WasTaggedRequest>,
    ) -> Result<Response<pb::WasTaggedResponse>, Status> {
        Err(unimpl("was_tagged"))
    }
    async fn set_default_artifact(
        &self,
        _r: Request<pb::SetDefaultArtifactRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("set_default_artifact"))
    }
    async fn create_artifact(
        &self,
        _r: Request<pb::CreateArtifactRequest>,
    ) -> Result<Response<pb::ArtifactResponse>, Status> {
        Err(unimpl("create_artifact"))
    }
    async fn get_artifact(
        &self,
        _r: Request<pb::GetArtifactRequest>,
    ) -> Result<Response<pb::ArtifactResponse>, Status> {
        Err(unimpl("get_artifact"))
    }
    async fn get_artifacts(
        &self,
        _r: Request<pb::GetArtifactsRequest>,
    ) -> Result<Response<pb::GetArtifactsResponse>, Status> {
        Err(unimpl("get_artifacts"))
    }
    async fn get_artifacts_by_location(
        &self,
        _r: Request<pb::GetArtifactsByLocationRequest>,
    ) -> Result<Response<pb::GetArtifactsByLocationResponse>, Status> {
        Err(unimpl("get_artifacts_by_location"))
    }
    async fn delete_artifact(
        &self,
        _r: Request<pb::DeleteArtifactRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("delete_artifact"))
    }
    async fn update_artifact_metadata(
        &self,
        _r: Request<pb::UpdateMetadataRequest>,
    ) -> Result<Response<pb::ArtifactResponse>, Status> {
        Err(unimpl("update_artifact_metadata"))
    }
    async fn set_attribute(
        &self,
        _r: Request<pb::SetAttributeRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("set_attribute"))
    }
    async fn get_attribute(
        &self,
        _r: Request<pb::GetAttributeRequest>,
    ) -> Result<Response<pb::GetAttributeResponse>, Status> {
        Err(unimpl("get_attribute"))
    }
    async fn delete_attribute(
        &self,
        _r: Request<pb::DeleteAttributeRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("delete_attribute"))
    }
    async fn create_edge(
        &self,
        _r: Request<pb::CreateEdgeRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("create_edge"))
    }
    async fn get_edges(
        &self,
        _r: Request<pb::GetEdgesRequest>,
    ) -> Result<Response<pb::GetEdgesResponse>, Status> {
        Err(unimpl("get_edges"))
    }
    async fn delete_edge(
        &self,
        _r: Request<pb::DeleteEdgeRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("delete_edge"))
    }
    async fn traverse_edges(
        &self,
        _r: Request<pb::TraverseEdgesRequest>,
    ) -> Result<Response<pb::TraverseEdgesResponse>, Status> {
        Err(unimpl("traverse_edges"))
    }
    async fn find_shortest_path(
        &self,
        _r: Request<pb::ShortestPathRequest>,
    ) -> Result<Response<pb::ShortestPathResponse>, Status> {
        Err(unimpl("find_shortest_path"))
    }
    async fn analyze_impact(
        &self,
        _r: Request<pb::ImpactAnalysisRequest>,
    ) -> Result<Response<pb::ImpactAnalysisResponse>, Status> {
        Err(unimpl("analyze_impact"))
    }
    async fn create_bundle(
        &self,
        _r: Request<pb::CreateBundleRequest>,
    ) -> Result<Response<pb::ItemResponse>, Status> {
        Err(unimpl("create_bundle"))
    }
    async fn add_bundle_member(
        &self,
        _r: Request<pb::AddBundleMemberRequest>,
    ) -> Result<Response<pb::AddBundleMemberResponse>, Status> {
        Err(unimpl("add_bundle_member"))
    }
    async fn remove_bundle_member(
        &self,
        _r: Request<pb::RemoveBundleMemberRequest>,
    ) -> Result<Response<pb::RemoveBundleMemberResponse>, Status> {
        Err(unimpl("remove_bundle_member"))
    }
    async fn get_bundle_members(
        &self,
        _r: Request<pb::GetBundleMembersRequest>,
    ) -> Result<Response<pb::GetBundleMembersResponse>, Status> {
        Err(unimpl("get_bundle_members"))
    }
    async fn get_bundle_history(
        &self,
        _r: Request<pb::GetBundleHistoryRequest>,
    ) -> Result<Response<pb::GetBundleHistoryResponse>, Status> {
        Err(unimpl("get_bundle_history"))
    }
    async fn get_tenant_usage(
        &self,
        _r: Request<pb::GetTenantUsageRequest>,
    ) -> Result<Response<pb::TenantUsageResponse>, Status> {
        Err(unimpl("get_tenant_usage"))
    }
    async fn get_event_capabilities(
        &self,
        _r: Request<pb::GetEventCapabilitiesRequest>,
    ) -> Result<Response<pb::EventCapabilities>, Status> {
        Err(unimpl("get_event_capabilities"))
    }
    async fn set_deprecated(
        &self,
        _r: Request<pb::SetDeprecatedRequest>,
    ) -> Result<Response<pb::StatusResponse>, Status> {
        Err(unimpl("set_deprecated"))
    }
}

/// Start the mock server on a free loopback port and return a connected client.
///
/// Assumes no interfering `KUMIHO_*` env / `~/.kumiho` credentials (true in CI).
async fn start_server() -> (FakeKumiho, Client) {
    let fake = FakeKumiho::default();
    let svc = KumihoServiceServer::new(fake.clone());

    // Reserve a free port, then hand the address to tonic.
    let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    let addr = listener.local_addr().unwrap();
    drop(listener);

    tokio::spawn(async move {
        tonic::transport::Server::builder()
            .add_service(svc)
            .serve(addr)
            .await
            .expect("mock server failed");
    });

    // connect_lazy + the client's transient-retry interceptor tolerate the brief
    // startup window; a short pause makes the first call deterministic.
    tokio::time::sleep(std::time::Duration::from_millis(200)).await;

    let client = Client::connect(format!("http://127.0.0.1:{}", addr.port()))
        .await
        .expect("connect");
    (fake, client)
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn integration_projects() {
    let (fake, client) = start_server().await;

    let p = client.create_project("vfx", "VFX assets").await.unwrap();
    assert_eq!(p.project_id, "proj-123");
    assert_eq!(p.name, "vfx");
    assert_eq!(p.description, "VFX assets");

    let projs = client.get_projects().await.unwrap();
    assert_eq!(projs.len(), 2);
    assert_eq!(projs[0].name, "alpha");
    assert_eq!(projs[1].name, "beta");

    assert!(
        fake.rec.lock().unwrap().saw_correlation_id,
        "server did not receive an x-correlation-id header"
    );
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn integration_create_item_fields_and_reserved_kind() {
    let (fake, client) = start_server().await;

    let item = client
        .create_item("/vfx/chars", "hero", "model", None)
        .await
        .unwrap();
    assert_eq!(item.kind, "model");
    assert_eq!(item.item_name, "hero");
    {
        let rec = fake.rec.lock().unwrap();
        let req = rec.last_item.as_ref().expect("server received CreateItem");
        assert_eq!(req.parent_path, "/vfx/chars");
        assert_eq!(req.item_name, "hero");
        assert_eq!(req.kind, "model");
    }

    // Reserved "bundle" kind is rejected client-side, before any RPC.
    fake.rec.lock().unwrap().last_item = None;
    let err = client
        .create_item("/vfx/chars", "pack", "bundle", None)
        .await;
    assert!(err.is_err(), "reserved kind 'bundle' should be rejected");
    assert!(
        fake.rec.lock().unwrap().last_item.is_none(),
        "reserved-kind create must not reach the server"
    );
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn integration_get_revision_carries_revision_query() {
    let (fake, client) = start_server().await;

    let rev = client
        .get_revision("kref://vfx/chars/hero.model?r=3")
        .await
        .unwrap();
    assert_eq!(rev.number, 3);
    assert!(rev.latest);
    assert!(fake.rec.lock().unwrap().last_revision_kref.contains("?r=3"));
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn integration_resolve_swallows_rpc_error() {
    let (_fake, client) = start_server().await;

    let loc = client.resolve("kref://vfx/chars/hero.model").await.unwrap();
    assert_eq!(loc.as_deref(), Some("/data/hero.fbx"));

    // A failed resolution returns Ok(None) — not an error — per the SDK fix.
    let loc = client
        .resolve("kref://vfx/chars/missing.model")
        .await
        .unwrap();
    assert_eq!(loc, None);
}
