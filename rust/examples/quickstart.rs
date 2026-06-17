//! End-to-end quickstart for the Kumiho Rust SDK.
//!
//! Run with a reachable server, e.g.:
//!   KUMIHO_SERVER_ENDPOINT=localhost:8080 cargo run --example quickstart
//!
//! With cached credentials (`kumiho-cli login`) discovery is automatic:
//!   cargo run --example quickstart
#![allow(clippy::result_large_err)]

use kumiho::{Client, EdgeType};
use tokio_stream::StreamExt;

#[tokio::main]
async fn main() -> kumiho::Result<()> {
    // Connect: explicit endpoint, or `Client::auto()` for discovery.
    let client = match std::env::var("KUMIHO_SERVER_ENDPOINT") {
        Ok(ep) => Client::connect(ep).await?,
        Err(_) => Client::auto().await?,
    };

    // Project -> space -> item -> revision -> artifact.
    let project = client
        .create_project("rust-demo", "Kumiho Rust SDK demo")
        .await?;
    println!("project: {} ({})", project.name, project.project_id);

    let space = project.create_space("characters", None).await?;
    let hero = space.create_item("hero", "model").await?;
    println!("item:    {}", hero.kref);

    let rev = hero.create_revision(None, 0).await?;
    rev.create_artifact("mesh", "/assets/hero.fbx", None)
        .await?;
    rev.set_default_artifact("mesh").await?;
    rev.tag("approved").await?;
    println!("revision {} tagged, default artifact set", rev.number);

    // Dependency edge to another revision.
    let texture_item = space.create_item("skin", "texture").await?;
    let texture_rev = texture_item.create_revision(None, 0).await?;
    rev.create_edge(&texture_rev, EdgeType::DEPENDS_ON, None)
        .await?;

    // Impact analysis.
    let impacted = texture_rev.analyze_impact(None, 10, 100).await?;
    println!("{} revisions depend on the texture", impacted.len());

    // Full-text search.
    let hits = client
        .search(
            "hero",
            "rust-demo",
            "",
            false,
            false,
            false,
            0.0,
            None,
            None,
        )
        .await?;
    for hit in hits.iter() {
        println!("hit: {} (score {:.2})", hit.item.kref, hit.score);
    }

    // Tail a few live events (best-effort).
    if let Ok(mut stream) = client
        .event_stream("revision.*", "", None, None, false)
        .await
    {
        if let Some(Ok(ev)) = stream.next().await {
            println!("event: {} -> {}", ev.routing_key, ev.kref);
        }
    }

    Ok(())
}
