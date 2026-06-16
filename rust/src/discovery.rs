//! Control-plane discovery, encrypted routing cache, and local-CE fallback.
//!
//! Mirrors the Python `discovery.py`: resolve the regional gRPC endpoint for a
//! tenant via `POST {control_plane}/api/discovery/tenant`, cache the routing
//! payload at rest (XOR + HMAC, machine-derived key), and honour the
//! cache-control refresh/expiry window. Also probes a loopback self-hosted CE
//! server so a local dev deployment "just works" without a token.

use base64::Engine;
use chrono::{DateTime, Utc};
use hmac::{Hmac, Mac};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::path::PathBuf;

type HmacSha256 = Hmac<Sha256>;

const DEFAULT_CONTROL_PLANE: &str = "https://control.kumiho.cloud";
const DEFAULT_CACHE_KEY: &str = "__default__";
const DEFAULT_LOCAL_CE_PORT: u16 = 9190;

/// Discovery / control-plane bootstrap failure.
#[derive(Debug, Clone, thiserror::Error)]
#[error("{0}")]
pub struct DiscoveryError(pub String);

impl From<DiscoveryError> for crate::Error {
    fn from(e: DiscoveryError) -> Self {
        crate::Error::Discovery(e.0)
    }
}

/// Regional gRPC routing returned by the control plane.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RegionRouting {
    pub region_code: String,
    pub server_url: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub grpc_authority: Option<String>,
}

/// Cache-control window emitted by the control plane.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheControl {
    pub issued_at: String,
    pub refresh_at: String,
    pub expires_at: String,
    #[serde(default)]
    pub expires_in_seconds: i64,
    #[serde(default)]
    pub refresh_after_seconds: i64,
}

impl CacheControl {
    fn ts(raw: &str) -> Option<DateTime<Utc>> {
        DateTime::parse_from_rfc3339(&raw.replace(' ', "T"))
            .ok()
            .map(|d| d.with_timezone(&Utc))
    }
    fn is_expired(&self) -> bool {
        match Self::ts(&self.expires_at) {
            Some(t) => Utc::now() >= t,
            None => true,
        }
    }
    fn should_refresh(&self) -> bool {
        match Self::ts(&self.refresh_at) {
            Some(t) => Utc::now() >= t,
            None => true,
        }
    }
}

/// A resolved discovery record (tenant + routing + cache window).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiscoveryRecord {
    pub tenant_id: String,
    #[serde(default)]
    pub tenant_name: Option<String>,
    #[serde(default)]
    pub roles: Vec<String>,
    #[serde(default)]
    pub guardrails: Option<serde_json::Value>,
    pub region: RegionRouting,
    pub cache_control: CacheControl,
}

impl DiscoveryRecord {
    /// The gRPC target to dial (authority preferred over server URL).
    pub fn target(&self) -> String {
        self.region
            .grpc_authority
            .clone()
            .unwrap_or_else(|| self.region.server_url.clone())
    }
}

// ---- at-rest cache encryption (defense-in-depth, machine-bound) ----

fn machine_id() -> String {
    #[cfg(target_os = "linux")]
    {
        for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"] {
            if let Ok(s) = std::fs::read_to_string(path) {
                let s = s.trim();
                if !s.is_empty() {
                    return s.to_string();
                }
            }
        }
    }
    #[cfg(target_os = "macos")]
    {
        if let Ok(out) = std::process::Command::new("ioreg")
            .args(["-rd1", "-c", "IOPlatformExpertDevice"])
            .output()
        {
            let text = String::from_utf8_lossy(&out.stdout);
            for line in text.lines() {
                if line.contains("IOPlatformUUID") {
                    if let Some(uuid) = line.split('"').nth_back(1) {
                        return uuid.to_string();
                    }
                }
            }
        }
    }
    // Fallback: a random id stored in the config dir.
    let id_file = crate::token_loader::config_dir().join(".machine_id");
    if let Ok(s) = std::fs::read_to_string(&id_file) {
        let s = s.trim();
        if !s.is_empty() {
            return s.to_string();
        }
    }
    let new_id = uuid::Uuid::new_v4().to_string();
    let _ = std::fs::create_dir_all(crate::token_loader::config_dir());
    let _ = std::fs::write(&id_file, &new_id);
    new_id
}

fn derive_key() -> [u8; 32] {
    let login = std::env::var("USER").or_else(|_| std::env::var("LOGNAME")).unwrap_or_default();
    let material = format!("kumiho-discovery-cache-v1:{}:{}", machine_id(), login);
    let mut hasher = Sha256::new();
    hasher.update(material.as_bytes());
    hasher.finalize().into()
}

fn keystream(key: &[u8], iv: &[u8], len: usize) -> Vec<u8> {
    let mut stream: Vec<u8> = {
        let mut h = Sha256::new();
        h.update(key);
        h.update(iv);
        h.finalize().to_vec()
    };
    while stream.len() < len {
        let tail = stream[stream.len() - 32..].to_vec();
        let mut h = Sha256::new();
        h.update(key);
        h.update(&tail);
        stream.extend_from_slice(&h.finalize());
    }
    stream
}

fn encrypt(plaintext: &str) -> String {
    let key = derive_key();
    let iv: [u8; 16] = rand::random();
    let pt = plaintext.as_bytes();
    let ks = keystream(&key, &iv, pt.len());
    let ct: Vec<u8> = pt.iter().zip(ks.iter()).map(|(p, k)| p ^ k).collect();
    let mut mac = HmacSha256::new_from_slice(&key).expect("hmac key");
    mac.update(&iv);
    mac.update(&ct);
    let tag = &mac.finalize().into_bytes()[..16];
    let mut blob = Vec::with_capacity(16 + ct.len() + 16);
    blob.extend_from_slice(&iv);
    blob.extend_from_slice(&ct);
    blob.extend_from_slice(tag);
    format!("enc:v1:{}", base64::engine::general_purpose::STANDARD.encode(blob))
}

fn decrypt(encrypted: &str) -> Option<String> {
    let Some(b64) = encrypted.strip_prefix("enc:v1:") else {
        return Some(encrypted.to_string()); // legacy plaintext
    };
    let key = derive_key();
    let raw = base64::engine::general_purpose::STANDARD.decode(b64).ok()?;
    if raw.len() < 32 {
        return None;
    }
    let iv = &raw[..16];
    let tag = &raw[raw.len() - 16..];
    let ct = &raw[16..raw.len() - 16];
    let mut mac = HmacSha256::new_from_slice(&key).ok()?;
    mac.update(iv);
    mac.update(ct);
    let expected = &mac.finalize().into_bytes()[..16];
    if expected != tag {
        return None;
    }
    let ks = keystream(&key, iv, ct.len());
    let pt: Vec<u8> = ct.iter().zip(ks.iter()).map(|(c, k)| c ^ k).collect();
    String::from_utf8(pt).ok()
}

fn cache_path() -> PathBuf {
    if let Ok(p) = std::env::var("KUMIHO_DISCOVERY_CACHE_FILE") {
        if !p.is_empty() {
            return PathBuf::from(p);
        }
    }
    // Own cache file (the Python SDK uses discovery-cache.json on the same key
    // derivation; we namespace ours to avoid cross-language key clashes).
    crate::token_loader::config_dir().join("discovery-cache.rust.json")
}

struct DiscoveryCache {
    path: PathBuf,
}

impl DiscoveryCache {
    fn read_all(&self) -> HashMap<String, DiscoveryRecord> {
        let Ok(content) = std::fs::read_to_string(&self.path) else {
            return HashMap::new();
        };
        let Some(plain) = decrypt(&content) else {
            return HashMap::new();
        };
        serde_json::from_str(&plain).unwrap_or_default()
    }

    fn load(&self, key: &str) -> Option<DiscoveryRecord> {
        self.read_all().remove(key)
    }

    fn store(&self, key: &str, record: &DiscoveryRecord) {
        let mut all = self.read_all();
        all.insert(key.to_string(), record.clone());
        let Ok(json) = serde_json::to_string_pretty(&all) else {
            return;
        };
        if let Some(parent) = self.path.parent() {
            let _ = std::fs::create_dir_all(parent);
        }
        let _ = std::fs::write(&self.path, encrypt(&json));
    }
}

fn build_discovery_url(base: &str) -> String {
    let base = base.trim_end_matches('/');
    if base.ends_with("/api/discovery/tenant") {
        base.to_string()
    } else if base.ends_with("/api/discovery") {
        format!("{base}/tenant")
    } else if base.ends_with("/api") {
        format!("{base}/discovery/tenant")
    } else {
        format!("{base}/api/discovery/tenant")
    }
}

async fn fetch_remote(
    base_url: &str,
    id_token: &str,
    tenant_hint: Option<&str>,
) -> Result<DiscoveryRecord, DiscoveryError> {
    let url = build_discovery_url(base_url);
    let mut body = serde_json::Map::new();
    if let Some(hint) = tenant_hint {
        body.insert("tenant_hint".into(), serde_json::Value::String(hint.to_string()));
    }
    let resp = reqwest::Client::new()
        .post(&url)
        .header("Authorization", format!("Bearer {id_token}"))
        .header("Content-Type", "application/json")
        .header("User-Agent", format!("kumiho-rust/{}", env!("CARGO_PKG_VERSION")))
        .json(&body)
        .send()
        .await
        .map_err(|e| DiscoveryError(format!("request failed: {e}")))?;
    let status = resp.status();
    if status.as_u16() >= 400 {
        let text = resp.text().await.unwrap_or_default();
        return Err(DiscoveryError(format!(
            "discovery endpoint returned {}: {}",
            status,
            &text.chars().take(200).collect::<String>()
        )));
    }
    resp.json::<DiscoveryRecord>()
        .await
        .map_err(|e| DiscoveryError(format!("invalid discovery payload: {e}")))
}

/// Resolve a [`DiscoveryRecord`], using the encrypted cache when fresh.
pub async fn resolve(
    id_token: &str,
    tenant_hint: Option<&str>,
    force_refresh: bool,
) -> Result<DiscoveryRecord, DiscoveryError> {
    let base_url =
        std::env::var("KUMIHO_CONTROL_PLANE_URL").unwrap_or_else(|_| DEFAULT_CONTROL_PLANE.to_string());
    let cache = DiscoveryCache { path: cache_path() };
    let cache_key = tenant_hint.unwrap_or(DEFAULT_CACHE_KEY);

    if !force_refresh {
        if let Some(cached) = cache.load(cache_key) {
            if !cached.cache_control.is_expired() {
                if cached.cache_control.should_refresh() {
                    match fetch_remote(&base_url, id_token, tenant_hint).await {
                        Ok(fresh) => {
                            cache.store(cache_key, &fresh);
                            return Ok(fresh);
                        }
                        Err(_) if !cached.cache_control.is_expired() => return Ok(cached),
                        Err(e) => return Err(e),
                    }
                }
                return Ok(cached);
            }
        }
    }

    let fresh = fetch_remote(&base_url, id_token, tenant_hint).await?;
    cache.store(cache_key, &fresh);
    Ok(fresh)
}

/// Probe loopback ports for a self-hosted CE server; return a gRPC target.
pub async fn resolve_local_ce_endpoint() -> Option<String> {
    let candidates: Vec<String> = if let Ok(ep) = std::env::var("KUMIHO_LOCAL_SERVER_ENDPOINT") {
        if ep.trim().is_empty() {
            vec![]
        } else {
            vec![normalize_local_target(ep.trim())]
        }
    } else if let Ok(port) = std::env::var("KUMIHO_LOCAL_SERVER_PORT") {
        match port.trim().parse::<u16>() {
            Ok(p) => vec![format!("127.0.0.1:{p}")],
            Err(_) => vec![],
        }
    } else {
        vec![format!("127.0.0.1:{DEFAULT_LOCAL_CE_PORT}")]
    };

    for target in candidates {
        if probe_ce(&target).await {
            return Some(target);
        }
    }
    None
}

fn normalize_local_target(raw: &str) -> String {
    let raw = raw.trim();
    let stripped = raw.split("://").last().unwrap_or(raw);
    if stripped.contains(':') {
        stripped.to_string()
    } else {
        format!("{stripped}:{DEFAULT_LOCAL_CE_PORT}")
    }
}

async fn probe_ce(target: &str) -> bool {
    let url = format!("http://{target}/api/_live");
    let client = match reqwest::Client::builder()
        .timeout(std::time::Duration::from_millis(500))
        .build()
    {
        Ok(c) => c,
        Err(_) => return false,
    };
    let Ok(resp) = client.get(&url).send().await else {
        return false;
    };
    if resp.status().as_u16() >= 400 {
        return false;
    }
    match resp.json::<serde_json::Value>().await {
        Ok(body) => body.get("deployment_mode").and_then(|v| v.as_str()) == Some("self_hosted_ce"),
        Err(_) => false,
    }
}
