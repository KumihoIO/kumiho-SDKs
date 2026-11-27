//! Loopback coverage for backup observations and native session errors.
#![cfg(feature = "mock-server")]

use kumiho::{
    backup_status::{
        pb::{
            self,
            backup_status_service_server::{BackupStatusService, BackupStatusServiceServer},
            GetBackupStatusRequest, GetBackupStatusResponse,
        },
        BackupState,
    },
    Client, Error,
};
use std::{collections::VecDeque, sync::Mutex};
use tokio_stream::wrappers::TcpListenerStream;
use tonic::{Code, Request, Response, Status};

struct Server(Mutex<VecDeque<Result<GetBackupStatusResponse, Status>>>);

#[tonic::async_trait]
impl BackupStatusService for Server {
    async fn get_backup_status(
        &self,
        request: Request<GetBackupStatusRequest>,
    ) -> Result<Response<GetBackupStatusResponse>, Status> {
        assert_eq!(
            request.metadata().get("authorization").unwrap(),
            "Bearer fixture-backup"
        );
        assert_eq!(request.metadata().get("x-tenant-id").unwrap(), "tenant");
        assert_eq!(request.into_inner(), GetBackupStatusRequest {});
        self.0
            .lock()
            .unwrap()
            .pop_front()
            .unwrap()
            .map(Response::new)
    }
}

fn observation(
    state: pb::BackupState,
    observed_at_ms: Option<u64>,
    last_checkpoint_ms: Option<u64>,
) -> GetBackupStatusResponse {
    GetBackupStatusResponse {
        state: state as i32,
        observed_at_ms,
        last_checkpoint_ms,
    }
}

#[tokio::test]
async fn reads_the_observation_using_the_existing_session_and_validates_wire_data() {
    use pb::BackupState as Wire;
    let server = Server(Mutex::new(VecDeque::from([
        Ok(observation(Wire::Healthy, Some(42), Some(40))),
        Ok(observation(Wire::Unavailable, Some(17), None)),
        Ok(observation(Wire::Unconfigured, None, None)),
        Ok(observation(Wire::Healthy, None, None)),
        Ok(observation(Wire::Healthy, Some(42), Some(43))),
        Ok(observation(Wire::Unavailable, Some(17), Some(16))),
        Ok(observation(Wire::Unconfigured, Some(17), None)),
        Ok(observation(Wire::Preparing, Some(u64::MAX), None)),
        Ok(observation(Wire::Unspecified, None, None)),
        Ok(GetBackupStatusResponse {
            state: 99,
            ..Default::default()
        }),
        Err(Status::permission_denied("fixture membership revoked")),
        Err(Status::unimplemented("fixture older server")),
    ])));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let address = listener.local_addr().unwrap();
    let (stop, stopped) = tokio::sync::oneshot::channel();
    let serving = tokio::spawn(
        tonic::transport::Server::builder()
            .add_service(BackupStatusServiceServer::new(server))
            .serve_with_incoming_shutdown(TcpListenerStream::new(listener), async {
                let _ = stopped.await;
            }),
    );
    let client = Client::builder()
        .endpoint(format!("http://{address}"))
        .token("fixture-backup")
        .use_discovery(false)
        .metadata("x-tenant-id", "tenant")
        .build()
        .await
        .unwrap();

    let healthy = client.get_backup_status().await.unwrap();
    assert_eq!(healthy.state, BackupState::Healthy);
    assert_eq!(healthy.observed_at_ms, Some(42));
    assert_eq!(healthy.last_checkpoint_ms, Some(40));
    let stale = client.get_backup_status().await.unwrap();
    assert_eq!(stale.state, BackupState::Unavailable);
    assert_eq!(stale.observed_at_ms, Some(17));
    assert_eq!(stale.last_checkpoint_ms, None);
    assert_eq!(
        client.get_backup_status().await.unwrap().state,
        BackupState::Unconfigured
    );
    for code in [Code::DataLoss; 7]
        .into_iter()
        .chain([Code::PermissionDenied, Code::Unimplemented])
    {
        assert!(
            matches!(client.get_backup_status().await, Err(Error::Rpc(status)) if status.code() == code)
        );
    }
    stop.send(()).unwrap();
    serving.await.unwrap().unwrap();
}
