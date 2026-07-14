// Compiles the shared kumiho.proto into prost/tonic types at build time.
//
// The proto lives in the `proto/` git submodule (shared across all Kumiho
// SDKs); the published crates.io package carries the file directly. `protoc`
// is resolved from $PROTOC, then PATH, then the vendored binary (default
// `vendored-protoc` feature) — a fresh clone builds with zero system deps.
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let proto = "proto/kumiho.proto";
    println!("cargo:rerun-if-changed={proto}");
    println!("cargo:rerun-if-env-changed=CARGO_FEATURE_MOCK_SERVER");
    println!("cargo:rerun-if-env-changed=PROTOC");

    if !std::path::Path::new(proto).exists() {
        fail(
            "kumiho.proto not found — the proto git submodule is missing.\n\
             From the repository root run:\n\n    \
                 git submodule update --init rust/proto\n\n\
             (Not needed when building the published crates.io package.)",
        );
    }

    if std::env::var_os("PROTOC").is_none() && protoc_on_path().is_none() {
        #[cfg(feature = "vendored-protoc")]
        {
            let vendored = protoc_bin_vendored::protoc_bin_path()?;
            std::env::set_var("PROTOC", &vendored);
        }
        #[cfg(not(feature = "vendored-protoc"))]
        fail(
            "protoc not found. Install it (apt: protobuf-compiler, brew/choco:\n\
             protobuf), set $PROTOC, or build with the default `vendored-protoc`\n\
             feature enabled.",
        );
    }

    // Server stubs are only needed by the in-process integration tests, which
    // enable the `mock-server` feature; SDK consumers get client-only codegen.
    let build_server = std::env::var("CARGO_FEATURE_MOCK_SERVER").is_ok();
    tonic_build::configure()
        .build_server(build_server)
        .build_client(true)
        .compile_protos(&[proto], &["proto"])?;
    Ok(())
}

fn protoc_on_path() -> Option<std::path::PathBuf> {
    let exe = if cfg!(windows) {
        "protoc.exe"
    } else {
        "protoc"
    };
    std::env::split_paths(&std::env::var_os("PATH")?)
        .map(|dir| dir.join(exe))
        .find(|p| p.is_file())
}

fn fail(msg: &str) -> ! {
    eprintln!("\n────────────────────────────────────────────────────────────");
    eprintln!("{msg}");
    eprintln!("────────────────────────────────────────────────────────────\n");
    std::process::exit(1);
}
