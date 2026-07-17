# Releasing the Kumiho SDKs

This repo publishes each SDK with its own tag-triggered workflow.

| SDK | Workflow | Tag pattern | Secret required |
|-----|----------|-------------|-----------------|
| Rust → crates.io | `.github/workflows/rust-publish.yml` | `rust-v*` | `CARGO_REGISTRY_TOKEN` |
| Go (tag-based) | `.github/workflows/go-release.yml` | `go/v*` | none (uses `GITHUB_TOKEN`) |
| Python → PyPI | `.github/workflows/sdk-publish.yml` | `sdk-v*` | existing PyPI setup |

CI for every PR (`sdk-ci.yml`) builds + tests both SDKs and verifies the Rust
crate **packages** cleanly (`cargo publish --dry-run`), so packaging breakage is
caught before you ever tag a release.

---

## 1. Rust → crates.io (needs a token)

### 1a. Get a crates.io API token

1. Sign in at <https://crates.io> with your GitHub account.
2. You must be an **owner** of the `kumiho` crate. The first publish claims the
   name; after that, add owners with
   `cargo owner --add <user-or-github:org:team> kumiho`.
3. Go to **Account Settings → API Tokens → New Token**.
   - Name: `kumiho-SDKs CI`.
   - Scopes: enable **`publish-update`** (and **`publish-new`** for the very
     first publish). Leave `yank`/`change-owners` off.
   - Crate scope: restrict to `kumiho` if the option is offered.
   - Expiry: set one (e.g. 1 year) and calendar a renewal.
4. Copy the token — it is shown **once**.

### 1b. Store it as a GitHub secret

The workflow runs in the `crates-io` environment, so store the token there
(more controllable than a plain repo secret):

1. Repo → **Settings → Environments → New environment** → name it `crates-io`.
2. (Recommended) Add a **Required reviewer** and restrict deployment to
   protected tags, so a publish can't run unreviewed.
3. In that environment → **Add secret**:
   - Name: `CARGO_REGISTRY_TOKEN`
   - Value: the token from step 1a.

> Prefer a repo-level secret instead? Settings → Secrets and variables →
> Actions → New repository secret, same name. Then you may drop the
> `environment: crates-io` line from `rust-publish.yml`.

### 1c. Cut a release

```bash
# bump rust/Cargo.toml version first (must equal the tag), commit, then:
git tag rust-v0.10.0
git push origin rust-v0.10.0
```

The workflow checks the tag matches `Cargo.toml`, runs `cargo publish
--dry-run`, then `cargo publish`. You can also run it manually from the Actions
tab (workflow_dispatch).

### ⚠️ Consumer caveat (protoc)

`build.rs` compiles `proto/kumiho.proto` with `tonic-build` at build time, so
**anyone depending on `kumiho` must have `protoc` installed**. To remove that
requirement later, either vendor protoc (add `protoc-bin-vendored` and point
`PROTOC` at it in `build.rs`) or commit the generated code and drop the
build-time codegen. Not required to publish, but worth doing for a smoother
consumer experience.

---

## 2. Go (no token)

Go has no central registry; the **git tag is the release**. Because the module
lives in the `go/` subdirectory (`module github.com/KumihoIO/kumiho-SDKs/go`),
the tag must be prefixed `go/`:

```bash
git tag go/v0.10.0
git push origin go/v0.10.0
```

`go-release.yml` then builds + tests at the tag and creates a GitHub Release
using the built-in `GITHUB_TOKEN` (no secret to configure). Consumers install
with:

```bash
go get github.com/KumihoIO/kumiho-SDKs/go@v0.10.0
```

---

## 3. Python → PyPI (already configured)

Unchanged — `sdk-publish.yml` publishes `kumiho` to PyPI on `sdk-v*` tags using
the existing setup. If it uses a `PYPI_API_TOKEN` secret, the same secret model
as the Rust token applies; if it uses PyPI **Trusted Publishing** (OIDC), no
secret is needed.

---

## Secrets summary

| Secret | Where | Used by | How to get it |
|--------|-------|---------|---------------|
| `CARGO_REGISTRY_TOKEN` | `crates-io` environment (or repo) | `rust-publish.yml` | crates.io → API Tokens (`publish-update`) |
| `GITHUB_TOKEN` | automatic | `go-release.yml`, all CI | provided by Actions, nothing to set |

## Version surface alignment (kumiho-memory)

Before tagging a kumiho-memory release, align every version surface —
`pyproject.toml` version, `kumiho_memory/__init__.py` `__version__`, the
README Status block (beta line + latest-release line), and the
`[project.urls]` links — so PyPI visitors never see stale versions or dead
links (issue #107).
