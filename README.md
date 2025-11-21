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
| `KUMIHO_TENANT_HINT` | Deprecated | Legacy override for forcing a tenant UUID. Auto-discovery now resolves the tenant from Supabase memberships, so the variable is ignored. |
| `KUMIHO_CONTROL_PLANE_URL` | Optional | Base URL for the control plane. Defaults to `https://kumiho.io`. The discovery helper calls `<base>/api/discovery/tenant`. |
| `KUMIHO_DISCOVERY_CACHE_FILE` | Optional | Path to persist discovery responses. Defaults to `~/.kumiho/discovery-cache.json`. |
| `KUMIHO_DISCOVERY_TIMEOUT_SECONDS` | Optional | HTTP timeout when contacting the discovery endpoint. Defaults to `10`. |

### Bootstrap via the discovery endpoint

The Phase 4 control plane exposes `POST /api/discovery/tenant`, which returns the
tenant ID, region routing info, and cache-control metadata. The Python SDK ships
`kumiho.client_from_discovery` to call this endpoint, persist the payload, and
refresh it when the control plane says the data is stale.

```python
from kumiho import client_from_discovery

# Reuses KUMIHO_AUTH_TOKEN / kumiho-auth token file for the Firebase ID token.
client = client_from_discovery()

# All subsequent calls reuse the cached region info until refresh_after_seconds.
group = client.create_group("demo-project")
```

The helper automatically:

1. Loads a Firebase ID token from `KUMIHO_AUTH_TOKEN` or the `kumiho-auth` cache.
2. Checks `~/.kumiho/discovery-cache.json` (configurable via
	`KUMIHO_DISCOVERY_CACHE_FILE`) for a non-expired entry keyed by the provided tenant hint (or a default record when no hint is supplied).
3. Refreshes the cache once the control plane’s `refresh_after_seconds` deadline
	passes, falling back to the cached response if the control plane is
	temporarily unavailable.
4. Injects the resolved `x-tenant-id` metadata and gRPC target/authority so the
	`Client` instance is immediately ready to talk to the correct regional server.

Set `force_refresh=True` when calling `client_from_discovery` to ignore the cache
entirely, or pass a custom `cache_path` if your environment needs an alternate
location.

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

If `KUMIHO_AUTH_TOKEN` (or the file fallback) is not configured, the fixtures automatically skip the live scenarios and print a message describing the required environment. Once the token is present, the suite will use it to call the server with `Authorization: Bearer <token>` headers; the multi-tenant routing is resolved automatically via discovery.

To explicitly exercise the full Firebase → Supabase → Neo4j path against a running server, target the `tests/test_live_e2e.py::test_firebase_supabase_neo4j_roundtrip` case:

```bash
cd kumiho-python
pytest tests/test_live_e2e.py -k roundtrip
```

This test creates real groups, products, versions, and resources via the gRPC client, so make sure your local server points at a disposable Neo4j database or uses unique names.

For details on how Firebase, Supabase, and the Rust server interact, see `docs/Firebase_control_plane.md` in the repo root.
