//! Locating bearer tokens for gRPC auth (mirrors Python `_token_loader.py`).
//!
//! Resolution order:
//! 1. `KUMIHO_AUTH_TOKEN` env var.
//! 2. `~/.kumiho/kumiho_authentication.json` — preferring the firebase
//!    `id_token` unless `KUMIHO_USE_CONTROL_PLANE_TOKEN` is set.

use std::path::PathBuf;

const TOKEN_ENV: &str = "KUMIHO_AUTH_TOKEN";
#[allow(dead_code)]
const FIREBASE_TOKEN_ENV: &str = "KUMIHO_FIREBASE_ID_TOKEN";
const USE_CP_TOKEN_ENV: &str = "KUMIHO_USE_CONTROL_PLANE_TOKEN";
const CREDENTIALS_FILENAME: &str = "kumiho_authentication.json";

fn normalize(value: Option<String>) -> Option<String> {
    value
        .map(|v| v.trim().to_string())
        .filter(|v| !v.is_empty())
}

fn env_flag(name: &str) -> bool {
    std::env::var(name)
        .map(|v| matches!(v.trim().to_ascii_lowercase().as_str(), "1" | "true" | "yes"))
        .unwrap_or(false)
}

/// The Kumiho config directory (`$KUMIHO_CONFIG_DIR` or `~/.kumiho`).
pub fn config_dir() -> PathBuf {
    if let Ok(dir) = std::env::var("KUMIHO_CONFIG_DIR") {
        if !dir.is_empty() {
            return PathBuf::from(shellexpand_tilde(&dir));
        }
    }
    let home = dirs::home_dir().unwrap_or_else(|| PathBuf::from("."));
    home.join(".kumiho")
}

fn shellexpand_tilde(p: &str) -> String {
    if let Some(rest) = p.strip_prefix("~") {
        if let Some(home) = dirs::home_dir() {
            return format!("{}{}", home.display(), rest);
        }
    }
    p.to_string()
}

fn credentials_path() -> PathBuf {
    config_dir().join(CREDENTIALS_FILENAME)
}

fn read_credentials() -> Option<serde_json::Value> {
    let path = credentials_path();
    let text = std::fs::read_to_string(path).ok()?;
    serde_json::from_str(&text).ok()
}

fn credentials_tokens() -> (Option<String>, Option<String>) {
    match read_credentials() {
        Some(data) => {
            let cp = normalize(
                data.get("control_plane_token")
                    .and_then(|v| v.as_str())
                    .map(String::from),
            );
            let id = normalize(
                data.get("id_token")
                    .and_then(|v| v.as_str())
                    .map(String::from),
            );
            (cp, id)
        }
        None => (None, None),
    }
}

/// Validate a token has JWT shape (`header.payload.signature`).
pub fn validate_token_format(
    token: Option<String>,
    source: &str,
) -> Result<Option<String>, String> {
    let token = match normalize(token) {
        Some(t) => t,
        None => return Ok(None),
    };
    let parts: Vec<&str> = token.split('.').collect();
    if parts.len() != 3 {
        return Err(format!(
            "Invalid {source} format: expected JWT with 3 parts, got {}. Run `kumiho-cli login`.",
            parts.len()
        ));
    }
    if parts.iter().any(|p| p.is_empty()) {
        return Err(format!(
            "Invalid {source} format: a JWT part is empty (token corrupted/incomplete)."
        ));
    }
    Ok(Some(token))
}

/// The preferred bearer token for gRPC calls, if any can be found.
pub fn load_bearer_token() -> Result<Option<String>, String> {
    if let Some(env_token) = normalize(std::env::var(TOKEN_ENV).ok()) {
        return validate_token_format(Some(env_token), "KUMIHO_AUTH_TOKEN");
    }
    let prefer_cp = env_flag(USE_CP_TOKEN_ENV);
    let (cp, firebase) = credentials_tokens();
    if prefer_cp {
        if let Some(cp) = cp.clone() {
            return validate_token_format(Some(cp), "control_plane_token");
        }
    }
    if let Some(fb) = firebase {
        return validate_token_format(Some(fb), "id_token");
    }
    if let Some(cp) = cp {
        return validate_token_format(Some(cp), "control_plane_token");
    }
    Ok(None)
}

/// A Firebase ID token for control-plane interactions, if available.
#[allow(dead_code)]
pub fn load_firebase_token() -> Option<String> {
    if let Some(env_token) = normalize(std::env::var(FIREBASE_TOKEN_ENV).ok()) {
        return Some(env_token);
    }
    credentials_tokens().1
}
