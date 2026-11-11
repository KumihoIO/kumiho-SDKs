//! Loopback checks for the project export route, authentication and complete response validation.
#![cfg(feature = "mock-server")]

use kumiho::{
    project_export::pb::{
        project_export_service_server::{ProjectExportService, ProjectExportServiceServer},
        ExportProjectRequest, ExportProjectResponse,
    },
    Client, Error,
};
use tokio_stream::wrappers::TcpListenerStream;
use tonic::{Code, Request, Response, Status};

struct Server;

#[tonic::async_trait]
impl ProjectExportService for Server {
    async fn export_project(
        &self,
        request: Request<ExportProjectRequest>,
    ) -> Result<Response<ExportProjectResponse>, Status> {
        assert_eq!(
            request.metadata().get("authorization").unwrap(),
            "Bearer fixture-export"
        );
        assert_eq!(request.metadata().get("x-tenant-id").unwrap(), "tenant");
        let project = request.into_inner().project;
        if project == "unavailable" {
            return Err(Status::unimplemented("project export is unavailable"));
        }
        let name = if project == "mismatch" {
            "different"
        } else {
            &project
        };
        let title = if project == "large" {
            "x".repeat(4 * 1024 * 1024)
        } else {
            "The film".into()
        };
        let document = if project == "partial" {
            br#"{"schema_version":1,"project":{"name":"partial"},"snapshot_sequence":"42"}"#
                .to_vec()
        } else {
            serde_json::to_vec(&serde_json::json!({
                "schema_version": 1,
                "snapshot_sequence": "42",
                "project": {"name": name, "metadata": {"title": title}},
                "spaces": [], "assets": [], "revisions": [], "dependencies": [], "artifacts": [],
            }))
            .unwrap()
        };
        Ok(Response::new(ExportProjectResponse {
            schema_version: 1,
            project,
            document,
        }))
    }
}

#[tokio::test]
async fn validates_the_native_manifest_and_keeps_the_same_auth_and_errors() {
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let address = listener.local_addr().unwrap();
    let (stop, stopped) = tokio::sync::oneshot::channel();
    let server = tokio::spawn(
        tonic::transport::Server::builder()
            .add_service(ProjectExportServiceServer::new(Server))
            .serve_with_incoming_shutdown(TcpListenerStream::new(listener), async {
                let _ = stopped.await;
            }),
    );
    let client = Client::builder()
        .endpoint(format!("http://{address}"))
        .token("fixture-export")
        .use_discovery(false)
        .metadata("x-tenant-id", "tenant")
        .build()
        .await
        .unwrap();

    let manifest = client.export_project("film").await.unwrap();
    assert_eq!(
        (manifest.project.as_str(), manifest.snapshot_sequence),
        ("film", 42)
    );
    assert!(manifest.document.contains("The film"));
    assert!(client.export_project("large").await.unwrap().document.len() > 4 * 1024 * 1024);
    for project in ["mismatch", "partial"] {
        assert!(
            matches!(client.export_project(project).await, Err(Error::Rpc(status)) if status.code() == Code::DataLoss)
        );
    }
    assert!(
        matches!(client.export_project("unavailable").await, Err(Error::Rpc(status)) if status.code() == Code::Unimplemented)
    );
    assert!(matches!(
        client.export_project("").await,
        Err(Error::InvalidArgument(_))
    ));
    let _ = stop.send(());
    server.await.unwrap().unwrap();
}
