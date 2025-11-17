# Kumiho Python SDK

This package provides the typed Python bindings for the Kumiho gRPC API. It mirrors the protobuf contract and ships a pytest harness for live workflows that hit the Rust server + Neo4j data plane.

## Install locally

From the repo root run:

```bash
cd kumiho-python/python
pip install -e .[dev]
```

The editable install exposes the `kumiho` package and pulls in `pytest` for the test suite. Any shell that runs the samples or tests should activate the same virtual environment where you installed the package.

## Auth + tenancy prerequisites

Kumiho relies on Firebase Authentication for identity and Supabase Postgres for the admin control plane. The Python client only needs a Firebase ID token that belongs to a Supabase membership: the server resolves the tenant + roles via the `tenant_directory` REST view.

| Variable | Required | Description |
| --- | --- | --- |
| `KUMIHO_SERVER_ENDPOINT` | Optional | `host:port` or `https://host` for the Rust server. Defaults to `localhost:8080`. |
| `KUMIHO_AUTH_TOKEN` | Yes for live calls | Firebase ID token (JWT). Obtain it via the Firebase SDK, `firebase login:ci`, or any custom auth flow. |
| `KUMIHO_AUTH_TOKEN_FILE` | Optional | Path to a file that contains the Firebase ID token. Useful for `firebase_token.txt` generated in the repo root. |
| `KUMIHO_TENANT_HINT` | Optional | Forces requests into a known tenant UUID when a user belongs to multiple tenants. The server still validates membership via Supabase. |

Steps to prepare a token for local testing:

1. `npm install -g firebase-tools` (if you have not already).
2. Run `firebase login:ci` with the same Firebase project configured in `config/default.toml`. The command prints a long-lived token.
3. Save the token into `firebase_token.txt` in the repo root or another secure file, then either export `KUMIHO_AUTH_TOKEN` or point `KUMIHO_AUTH_TOKEN_FILE` at the file.
4. Ensure the Firebase UID tied to that token exists as an `owner` or `editor` inside Supabase `memberships`. The Rust server will deny RPCs until the control plane exposes that membership through `tenant_directory`.

Supabase service keys are **not** required for the Python SDK—the server already hides the control-plane REST endpoint. You only need the Firebase ID token described above.

## Running the tests

The test suite mixes mocked unit tests and live integration flows:

* Unit tests use monkeypatched stubs and run anywhere.
* Integration tests require a running Rust server, a Neo4j instance seeded for tests, and a Firebase token that belongs to a Supabase tenant.

Run the tests from `kumiho-python`:

```bash
cd kumiho-python
pytest
```

If `KUMIHO_AUTH_TOKEN` (or the file fallback) is not configured, the fixtures automatically skip the live scenarios and print a message describing the required environment. Once the token is present, the suite will use it to call the server with `Authorization: Bearer <token>` headers and will propagate any optional `KUMIHO_TENANT_HINT` metadata as well.

For details on how Firebase, Supabase, and the Rust server interact, see `docs/Firebase_control_plane.md` in the repo root.
