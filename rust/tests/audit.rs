//! Synthetic gRPC transport test: exact filters, auth, typed actor, coverage and closed RPC errors.
#![cfg(feature = "mock-server")]
use kumiho::{
    audit::pb::{
        change_audit_service_server::{ChangeAuditService, ChangeAuditServiceServer},
        *,
    },
    Client, Error,
};
use std::sync::{Arc, Mutex};
use tokio_stream::wrappers::TcpListenerStream;
use tonic::{Request, Response, Status};
#[derive(Clone)]
struct Server(Arc<Mutex<Vec<ListChangesRequest>>>);
#[tonic::async_trait]
impl ChangeAuditService for Server {
    async fn list_changes(
        &self,
        r: Request<ListChangesRequest>,
    ) -> Result<Response<ChangeAuditPage>, Status> {
        assert_eq!(
            r.metadata().get("authorization").unwrap(),
            "Bearer fixture-audit"
        );
        assert_eq!(r.metadata().get("x-tenant-id").unwrap(), "tenant");
        if r.get_ref().cursor == "expired" {
            return Err(Status::failed_precondition(
                "event cursor outside replay window",
            ));
        }
        self.0.lock().unwrap().push(r.into_inner());
        Ok(Response::new(ChangeAuditPage {
            entries: vec![ChangeAuditEntry {
                event_id: "immutable-change".into(),
                action: "revision.created".into(),
                committed_at_ms: 1700000000000,
                actor: Some(AuditPrincipal {
                    kind: "agent".into(),
                    id: "agent-fixture".into(),
                }),
                via: vec![AuditPrincipal {
                    kind: "user".into(),
                    id: "owner".into(),
                }],
                target_kref: "kref://film/shots/a.shot?r=2".into(),
                related_krefs: vec![],
                request_id: None,
            }],
            next_cursor: "opaque-fixture".into(),
            has_more: true,
            observed_through: "opaque-tail".into(),
            replay_window_limited: true,
            retention_hours: 72,
            max_events: 10000,
        }))
    }
}
#[tokio::test]
async fn audit_rpc_preserves_filters_attribution_coverage_and_errors() {
    let seen = Arc::new(Mutex::new(Vec::new()));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let address = listener.local_addr().unwrap();
    let (stop_tx, stop_rx) = tokio::sync::oneshot::channel();
    let server = tokio::spawn(
        tonic::transport::Server::builder()
            .add_service(ChangeAuditServiceServer::new(Server(seen.clone())))
            .serve_with_incoming_shutdown(TcpListenerStream::new(listener), async {
                let _ = stop_rx.await;
            }),
    );
    let client = Client::builder()
        .endpoint(format!("http://{address}"))
        .token("fixture-audit")
        .use_discovery(false)
        .metadata("x-tenant-id", "tenant")
        .build()
        .await
        .unwrap();
    let q = ListChangesRequest {
        page_size: 25,
        cursor: "previous".into(),
        from_ms: 100,
        until_ms: 200,
        action: "revision.created".into(),
        project: "film".into(),
        actor_kind: "agent".into(),
        actor_id: "agent-fixture".into(),
    };
    let p = client
        .list_changes(q.clone())
        .await
        .expect("native audit RPC must be available");
    assert_eq!(seen.lock().unwrap().as_slice(), &[q]);
    assert_eq!(p.next_cursor, "opaque-fixture");
    assert!(p.has_more && p.replay_window_limited);
    assert_eq!(p.entries[0].actor.as_ref().unwrap().kind, "agent");
    assert_eq!(p.entries[0].via[0].id, "owner");
    assert!(p.entries[0].request_id.is_none());
    let error = client
        .list_changes(ListChangesRequest {
            cursor: "expired".into(),
            ..Default::default()
        })
        .await
        .unwrap_err();
    assert!(matches!(error,Error::Rpc(s) if s.code()==tonic::Code::FailedPrecondition));
    let _ = stop_tx.send(());
    server.await.unwrap().unwrap();
}
