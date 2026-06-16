package kumiho

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

const (
	tokenEnv         = "KUMIHO_AUTH_TOKEN"
	firebaseTokenEnv = "KUMIHO_FIREBASE_ID_TOKEN"
	useCPTokenEnv    = "KUMIHO_USE_CONTROL_PLANE_TOKEN"
	credentialsFile  = "kumiho_authentication.json"
	configDirEnv     = "KUMIHO_CONFIG_DIR"
)

func normalizeToken(v string) string { return strings.TrimSpace(v) }

func envFlag(name string) bool {
	switch strings.ToLower(strings.TrimSpace(os.Getenv(name))) {
	case "1", "true", "yes":
		return true
	default:
		return false
	}
}

// configDir returns $KUMIHO_CONFIG_DIR or ~/.kumiho.
func configDir() string {
	if d := os.Getenv(configDirEnv); d != "" {
		return expandHome(d)
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return ".kumiho"
	}
	return filepath.Join(home, ".kumiho")
}

func expandHome(p string) string {
	if strings.HasPrefix(p, "~") {
		if home, err := os.UserHomeDir(); err == nil {
			return home + p[1:]
		}
	}
	return p
}

func credentialsTokens() (controlPlane, firebase string) {
	data, err := os.ReadFile(filepath.Join(configDir(), credentialsFile))
	if err != nil {
		return "", ""
	}
	var m map[string]any
	if json.Unmarshal(data, &m) != nil {
		return "", ""
	}
	if v, ok := m["control_plane_token"].(string); ok {
		controlPlane = normalizeToken(v)
	}
	if v, ok := m["id_token"].(string); ok {
		firebase = normalizeToken(v)
	}
	return controlPlane, firebase
}

func validateTokenFormat(token, source string) (string, error) {
	token = normalizeToken(token)
	if token == "" {
		return "", nil
	}
	parts := strings.Split(token, ".")
	if len(parts) != 3 {
		return "", fmt.Errorf("invalid %s format: expected JWT with 3 parts, got %d (run `kumiho-cli login`)", source, len(parts))
	}
	for _, p := range parts {
		if p == "" {
			return "", fmt.Errorf("invalid %s format: a JWT part is empty", source)
		}
	}
	return token, nil
}

// loadBearerToken returns the preferred bearer token for gRPC calls, if any.
func loadBearerToken() (string, error) {
	if env := normalizeToken(os.Getenv(tokenEnv)); env != "" {
		return validateTokenFormat(env, "KUMIHO_AUTH_TOKEN")
	}
	cp, firebase := credentialsTokens()
	if envFlag(useCPTokenEnv) && cp != "" {
		return validateTokenFormat(cp, "control_plane_token")
	}
	if firebase != "" {
		return validateTokenFormat(firebase, "id_token")
	}
	if cp != "" {
		return validateTokenFormat(cp, "control_plane_token")
	}
	return "", nil
}
