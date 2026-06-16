//! The low-level gRPC client and connection bootstrapping.
//!
//! [`Client`] wraps every `KumihoService` RPC and is cheaply cloneable (the
//! underlying channel is shared). Domain objects ([`crate::Project`], etc.)
//! hold a `Client` and delegate to it. Mirrors Python's `_Client`.

use crate::edge::{
    Edge, EdgeDirection, ImpactedRevision, PathStep, RevisionPath, ShortestPathResult,
    TraversalResult,
};
use crate::error::{Error, Result};
use crate::kref::Kref;
use crate::models::artifact::Artifact;
use crate::models::bundle::{Bundle, BundleMember, BundleRevisionHistory, RESERVED_KINDS};
use crate::models::event::{Event, EventCapabilities};
use crate::models::item::Item;
use crate::models::project::Project;
use crate::models::revision::Revision;
use crate::models::space::Space;
use crate::pb;
use std::collections::HashMap;
use std::time::Duration;
use tokio_stream::{Stream, StreamExt};
use tonic::metadata::{AsciiMetadataKey, AsciiMetadataValue};
use tonic::service::interceptor::InterceptedService;
use tonic::transport::{Channel, ClientTlsConfig, Endpoint};

type GrpcClient =
    pb::kumiho_service_client::KumihoServiceClient<InterceptedService<Channel, KumihoInterceptor>>;

const DEFAULT_RPC_TIMEOUT_SECS: f64 = 30.0;
const RETRY_MAX_ATTEMPTS: u32 = 3;
const RETRY_BASE_DELAY_MS: u64 = 500;
const RETRY_MAX_DELAY_MS: u64 = 5000;

fn retry_max_attempts() -> u32 {
    std::env::var("KUMIHO_GRPC_RETRY_MAX_ATTEMPTS")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(RETRY_MAX_ATTEMPTS)
}

fn rpc_timeout() -> Option<Duration> {
    let secs = std::env::var("KUMIHO_RPC_TIMEOUT_SECS")
        .ok()
        .and_then(|v| v.parse::<f64>().ok())
        .unwrap_or(DEFAULT_RPC_TIMEOUT_SECS);
    if secs <= 0.0 {
        None
    } else {
        Some(Duration::from_secs_f64(secs))
    }
}

fn backoff(attempt: u32) -> Duration {
    let base = RETRY_BASE_DELAY_MS * (1u64 << (attempt - 1).min(16));
    let capped = base.min(RETRY_MAX_DELAY_MS);
    let jitter = (rand::random::<f64>() * (capped as f64) * 0.25) as u64;
    Duration::from_millis(capped + jitter)
}

fn is_transient(code: tonic::Code) -> bool {
    matches!(
        code,
        tonic::Code::Unavailable
            | tonic::Code::DeadlineExceeded
            | tonic::Code::Internal
            | tonic::Code::ResourceExhausted
    )
}

/// Runs a unary RPC with transient-failure retry + per-call deadline.
macro_rules! unary {
    ($self:ident, $method:ident, $msg:expr) => {{
        let msg = $msg;
        let max = $self.max_attempts;
        let mut attempt: u32 = 0;
        loop {
            let mut grpc = $self.grpc.clone();
            let mut request = tonic::Request::new(msg.clone());
            if let Some(d) = $self.rpc_timeout {
                request.set_timeout(d);
            }
            match grpc.$method(request).await {
                Ok(r) => break Ok::<_, crate::Error>(r.into_inner()),
                Err(status) => {
                    attempt += 1;
                    if is_transient(status.code()) && attempt < max {
                        tokio::time::sleep(backoff(attempt)).await;
                        continue;
                    }
                    break Err(crate::Error::Rpc(status));
                }
            }
        }
    }};
}

// ---- interceptor: injects auth/tenant metadata + a per-call correlation id ----

#[derive(Clone)]
pub(crate) struct KumihoInterceptor {
    metadata: Vec<(String, String)>,
}

impl tonic::service::Interceptor for KumihoInterceptor {
    fn call(
        &mut self,
        mut req: tonic::Request<()>,
    ) -> std::result::Result<tonic::Request<()>, tonic::Status> {
        let md = req.metadata_mut();
        for (k, v) in &self.metadata {
            if let (Ok(key), Ok(val)) = (
                AsciiMetadataKey::from_bytes(k.as_bytes()),
                AsciiMetadataValue::try_from(v.as_str()),
            ) {
                md.insert(key, val);
            }
        }
        let cid = format!("kumiho-{}", uuid::Uuid::new_v4().simple());
        if let Ok(val) = AsciiMetadataValue::try_from(cid.as_str()) {
            md.insert("x-correlation-id", val);
        }
        Ok(req)
    }
}

/// A page of list results carrying an optional pagination cursor.
#[derive(Debug, Clone)]
pub struct Page<T> {
    /// The items on this page.
    pub items: Vec<T>,
    /// Cursor for the next page, if more results exist.
    pub next_cursor: Option<String>,
    /// Total count across all pages, if the server reported it.
    pub total_count: Option<i32>,
}

impl<T> std::ops::Deref for Page<T> {
    type Target = [T];
    fn deref(&self) -> &[T] {
        &self.items
    }
}

impl<T> IntoIterator for Page<T> {
    type Item = T;
    type IntoIter = std::vec::IntoIter<T>;
    fn into_iter(self) -> Self::IntoIter {
        self.items.into_iter()
    }
}

fn page_from<T>(items: Vec<T>, pagination: Option<pb::PaginationResponse>) -> Page<T> {
    match pagination {
        Some(p) => Page {
            items,
            next_cursor: (!p.next_cursor.is_empty()).then_some(p.next_cursor),
            total_count: Some(p.total_count),
        },
        None => Page {
            items,
            next_cursor: None,
            total_count: None,
        },
    }
}

/// A revision scored against a query by the server.
#[derive(Debug, Clone)]
pub struct ScoredRevision {
    /// The revision kref.
    pub kref: String,
    /// Relevance score (0.0–1.0).
    pub score: f32,
    /// How the score was computed: `"vector"`, `"fulltext"`, or `"hybrid"`.
    pub score_method: String,
}

/// A full-text search hit: the matched item plus its relevance score.
#[derive(Debug, Clone)]
pub struct SearchResult {
    /// The matched item.
    pub item: Item,
    /// Relevance score from the search index (higher is better).
    pub score: f32,
    /// Where the match was found: `"item"`, `"revision"`, `"artifact"`.
    pub matched_in: Vec<String>,
}

/// Tenant usage and limits.
#[derive(Debug, Clone)]
pub struct TenantUsage {
    pub node_count: i64,
    pub node_limit: i64,
    pub tenant_id: String,
}

/// Builder for [`Client`] with full control over endpoint, auth and routing.
#[derive(Default)]
pub struct ClientBuilder {
    endpoint: Option<String>,
    token: Option<String>,
    tenant_hint: Option<String>,
    use_discovery: Option<bool>,
    force_discovery_refresh: bool,
    metadata: Vec<(String, String)>,
}

impl ClientBuilder {
    /// Explicit gRPC endpoint (`host:port`, `https://host`, `grpcs://host:port`).
    pub fn endpoint(mut self, ep: impl Into<String>) -> Self {
        self.endpoint = Some(ep.into());
        self
    }
    /// Explicit bearer token (otherwise loaded from env / `~/.kumiho`).
    pub fn token(mut self, token: impl Into<String>) -> Self {
        self.token = Some(token.into());
        self
    }
    /// Tenant slug/id hint for discovery or the `x-tenant-id` header.
    pub fn tenant_hint(mut self, hint: impl Into<String>) -> Self {
        self.tenant_hint = Some(hint.into());
        self
    }
    /// Force control-plane discovery on/off (default: on when a token exists
    /// and no explicit endpoint is given).
    pub fn use_discovery(mut self, yes: bool) -> Self {
        self.use_discovery = Some(yes);
        self
    }
    /// Bypass the discovery cache and re-fetch routing.
    pub fn force_discovery_refresh(mut self, yes: bool) -> Self {
        self.force_discovery_refresh = yes;
        self
    }
    /// Add a static metadata header sent on every RPC.
    pub fn metadata(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.metadata.push((key.into(), value.into()));
        self
    }

    /// Resolve routing/auth and build the [`Client`].
    pub async fn build(mut self) -> Result<Client> {
        // 1. Resolve token.
        let mut token = match self.token.take() {
            Some(t) => Some(t),
            None => crate::token_loader::load_bearer_token().map_err(Error::InvalidArgument)?,
        };

        // 2. No endpoint + no token -> try a local self-hosted CE server.
        if self.endpoint.is_none() && token.is_none() {
            if let Some(local) = crate::discovery::resolve_local_ce_endpoint().await? {
                self.endpoint = Some(local);
                self.use_discovery = Some(false);
            }
        }

        let mut metadata = self.metadata.clone();

        // 3. Discovery (when no explicit endpoint, enabled, token present).
        let discovery_enabled = self
            .use_discovery
            .unwrap_or_else(|| !env_flag("KUMIHO_DISABLE_AUTO_DISCOVERY"));
        if self.endpoint.is_none() && discovery_enabled {
            if let Some(tok) = token.clone() {
                match crate::discovery::resolve(
                    &tok,
                    self.tenant_hint.as_deref(),
                    self.force_discovery_refresh,
                )
                .await
                {
                    Ok(record) => {
                        self.endpoint = Some(record.target());
                        metadata.push(("x-tenant-id".into(), record.tenant_id.clone()));
                    }
                    Err(_) => {
                        if let Some(hint) = &self.tenant_hint {
                            metadata.push(("x-tenant-id".into(), hint.clone()));
                        }
                    }
                }
            } else if let Some(hint) = &self.tenant_hint {
                metadata.push(("x-tenant-id".into(), hint.clone()));
            }
        }

        // 4. Fall back to env / localhost.
        let target = self.endpoint.clone().unwrap_or_else(|| {
            std::env::var("KUMIHO_SERVER_ENDPOINT")
                .or_else(|_| std::env::var("KUMIHO_SERVER_ADDRESS"))
                .unwrap_or_else(|_| "localhost:8080".to_string())
        });

        // 5. Normalize + build channel.
        let (host, port, mut use_tls) = normalize_target(&target)?;
        if let Ok(v) = std::env::var("KUMIHO_SERVER_USE_TLS") {
            use_tls = matches!(v.to_ascii_lowercase().as_str(), "1" | "true" | "yes");
        }
        let channel = build_channel(&host, port, use_tls).await?;

        // 6. Auth header.
        if let Some(tok) = token.take() {
            metadata.push(("authorization".into(), format!("Bearer {tok}")));
        }

        let interceptor = KumihoInterceptor { metadata };
        let grpc =
            pb::kumiho_service_client::KumihoServiceClient::with_interceptor(channel, interceptor)
                .max_decoding_message_size(64 * 1024 * 1024);

        Ok(Client {
            grpc,
            max_attempts: retry_max_attempts(),
            rpc_timeout: rpc_timeout(),
        })
    }
}

// Mirrors the Python _Client._env_flag used for KUMIHO_DISABLE_AUTO_DISCOVERY:
// an unset variable is false, but any set value other than 0/false/no (including
// an empty string) is true.
fn env_flag(name: &str) -> bool {
    std::env::var(name)
        .map(|v| !matches!(v.trim().to_ascii_lowercase().as_str(), "0" | "false" | "no"))
        .unwrap_or(false)
}

fn normalize_target(raw: &str) -> Result<(String, u16, bool)> {
    let target = raw.trim();
    if target.is_empty() {
        return Err(Error::InvalidArgument("endpoint cannot be empty".into()));
    }
    let (scheme, rest) = match target.split_once("://") {
        Some((s, r)) => (s.to_ascii_lowercase(), r),
        None => (String::new(), target),
    };
    let hostport = rest.split('/').next().unwrap_or(rest);
    let (host, port_opt) = match hostport.rsplit_once(':') {
        Some((h, p)) => (h.to_string(), p.parse::<u16>().ok()),
        None => (hostport.to_string(), None),
    };
    if host.is_empty() {
        return Err(Error::InvalidArgument(format!("invalid endpoint: {raw}")));
    }
    let tls_scheme = matches!(scheme.as_str(), "https" | "grpcs");
    let port = port_opt.unwrap_or_else(|| match scheme.as_str() {
        "https" | "grpcs" => 443,
        "http" | "grpc" => 80,
        _ => 8080,
    });
    let use_tls = tls_scheme || port == 443;
    Ok((host, port, use_tls))
}

async fn build_channel(host: &str, port: u16, use_tls: bool) -> Result<Channel> {
    let scheme = if use_tls { "https" } else { "http" };
    let url = format!("{scheme}://{host}:{port}");
    let mut endpoint = Endpoint::from_shared(url)
        .map_err(|e| Error::InvalidArgument(format!("invalid endpoint: {e}")))?
        .http2_keep_alive_interval(Duration::from_secs(30))
        .keep_alive_timeout(Duration::from_secs(10))
        .keep_alive_while_idle(true);

    if use_tls {
        let authority =
            std::env::var("KUMIHO_SERVER_AUTHORITY").unwrap_or_else(|_| host.to_string());
        let mut tls = ClientTlsConfig::new()
            .with_native_roots()
            .domain_name(authority);
        if let Ok(ca_path) = std::env::var("KUMIHO_SERVER_CA_FILE") {
            if !ca_path.is_empty() {
                let pem = std::fs::read(&ca_path)?;
                tls = tls.ca_certificate(tonic::transport::Certificate::from_pem(pem));
            }
        }
        endpoint = endpoint.tls_config(tls)?;
    }
    Ok(endpoint.connect_lazy())
}

/// Low-level async gRPC client for Kumiho. Clone freely; the channel is shared.
#[derive(Clone)]
pub struct Client {
    grpc: GrpcClient,
    // Retry/deadline config, resolved once at build time rather than re-reading
    // the environment on every RPC.
    max_attempts: u32,
    rpc_timeout: Option<Duration>,
}

impl Client {
    /// Connect to an explicit endpoint, loading any cached token.
    ///
    /// ```no_run
    /// # async fn f() -> kumiho::Result<()> {
    /// let client = kumiho::Client::connect("https://us-central.kumiho.cloud").await?;
    /// # Ok(()) }
    /// ```
    pub async fn connect(endpoint: impl Into<String>) -> Result<Client> {
        ClientBuilder::default().endpoint(endpoint).build().await
    }

    /// Auto-configure following the standard Kumiho bootstrap chain:
    ///
    /// 1. Load a bearer token (`KUMIHO_AUTH_TOKEN`, else `~/.kumiho/kumiho_authentication.json`).
    /// 2. **Token present** → control-plane discovery resolves the tenant's
    ///    regional cloud kumiho-server (errors propagate).
    /// 3. **No token** → probe the loopback self-hosted CE server and use it.
    /// 4. Neither available → returns an error.
    ///
    /// For explicit endpoints or a localhost dev fallback, use
    /// [`Client::connect`] or [`Client::builder`].
    pub async fn auto() -> Result<Client> {
        Self::auto_with_tenant(None).await
    }

    /// Like [`Client::auto`], but pins discovery to a specific tenant slug/id.
    pub async fn auto_with_tenant(tenant_hint: Option<&str>) -> Result<Client> {
        let token = crate::token_loader::load_bearer_token().map_err(Error::InvalidArgument)?;
        if let Some(tok) = token {
            // Token present -> control-plane discovery -> tenant's cloud server.
            let record = crate::discovery::resolve(&tok, tenant_hint, false).await?;
            return ClientBuilder::default()
                .endpoint(record.target())
                .token(tok)
                .use_discovery(false)
                .metadata("x-tenant-id", record.tenant_id)
                .build()
                .await;
        }
        // No token -> fall back to a local self-hosted CE server if present.
        if let Some(local) = crate::discovery::resolve_local_ce_endpoint().await? {
            return ClientBuilder::default()
                .endpoint(local)
                .use_discovery(false)
                .build()
                .await;
        }
        Err(Error::Discovery(
            "no credentials found: set KUMIHO_AUTH_TOKEN or run `kumiho-cli login`; \
             no local self-hosted CE server detected on loopback"
                .into(),
        ))
    }

    /// Build a tokenless client pointed at a locally-detected self-hosted CE
    /// server, or `None` if none is detected. Mirrors Python `client_from_local_ce`.
    pub async fn from_local_ce() -> Result<Option<Client>> {
        match crate::discovery::resolve_local_ce_endpoint().await? {
            Some(local) => Ok(Some(
                ClientBuilder::default()
                    .endpoint(local)
                    .use_discovery(false)
                    .build()
                    .await?,
            )),
            None => Ok(None),
        }
    }

    /// Start a [`ClientBuilder`] for full control.
    pub fn builder() -> ClientBuilder {
        ClientBuilder::default()
    }

    // ----------------------------------------------------------------- Projects

    /// Create a new project.
    pub async fn create_project(
        &self,
        name: impl Into<String>,
        description: impl Into<String>,
    ) -> Result<Project> {
        let req = pb::CreateProjectRequest {
            name: name.into(),
            description: description.into(),
        };
        match unary!(self, create_project, req) {
            Ok(resp) => Ok(Project::from_pb(resp, self.clone())),
            Err(Error::Rpc(s)) if s.code() == tonic::Code::ResourceExhausted => {
                Err(Error::ProjectLimit(s.message().to_string()))
            }
            Err(e) => Err(e),
        }
    }

    /// List all projects accessible to the current user.
    pub async fn get_projects(&self) -> Result<Vec<Project>> {
        let resp = unary!(self, get_projects, pb::GetProjectsRequest {})?;
        Ok(resp
            .projects
            .into_iter()
            .map(|p| Project::from_pb(p, self.clone()))
            .collect())
    }

    /// Get a project by name, or `None` if not found.
    pub async fn get_project(&self, name: &str) -> Result<Option<Project>> {
        Ok(self
            .get_projects()
            .await?
            .into_iter()
            .find(|p| p.name == name))
    }

    /// Delete (force=true) or deprecate a project.
    pub async fn delete_project(&self, project_id: &str, force: bool) -> Result<()> {
        let req = pb::DeleteProjectRequest {
            project_id: project_id.to_string(),
            force,
        };
        unary!(self, delete_project, req)?;
        Ok(())
    }

    /// Update a project's description and/or public-access flag.
    pub async fn update_project(
        &self,
        project_id: &str,
        allow_public: Option<bool>,
        description: Option<String>,
    ) -> Result<Project> {
        let req = pb::UpdateProjectRequest {
            project_id: project_id.to_string(),
            allow_public,
            description,
        };
        let resp = unary!(self, update_project, req)?;
        Ok(Project::from_pb(resp, self.clone()))
    }

    // ------------------------------------------------------------------- Spaces

    /// Create a space under `parent_path`.
    pub async fn create_space(&self, parent_path: &str, space_name: &str) -> Result<Space> {
        let req = pb::CreateSpaceRequest {
            parent_path: parent_path.to_string(),
            space_name: space_name.to_string(),
            exists_error: false,
        };
        let resp = unary!(self, create_space, req)?;
        Ok(Space::from_pb(resp, self.clone()))
    }

    /// Get a space by path or kref.
    pub async fn get_space(&self, path: &str) -> Result<Space> {
        let req = pb::GetSpaceRequest {
            path_or_kref: path.to_string(),
        };
        let resp = unary!(self, get_space, req)?;
        Ok(Space::from_pb(resp, self.clone()))
    }

    /// List child spaces under `parent_path`.
    pub async fn get_child_spaces(
        &self,
        parent_path: &str,
        recursive: bool,
        page_size: Option<i32>,
        cursor: Option<String>,
    ) -> Result<Page<Space>> {
        let req = pb::GetChildSpacesRequest {
            parent_path: parent_path.to_string(),
            recursive,
            pagination: make_pagination(page_size, cursor),
        };
        let resp = unary!(self, get_child_spaces, req)?;
        let items = resp
            .spaces
            .into_iter()
            .map(|s| Space::from_pb(s, self.clone()))
            .collect();
        Ok(page_from(items, resp.pagination))
    }

    /// Replace/merge a space's metadata.
    pub async fn update_space_metadata(
        &self,
        kref: &Kref,
        metadata: HashMap<String, String>,
    ) -> Result<Space> {
        let req = pb::UpdateMetadataRequest {
            kref: Some(kref.to_pb()),
            metadata,
        };
        let resp = unary!(self, update_space_metadata, req)?;
        Ok(Space::from_pb(resp, self.clone()))
    }

    // -------------------------------------------------------------------- Items

    /// Create an item. Rejects the reserved `bundle` kind (use [`Client::create_bundle`]).
    pub async fn create_item(
        &self,
        parent_path: &str,
        item_name: &str,
        kind: &str,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Item> {
        if RESERVED_KINDS.contains(&kind.to_ascii_lowercase().as_str()) {
            return Err(Error::ReservedKind(kind.to_string()));
        }
        let req = pb::CreateItemRequest {
            parent_path: parent_path.to_string(),
            item_name: item_name.to_string(),
            kind: kind.to_string(),
            exists_error: false,
        };
        let resp = unary!(self, create_item, req)?;
        let item = Item::from_pb(resp, self.clone());
        if let Some(md) = metadata {
            if !md.is_empty() {
                return self.update_item_metadata(&item.kref, md).await;
            }
        }
        Ok(item)
    }

    /// Get an item by parent path, name and kind.
    pub async fn get_item(&self, parent_path: &str, item_name: &str, kind: &str) -> Result<Item> {
        let req = pb::GetItemRequest {
            parent_path: parent_path.to_string(),
            item_name: item_name.to_string(),
            kind: kind.to_string(),
        };
        let resp = unary!(self, get_item, req)?;
        Ok(Item::from_pb(resp, self.clone()))
    }

    /// Get an item by its kref URI.
    pub async fn get_item_by_kref(&self, kref_uri: &str) -> Result<Item> {
        let (parent_path, name, kind) = split_item_kref(kref_uri)?;
        self.get_item(&parent_path, &name, &kind).await
    }

    /// Get a bundle by its kref URI (verifies kind == `bundle`).
    pub async fn get_bundle_by_kref(&self, kref_uri: &str) -> Result<Bundle> {
        let (parent_path, name, kind) = split_item_kref(kref_uri)?;
        if kind != "bundle" {
            return Err(Error::InvalidArgument(format!(
                "'{kref_uri}' is not a bundle (kind='{kind}')"
            )));
        }
        let req = pb::GetItemRequest {
            parent_path,
            item_name: name,
            kind: "bundle".into(),
        };
        let resp = unary!(self, get_item, req)?;
        Bundle::from_pb(resp, self.clone())
    }

    /// List items in a space with optional filters/pagination.
    pub async fn get_items(
        &self,
        parent_path: &str,
        item_name_filter: &str,
        kind_filter: &str,
        page_size: Option<i32>,
        cursor: Option<String>,
        include_deprecated: bool,
    ) -> Result<Page<Item>> {
        let req = pb::GetItemsRequest {
            parent_path: parent_path.to_string(),
            item_name_filter: item_name_filter.to_string(),
            kind_filter: kind_filter.to_string(),
            pagination: make_pagination(page_size, cursor),
            include_deprecated,
        };
        let resp = unary!(self, get_items, req)?;
        let items = resp
            .items
            .into_iter()
            .map(|p| Item::from_pb(p, self.clone()))
            .collect();
        Ok(page_from(items, resp.pagination))
    }

    /// Search items across the system by context/name/kind filters.
    pub async fn item_search(
        &self,
        context_filter: &str,
        item_name_filter: &str,
        kind_filter: &str,
        page_size: Option<i32>,
        cursor: Option<String>,
        include_deprecated: bool,
    ) -> Result<Page<Item>> {
        let req = pb::ItemSearchRequest {
            context_filter: context_filter.to_string(),
            item_name_filter: item_name_filter.to_string(),
            kind_filter: kind_filter.to_string(),
            pagination: make_pagination(page_size, cursor),
            include_deprecated,
        };
        let resp = unary!(self, item_search, req)?;
        let items = resp
            .items
            .into_iter()
            .map(|p| Item::from_pb(p, self.clone()))
            .collect();
        Ok(page_from(items, resp.pagination))
    }

    /// Full-text fuzzy search returning ranked [`SearchResult`]s.
    #[allow(clippy::too_many_arguments)]
    pub async fn search(
        &self,
        query: &str,
        context_filter: &str,
        kind_filter: &str,
        include_deprecated: bool,
        include_revision_metadata: bool,
        include_artifact_metadata: bool,
        min_score: f32,
        page_size: Option<i32>,
        cursor: Option<String>,
    ) -> Result<Page<SearchResult>> {
        let req = pb::SearchRequest {
            query: query.to_string(),
            context_filter: context_filter.to_string(),
            kind_filter: kind_filter.to_string(),
            include_deprecated,
            pagination: make_pagination(page_size, cursor),
            min_score,
            include_revision_metadata,
            include_artifact_metadata,
        };
        let resp = unary!(self, search, req)?;
        let items = resp
            .results
            .into_iter()
            .filter_map(|r| {
                r.item.map(|it| SearchResult {
                    item: Item::from_pb(it, self.clone()),
                    score: r.score,
                    matched_in: r.matched_in,
                })
            })
            .collect();
        Ok(page_from(items, resp.pagination))
    }

    /// Score specific revisions against a query (server-side embeddings).
    pub async fn score_revisions(
        &self,
        query: &str,
        revision_krefs: &[String],
        score_fields: Option<Vec<String>>,
    ) -> Result<Vec<ScoredRevision>> {
        let req = pb::ScoreRevisionsRequest {
            query: query.to_string(),
            revision_krefs: revision_krefs
                .iter()
                .map(|k| pb::Kref { uri: k.clone() })
                .collect(),
            score_fields: score_fields.unwrap_or_default(),
        };
        let resp = unary!(self, score_revisions, req)?;
        Ok(resp
            .scored_revisions
            .into_iter()
            .map(|sr| ScoredRevision {
                kref: sr.kref.map(|k| k.uri).unwrap_or_default(),
                score: sr.score,
                score_method: sr.score_method,
            })
            .collect())
    }

    /// Merge metadata into an item.
    pub async fn update_item_metadata(
        &self,
        kref: &Kref,
        metadata: HashMap<String, String>,
    ) -> Result<Item> {
        let req = pb::UpdateMetadataRequest {
            kref: Some(kref.to_pb()),
            metadata,
        };
        let resp = unary!(self, update_item_metadata, req)?;
        Ok(Item::from_pb(resp, self.clone()))
    }

    // ---------------------------------------------------------------- Revisions

    /// Create a revision for an item (`number = 0` auto-increments).
    pub async fn create_revision(
        &self,
        item_kref: &Kref,
        metadata: Option<HashMap<String, String>>,
        number: i32,
        embedding_text: &str,
    ) -> Result<Revision> {
        let req = pb::CreateRevisionRequest {
            item_kref: Some(item_kref.to_pb()),
            metadata: metadata.unwrap_or_default(),
            number,
            exists_error: false,
            embedding_text: embedding_text.to_string(),
        };
        let resp = unary!(self, create_revision, req)?;
        Ok(Revision::from_pb(resp, self.clone()))
    }

    /// Get a revision by kref URI. Supports `?t=tag` / `?time=YYYYMMDDHHMM`.
    pub async fn get_revision(&self, kref_uri: &str) -> Result<Revision> {
        let (base, tag, time) = parse_tag_time(kref_uri)?;
        if tag.is_some() || time.is_some() {
            let req = pb::ResolveKrefRequest {
                kref: base,
                tag,
                time,
            };
            let resp = unary!(self, resolve_kref, req)?;
            return Ok(Revision::from_pb(resp, self.clone()));
        }
        let req = pb::KrefRequest {
            kref: Some(pb::Kref {
                uri: kref_uri.to_string(),
            }),
        };
        let resp = unary!(self, get_revision, req)?;
        Ok(Revision::from_pb(resp, self.clone()))
    }

    /// Get the item that owns the given revision kref.
    pub async fn get_item_from_revision(&self, revision_kref: &str) -> Result<Item> {
        let rev = self.get_revision(revision_kref).await?;
        self.get_item_by_kref(rev.item_kref.uri()).await
    }

    /// List all revisions of an item.
    pub async fn get_revisions(&self, item_kref: &Kref) -> Result<Vec<Revision>> {
        let req = pb::GetRevisionsRequest {
            item_kref: Some(item_kref.to_pb()),
            pagination: None,
        };
        let resp = unary!(self, get_revisions, req)?;
        Ok(resp
            .revisions
            .into_iter()
            .map(|r| Revision::from_pb(r, self.clone()))
            .collect())
    }

    /// Resolve the latest revision of an item, or `None` if it has none.
    pub async fn get_latest_revision(&self, item_kref: &Kref) -> Result<Option<Revision>> {
        let req = pb::ResolveKrefRequest {
            kref: item_kref.uri().to_string(),
            tag: None,
            time: None,
        };
        match unary!(self, resolve_kref, req) {
            Ok(resp) => Ok(Some(Revision::from_pb(resp, self.clone()))),
            Err(Error::Rpc(s)) if s.code() == tonic::Code::NotFound => Ok(None),
            Err(e) => Err(e),
        }
    }

    /// Batch-fetch revisions by revision krefs and/or item krefs + tag.
    pub async fn batch_get_revisions(
        &self,
        revision_krefs: &[String],
        item_krefs: &[String],
        tag: &str,
        allow_partial: bool,
    ) -> Result<(Vec<Revision>, Vec<String>)> {
        let req = pb::BatchGetRevisionsRequest {
            revision_krefs: revision_krefs
                .iter()
                .map(|k| pb::Kref { uri: k.clone() })
                .collect(),
            item_krefs: item_krefs
                .iter()
                .map(|k| pb::Kref { uri: k.clone() })
                .collect(),
            tag: tag.to_string(),
            allow_partial,
        };
        let resp = unary!(self, batch_get_revisions, req)?;
        let revisions = resp
            .revisions
            .into_iter()
            .map(|r| Revision::from_pb(r, self.clone()))
            .collect();
        Ok((revisions, resp.not_found))
    }

    /// Delete a revision.
    pub async fn delete_revision(&self, kref: &Kref, force: bool) -> Result<()> {
        let req = pb::DeleteRevisionRequest {
            kref: Some(kref.to_pb()),
            force,
        };
        unary!(self, delete_revision, req)?;
        Ok(())
    }

    /// Delete a space by path (force=true to delete a non-empty space).
    pub async fn delete_space(&self, path: &str, force: bool) -> Result<()> {
        let req = pb::DeleteSpaceRequest {
            path: path.to_string(),
            force,
        };
        unary!(self, delete_space, req)?;
        Ok(())
    }

    /// Delete an item (force=true to delete with revisions).
    pub async fn delete_item(&self, kref: &Kref, force: bool) -> Result<()> {
        let req = pb::DeleteItemRequest {
            kref: Some(kref.to_pb()),
            force,
        };
        unary!(self, delete_item, req)?;
        Ok(())
    }

    /// Resolve an item kref to a revision by tag and/or time (low-level).
    pub async fn resolve_kref(
        &self,
        kref: &str,
        tag: Option<String>,
        time: Option<String>,
    ) -> Result<Revision> {
        let req = pb::ResolveKrefRequest {
            kref: kref.to_string(),
            tag,
            time,
        };
        let resp = unary!(self, resolve_kref, req)?;
        Ok(Revision::from_pb(resp, self.clone()))
    }

    /// Merge metadata into a revision.
    pub async fn update_revision_metadata(
        &self,
        kref: &Kref,
        metadata: HashMap<String, String>,
    ) -> Result<Revision> {
        let req = pb::UpdateMetadataRequest {
            kref: Some(kref.to_pb()),
            metadata,
        };
        let resp = unary!(self, update_revision_metadata, req)?;
        Ok(Revision::from_pb(resp, self.clone()))
    }

    /// Peek the next revision number for an item.
    pub async fn peek_next_revision(&self, item_kref: &Kref) -> Result<i32> {
        let req = pb::PeekNextRevisionRequest {
            item_kref: Some(item_kref.to_pb()),
        };
        Ok(unary!(self, peek_next_revision, req)?.number)
    }

    /// Apply a tag to a revision.
    pub async fn tag_revision(&self, kref: &Kref, tag: &str) -> Result<()> {
        let req = pb::TagRevisionRequest {
            kref: Some(kref.to_pb()),
            tag: tag.to_string(),
        };
        unary!(self, tag_revision, req)?;
        Ok(())
    }

    /// Remove a tag from a revision.
    pub async fn untag_revision(&self, kref: &Kref, tag: &str) -> Result<()> {
        let req = pb::UnTagRevisionRequest {
            kref: Some(kref.to_pb()),
            tag: tag.to_string(),
        };
        unary!(self, un_tag_revision, req)?;
        Ok(())
    }

    /// Whether a revision currently has a tag.
    pub async fn has_tag(&self, kref: &Kref, tag: &str) -> Result<bool> {
        let req = pb::HasTagRequest {
            kref: Some(kref.to_pb()),
            tag: tag.to_string(),
        };
        Ok(unary!(self, has_tag, req)?.has_tag)
    }

    /// Whether a revision was ever tagged with a tag.
    pub async fn was_tagged(&self, kref: &Kref, tag: &str) -> Result<bool> {
        let req = pb::WasTaggedRequest {
            kref: Some(kref.to_pb()),
            tag: tag.to_string(),
        };
        Ok(unary!(self, was_tagged, req)?.was_tagged)
    }

    /// Set the default artifact for a revision.
    pub async fn set_default_artifact(
        &self,
        revision_kref: &Kref,
        artifact_name: &str,
    ) -> Result<()> {
        let req = pb::SetDefaultArtifactRequest {
            revision_kref: Some(revision_kref.to_pb()),
            artifact_name: artifact_name.to_string(),
        };
        unary!(self, set_default_artifact, req)?;
        Ok(())
    }

    // ---------------------------------------------------------------- Artifacts

    /// Create an artifact (file reference) on a revision.
    pub async fn create_artifact(
        &self,
        revision_kref: &Kref,
        name: &str,
        location: &str,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Artifact> {
        let req = pb::CreateArtifactRequest {
            revision_kref: Some(revision_kref.to_pb()),
            name: name.to_string(),
            location: location.to_string(),
            exists_error: false,
            metadata: metadata.unwrap_or_default(),
        };
        let resp = unary!(self, create_artifact, req)?;
        Ok(Artifact::from_pb(resp, self.clone()))
    }

    /// Get an artifact by revision kref + name.
    pub async fn get_artifact(&self, revision_kref: &Kref, name: &str) -> Result<Artifact> {
        let req = pb::GetArtifactRequest {
            revision_kref: Some(revision_kref.to_pb()),
            name: name.to_string(),
        };
        let resp = unary!(self, get_artifact, req)?;
        Ok(Artifact::from_pb(resp, self.clone()))
    }

    /// Get an artifact by kref URI; falls back to the revision's default artifact.
    pub async fn get_artifact_by_kref(&self, kref_uri: &str) -> Result<Artifact> {
        let kref = Kref::new(kref_uri).map_err(|e| Error::KrefValidation(e.0))?;
        if let Some(name) = kref.artifact_name() {
            let revision_uri = kref_uri.split("&a=").next().unwrap_or(kref_uri);
            let revision_kref = Kref::new(revision_uri).map_err(|e| Error::KrefValidation(e.0))?;
            return self.get_artifact(&revision_kref, &name).await;
        }
        let revision = self.get_revision(kref_uri).await?;
        match &revision.default_artifact {
            Some(default_name) => self.get_artifact(&revision.kref, default_name).await,
            None => Err(Error::InvalidArgument(format!(
                "artifact kref '{kref_uri}' missing &a= and no default_artifact set"
            ))),
        }
    }

    /// Get all artifacts on a revision.
    pub async fn get_artifacts(&self, revision_kref: &Kref) -> Result<Vec<Artifact>> {
        let req = pb::GetArtifactsRequest {
            revision_kref: Some(revision_kref.to_pb()),
        };
        let resp = unary!(self, get_artifacts, req)?;
        Ok(resp
            .artifacts
            .into_iter()
            .map(|a| Artifact::from_pb(a, self.clone()))
            .collect())
    }

    /// Reverse-lookup: all artifacts referencing a file location.
    pub async fn get_artifacts_by_location(&self, location: &str) -> Result<Vec<Artifact>> {
        let req = pb::GetArtifactsByLocationRequest {
            location: location.to_string(),
        };
        let resp = unary!(self, get_artifacts_by_location, req)?;
        Ok(resp
            .artifacts
            .into_iter()
            .map(|a| Artifact::from_pb(a, self.clone()))
            .collect())
    }

    /// Delete an artifact.
    pub async fn delete_artifact(&self, kref: &Kref, force: bool) -> Result<()> {
        let req = pb::DeleteArtifactRequest {
            kref: Some(kref.to_pb()),
            force,
        };
        unary!(self, delete_artifact, req)?;
        Ok(())
    }

    /// Merge metadata into an artifact.
    pub async fn update_artifact_metadata(
        &self,
        kref: &Kref,
        metadata: HashMap<String, String>,
    ) -> Result<Artifact> {
        let req = pb::UpdateMetadataRequest {
            kref: Some(kref.to_pb()),
            metadata,
        };
        let resp = unary!(self, update_artifact_metadata, req)?;
        Ok(Artifact::from_pb(resp, self.clone()))
    }

    /// Deprecate/restore any node (item, revision, artifact).
    pub async fn set_deprecated(&self, kref: &Kref, deprecated: bool) -> Result<()> {
        let req = pb::SetDeprecatedRequest {
            kref: Some(kref.to_pb()),
            deprecated,
        };
        unary!(self, set_deprecated, req)?;
        Ok(())
    }

    /// Resolve a kref to a file location, or `None` on failure.
    pub async fn resolve(&self, kref: &str) -> Result<Option<String>> {
        let (_, tag, time) = parse_tag_time(kref)?;
        let req = pb::ResolveLocationRequest {
            kref: kref.to_string(),
            tag,
            time,
        };
        match unary!(self, resolve_location, req) {
            Ok(resp) => Ok(Some(resp.location)),
            Err(Error::Rpc(_)) => Ok(None),
            Err(e) => Err(e),
        }
    }

    // --------------------------------------------------------------- Attributes

    /// Set a single metadata attribute on any entity.
    pub async fn set_attribute(&self, kref: &Kref, key: &str, value: &str) -> Result<bool> {
        let req = pb::SetAttributeRequest {
            kref: Some(kref.to_pb()),
            key: key.to_string(),
            value: value.to_string(),
        };
        Ok(unary!(self, set_attribute, req)?.success)
    }

    /// Get a single metadata attribute, or `None` if unset.
    pub async fn get_attribute(&self, kref: &Kref, key: &str) -> Result<Option<String>> {
        let req = pb::GetAttributeRequest {
            kref: Some(kref.to_pb()),
            key: key.to_string(),
        };
        let resp = unary!(self, get_attribute, req)?;
        Ok(resp.exists.then_some(resp.value))
    }

    /// Delete a single metadata attribute.
    pub async fn delete_attribute(&self, kref: &Kref, key: &str) -> Result<bool> {
        let req = pb::DeleteAttributeRequest {
            kref: Some(kref.to_pb()),
            key: key.to_string(),
        };
        Ok(unary!(self, delete_attribute, req)?.success)
    }

    // -------------------------------------------------------------------- Edges

    /// Create a typed edge between two revisions.
    pub async fn create_edge(
        &self,
        source: &Revision,
        target: &Revision,
        edge_type: &str,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Edge> {
        crate::edge::validate_edge_type(edge_type)?;
        let md = metadata.unwrap_or_default();
        let req = pb::CreateEdgeRequest {
            source_revision_kref: Some(source.kref.to_pb()),
            target_revision_kref: Some(target.kref.to_pb()),
            edge_type: edge_type.to_string(),
            metadata: md.clone(),
            exists_error: false,
        };
        unary!(self, create_edge, req)?;
        // Server returns only status; synthesize the Edge client-side.
        let pb_edge = pb::Edge {
            source_kref: Some(source.kref.to_pb()),
            target_kref: Some(target.kref.to_pb()),
            edge_type: edge_type.to_string(),
            metadata: md,
            created_at: String::new(),
            author: String::new(),
            username: String::new(),
        };
        Ok(Edge::from_pb(pb_edge, self.clone()))
    }

    /// Get edges for a revision, filtered by type and direction.
    pub async fn get_edges(
        &self,
        kref: &Kref,
        edge_type_filter: &str,
        direction: EdgeDirection,
    ) -> Result<Vec<Edge>> {
        let req = pb::GetEdgesRequest {
            kref: Some(kref.to_pb()),
            edge_type_filter: edge_type_filter.to_string(),
            direction: direction.as_pb(),
            pagination: None,
        };
        let resp = unary!(self, get_edges, req)?;
        Ok(resp
            .edges
            .into_iter()
            .map(|e| Edge::from_pb(e, self.clone()))
            .collect())
    }

    /// Delete an edge.
    pub async fn delete_edge(
        &self,
        source_kref: &Kref,
        target_kref: &Kref,
        edge_type: &str,
    ) -> Result<()> {
        crate::edge::validate_edge_type(edge_type)?;
        let req = pb::DeleteEdgeRequest {
            source_kref: Some(source_kref.to_pb()),
            target_kref: Some(target_kref.to_pb()),
            edge_type: edge_type.to_string(),
        };
        unary!(self, delete_edge, req)?;
        Ok(())
    }

    // ------------------------------------------------------------ Graph traversal

    /// Transitively traverse edges from an origin revision.
    pub async fn traverse_edges(
        &self,
        origin_kref: &Kref,
        direction: EdgeDirection,
        edge_type_filter: Option<Vec<String>>,
        max_depth: i32,
        limit: i32,
        include_path: bool,
    ) -> Result<TraversalResult> {
        let req = pb::TraverseEdgesRequest {
            origin_kref: Some(origin_kref.to_pb()),
            direction: direction.as_pb(),
            edge_type_filter: edge_type_filter.unwrap_or_default(),
            max_depth,
            limit,
            include_path,
        };
        let resp = unary!(self, traverse_edges, req)?;
        let revision_krefs = resp
            .revision_krefs
            .into_iter()
            .map(|k| Kref::unchecked(k.uri))
            .collect();
        let paths = resp.paths.into_iter().map(map_path).collect();
        let edges = resp
            .edges
            .into_iter()
            .map(|e| Edge::from_pb(e, self.clone()))
            .collect();
        Ok(TraversalResult::new(
            revision_krefs,
            paths,
            edges,
            resp.total_count,
            resp.truncated,
            self.clone(),
        ))
    }

    /// Find the shortest path between two revisions.
    pub async fn find_shortest_path(
        &self,
        source_kref: &Kref,
        target_kref: &Kref,
        edge_type_filter: Option<Vec<String>>,
        max_depth: i32,
        all_shortest: bool,
    ) -> Result<ShortestPathResult> {
        let req = pb::ShortestPathRequest {
            source_kref: Some(source_kref.to_pb()),
            target_kref: Some(target_kref.to_pb()),
            edge_type_filter: edge_type_filter.unwrap_or_default(),
            max_depth,
            all_shortest,
        };
        let resp = unary!(self, find_shortest_path, req)?;
        Ok(ShortestPathResult {
            paths: resp.paths.into_iter().map(map_path).collect(),
            path_exists: resp.path_exists,
            path_length: resp.path_length,
        })
    }

    /// Analyze which revisions are impacted by changes to a revision.
    pub async fn analyze_impact(
        &self,
        revision_kref: &Kref,
        edge_type_filter: Option<Vec<String>>,
        max_depth: i32,
        limit: i32,
    ) -> Result<Vec<ImpactedRevision>> {
        let req = pb::ImpactAnalysisRequest {
            revision_kref: Some(revision_kref.to_pb()),
            edge_type_filter: edge_type_filter.unwrap_or_default(),
            max_depth,
            limit,
        };
        let resp = unary!(self, analyze_impact, req)?;
        Ok(resp
            .impacted_revisions
            .into_iter()
            .map(|iv| ImpactedRevision {
                revision_kref: Kref::unchecked(iv.revision_kref.map(|k| k.uri).unwrap_or_default()),
                item_kref: iv
                    .item_kref
                    .and_then(|k| (!k.uri.is_empty()).then(|| Kref::unchecked(k.uri))),
                impact_depth: iv.impact_depth,
                impact_path_types: iv.impact_path_types,
            })
            .collect())
    }

    // ------------------------------------------------------------------ Bundles

    /// Create a bundle (the reserved `bundle` kind).
    pub async fn create_bundle(
        &self,
        parent_path: &str,
        bundle_name: &str,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Bundle> {
        let req = pb::CreateBundleRequest {
            parent_path: parent_path.to_string(),
            bundle_name: bundle_name.to_string(),
            metadata: metadata.unwrap_or_default(),
        };
        let resp = unary!(self, create_bundle, req)?;
        Bundle::from_pb(resp, self.clone())
    }

    /// Add an item to a bundle. Returns `(success, message, new_revision)`.
    pub async fn add_bundle_member(
        &self,
        bundle_kref: &Kref,
        member_item_kref: &Kref,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<(bool, String, Option<Revision>)> {
        let req = pb::AddBundleMemberRequest {
            bundle_kref: Some(bundle_kref.to_pb()),
            member_item_kref: Some(member_item_kref.to_pb()),
            metadata: metadata.unwrap_or_default(),
        };
        let resp = unary!(self, add_bundle_member, req)?;
        let rev = resp
            .new_revision
            .map(|r| Revision::from_pb(r, self.clone()));
        Ok((resp.success, resp.message, rev))
    }

    /// Remove an item from a bundle. Returns `(success, message, new_revision)`.
    pub async fn remove_bundle_member(
        &self,
        bundle_kref: &Kref,
        member_item_kref: &Kref,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<(bool, String, Option<Revision>)> {
        let req = pb::RemoveBundleMemberRequest {
            bundle_kref: Some(bundle_kref.to_pb()),
            member_item_kref: Some(member_item_kref.to_pb()),
            metadata: metadata.unwrap_or_default(),
        };
        let resp = unary!(self, remove_bundle_member, req)?;
        let rev = resp
            .new_revision
            .map(|r| Revision::from_pb(r, self.clone()));
        Ok((resp.success, resp.message, rev))
    }

    /// Get a bundle's members (optionally at a specific revision).
    pub async fn get_bundle_members(
        &self,
        bundle_kref: &Kref,
        revision_number: Option<i32>,
    ) -> Result<(Vec<BundleMember>, i32, i32)> {
        let req = pb::GetBundleMembersRequest {
            bundle_kref: Some(bundle_kref.to_pb()),
            revision_number,
        };
        let resp = unary!(self, get_bundle_members, req)?;
        let members = resp
            .members
            .into_iter()
            .map(|m| BundleMember {
                item_kref: Kref::unchecked(m.item_kref.map(|k| k.uri).unwrap_or_default()),
                added_at: m.added_at,
                added_by: m.added_by,
                added_by_username: m.added_by_username,
                added_in_revision: m.added_in_revision,
            })
            .collect();
        Ok((members, resp.revision_number, resp.total_count))
    }

    /// Get a bundle's immutable membership-change history.
    pub async fn get_bundle_history(
        &self,
        bundle_kref: &Kref,
    ) -> Result<Vec<BundleRevisionHistory>> {
        let req = pb::GetBundleHistoryRequest {
            bundle_kref: Some(bundle_kref.to_pb()),
        };
        let resp = unary!(self, get_bundle_history, req)?;
        Ok(resp
            .history
            .into_iter()
            .map(|h| BundleRevisionHistory {
                revision_number: h.revision_number,
                action: h.action,
                member_item_kref: h
                    .member_item_kref
                    .and_then(|k| (!k.uri.is_empty()).then(|| Kref::unchecked(k.uri))),
                author: h.author,
                username: h.username,
                created_at: h.created_at,
                metadata: h.metadata,
            })
            .collect())
    }

    // ------------------------------------------------------------------- Tenant

    /// Get the current tenant's node usage and limit.
    pub async fn get_tenant_usage(&self) -> Result<TenantUsage> {
        let resp = unary!(self, get_tenant_usage, pb::GetTenantUsageRequest {})?;
        Ok(TenantUsage {
            node_count: resp.node_count,
            node_limit: resp.node_limit,
            tenant_id: resp.tenant_id,
        })
    }

    // -------------------------------------------------------------------- Events

    /// Subscribe to the server event stream.
    ///
    /// Returns an async [`Stream`] of [`Event`]s. The stream ends (or errors)
    /// when the server closes the channel.
    pub async fn event_stream(
        &self,
        routing_key_filter: &str,
        kref_filter: &str,
        cursor: Option<String>,
        consumer_group: Option<String>,
        from_beginning: bool,
    ) -> Result<impl Stream<Item = Result<Event>>> {
        let mut req = pb::EventStreamRequest {
            routing_key_filter: routing_key_filter.to_string(),
            kref_filter: kref_filter.to_string(),
            cursor,
            consumer_group,
            start_position: None,
        };
        if from_beginning {
            req.start_position = Some(pb::event_stream_request::StartPosition::FromBeginning(true));
        }
        let mut grpc = self.grpc.clone();
        let stream = grpc.event_stream(req).await?.into_inner();
        Ok(stream.map(|item| item.map(Event::from_pb).map_err(Error::Rpc)))
    }

    /// Get this tenant tier's event-streaming capabilities.
    pub async fn get_event_capabilities(&self) -> Result<EventCapabilities> {
        let resp = unary!(
            self,
            get_event_capabilities,
            pb::GetEventCapabilitiesRequest {}
        )?;
        Ok(EventCapabilities {
            supports_replay: resp.supports_replay,
            supports_cursor: resp.supports_cursor,
            supports_consumer_groups: resp.supports_consumer_groups,
            max_retention_hours: resp.max_retention_hours,
            max_buffer_size: resp.max_buffer_size,
            tier: resp.tier,
        })
    }
}

// ------------------------------------------------------------------- free helpers

fn make_pagination(
    page_size: Option<i32>,
    cursor: Option<String>,
) -> Option<pb::PaginationRequest> {
    if page_size.is_none() && cursor.is_none() {
        return None;
    }
    Some(pb::PaginationRequest {
        page_size: page_size.unwrap_or(100),
        cursor: cursor.unwrap_or_default(),
    })
}

fn map_path(p: pb::RevisionPath) -> RevisionPath {
    RevisionPath {
        steps: p
            .steps
            .into_iter()
            .map(|s| PathStep {
                revision_kref: Kref::unchecked(s.revision_kref.map(|k| k.uri).unwrap_or_default()),
                edge_type: s.edge_type,
                depth: s.depth,
            })
            .collect(),
        total_depth: p.total_depth,
    }
}

/// Split an item kref URI into `(parent_path_with_leading_slash, name, kind)`.
fn split_item_kref(kref_uri: &str) -> Result<(String, String, String)> {
    let kref = Kref::new(kref_uri).map_err(|e| Error::KrefValidation(e.0))?;
    let path = kref.path();
    let (space_path, item_name_kind) = path
        .split_once('/')
        .ok_or_else(|| Error::InvalidArgument(format!("invalid item kref: {kref_uri}")))?;
    let (name, kind) = item_name_kind.split_once('.').ok_or_else(|| {
        Error::InvalidArgument(format!("invalid item name.kind: {item_name_kind}"))
    })?;
    Ok((format!("/{space_path}"), name.to_string(), kind.to_string()))
}

/// Parse `?t=`/`?tag=`/`?time=` query params from a kref; returns `(base, tag, time)`.
fn parse_tag_time(kref_uri: &str) -> Result<(String, Option<String>, Option<String>)> {
    let Some((base, params)) = kref_uri.split_once('?') else {
        return Ok((kref_uri.to_string(), None, None));
    };
    let mut tag = None;
    let mut time = None;
    for param in params.split('&') {
        if let Some(v) = param
            .strip_prefix("t=")
            .or_else(|| param.strip_prefix("tag="))
        {
            tag = Some(v.to_string());
        } else if let Some(v) = param.strip_prefix("time=") {
            if v.len() != 12 || !v.chars().all(|c| c.is_ascii_digit()) {
                return Err(Error::InvalidArgument(
                    "time must be in YYYYMMDDHHMM format".into(),
                ));
            }
            time = Some(v.to_string());
        }
    }
    Ok((base.to_string(), tag, time))
}
