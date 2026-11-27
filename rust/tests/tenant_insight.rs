//! Loopback coverage for tenant aggregates: the existing session, the answer and the refusals.
#![cfg(feature = "mock-server")]

use kumiho::{
    tenant_insight::{
        pb::tenant_insight_service_server::{TenantInsightService, TenantInsightServiceServer},
        AggregateBasis, GetTenantAggregatesRequest, Granularity, ProjectAggregate,
        TenantAggregates,
    },
    Client, Error,
};
use std::{collections::VecDeque, sync::Mutex};
use tokio_stream::wrappers::TcpListenerStream;
use tonic::{Code, Request, Response, Status};

struct Server(Mutex<VecDeque<Result<TenantAggregates, Status>>>);

fn request() -> GetTenantAggregatesRequest {
    GetTenantAggregatesRequest {
        include_deprecated: false,
        granularity: Granularity::Day as i32,
        window_days: 60,
        recent_limit: 100,
        utc_offset_minutes: 540,
    }
}

#[tonic::async_trait]
impl TenantInsightService for Server {
    async fn get_tenant_aggregates(
        &self,
        received: Request<GetTenantAggregatesRequest>,
    ) -> Result<Response<TenantAggregates>, Status> {
        assert_eq!(
            received.metadata().get("authorization").unwrap(),
            "Bearer fixture-insight"
        );
        assert_eq!(received.metadata().get("x-tenant-id").unwrap(), "tenant");
        assert_eq!(received.into_inner(), request());
        self.0
            .lock()
            .unwrap()
            .pop_front()
            .unwrap()
            .map(Response::new)
    }
}

#[tokio::test]
async fn reads_the_aggregates_using_the_existing_session_and_retries_only_unavailable() {
    std::env::set_var("KUMIHO_GRPC_RETRY_MAX_ATTEMPTS", "2");
    let answer = TenantAggregates {
        basis: Some(AggregateBasis {
            cell_log_index: 7,
            as_of: "2026-11-26T00:00:00Z".into(),
            ..Default::default()
        }),
        projects: vec![ProjectAggregate {
            name: "a".into(),
            revisions: 17_673,
            ..Default::default()
        }],
        ..Default::default()
    };
    let refusals = [
        Status::permission_denied("permission denied"),
        Status::failed_precondition(
            "tenant aggregates need a security administrator or a tenant without object labels",
        ),
        Status::resource_exhausted("resource limit exceeded: tenant aggregate exceeds 1 rows"),
        Status::invalid_argument("window_days must be 0..=120"),
        Status::data_loss("stored record is corrupt"),
        Status::unimplemented("fixture older server"),
    ];
    let kept_changing =
        || Status::unavailable("tenant aggregate: the tenant kept changing during the read");
    let server = Server(Mutex::new(
        [Ok(answer.clone()), Err(kept_changing()), Ok(answer.clone())]
            .into_iter()
            .chain(refusals.iter().cloned().map(Err))
            .chain([Err(kept_changing()), Err(kept_changing())])
            .collect(),
    ));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let address = listener.local_addr().unwrap();
    let (stop, stopped) = tokio::sync::oneshot::channel();
    let serving = tokio::spawn(
        tonic::transport::Server::builder()
            .add_service(TenantInsightServiceServer::new(server))
            .serve_with_incoming_shutdown(TcpListenerStream::new(listener), async {
                let _ = stopped.await;
            }),
    );
    let client = Client::builder()
        .endpoint(format!("http://{address}"))
        .token("fixture-insight")
        .use_discovery(false)
        .metadata("x-tenant-id", "tenant")
        .build()
        .await
        .unwrap();

    assert_eq!(
        client.get_tenant_aggregates(request()).await.unwrap(),
        answer
    );
    // One Unavailable is retried and the second attempt answers.
    assert_eq!(
        client.get_tenant_aggregates(request()).await.unwrap(),
        answer
    );
    // Every other refusal is returned from the first attempt, and Unavailable after the last one.
    for code in refusals.iter().map(Status::code).chain([Code::Unavailable]) {
        assert!(
            matches!(client.get_tenant_aggregates(request()).await, Err(Error::Rpc(status)) if status.code() == code),
            "{code:?}"
        );
    }
    stop.send(()).unwrap();
    serving.await.unwrap().unwrap();
}
