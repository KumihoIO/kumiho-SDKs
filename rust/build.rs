// Compiles the shared kumiho.proto into prost/tonic types at build time.
//
// The proto lives in the `proto/` git submodule (shared across all Kumiho
// SDKs). Requires `protoc` to be installed and on PATH.
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let proto = "proto/kumiho.proto";
    println!("cargo:rerun-if-changed={proto}");
    println!("cargo:rerun-if-env-changed=CARGO_FEATURE_MOCK_SERVER");
    // Server stubs are only needed by the in-process integration tests, which
    // enable the `mock-server` feature; SDK consumers get client-only codegen.
    let build_server = std::env::var("CARGO_FEATURE_MOCK_SERVER").is_ok();
    tonic_build::configure()
        .build_server(build_server)
        .build_client(true)
        .compile_protos(&[proto], &["proto"])?;
    Ok(())
}
