// Compiles the shared kumiho.proto into prost/tonic types at build time.
//
// The proto lives in the `proto/` git submodule (shared across all Kumiho
// SDKs). Requires `protoc` to be installed and on PATH.
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let proto = "proto/kumiho.proto";
    println!("cargo:rerun-if-changed={proto}");
    tonic_build::configure()
        .build_server(false)
        .build_client(true)
        .compile_protos(&[proto], &["proto"])?;
    Ok(())
}
