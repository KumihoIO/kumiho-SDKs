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
| `KUMIHO_FIREBASE_API_KEY` | Optional | Firebase Web API key used by the `kumiho-auth` helper. Pass it via the env var or `--api-key` flag when logging in. |
| `KUMIHO_TENANT_HINT` | Optional | Forces requests into a known tenant UUID when a user belongs to multiple tenants. The server still validates membership via Supabase. |

### Firebase token helper (`kumiho-auth`)

The Python package ships a small CLI that uses the Firebase Web API directly, so you do **not** need the Firebase CLI on every machine. After installing the editable package, run:

```bash
cd kumiho-python/python
pip install -e .[dev]
kumiho-auth login --api-key <firebase-web-api-key>
```

The flow prompts for your Firebase email/password, exchanges them for an ID + refresh token, and stores the credentials at `~/.kumiho/credentials.json`. It also writes the current ID token to `firebase_token.txt` in the repo root (or the path passed via `--token-file`) and ensures `.env.local` contains `KUMIHO_AUTH_TOKEN_FILE=<path>`. Subsequent runs of the CLI or `pytest` can refresh the token automatically:

```bash
kumiho-auth refresh
```

When `pytest` needs a live token and none of the env vars/files are set, it calls the same helper. If you are in a non-interactive environment, export `KUMIHO_AUTH_TOKEN` or run `kumiho-auth login` ahead of time so the cached credentials can be reused.

Ensure the Firebase UID tied to that token exists as an `owner` or `editor` inside Supabase `memberships`. The Rust server will deny RPCs until the control plane exposes that membership through `tenant_directory`. Supabase service keys are **not** required for the Python SDK—the server already hides the control-plane REST endpoint.

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

To explicitly exercise the full Firebase → Supabase → Neo4j path against a running server, target the `tests/test_live_e2e.py::test_firebase_supabase_neo4j_roundtrip` case:

```bash
cd kumiho-python
pytest tests/test_live_e2e.py -k roundtrip
```

This test creates real groups, products, versions, and resources via the gRPC client, so make sure your local server points at a disposable Neo4j database or uses unique names.

For details on how Firebase, Supabase, and the Rust server interact, see `docs/Firebase_control_plane.md` in the repo root.
