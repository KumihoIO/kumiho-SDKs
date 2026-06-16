package kumiho

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
)

// Kref is a Kumiho Reference: a URI uniquely identifying any object,
// kref://project/space/item.kind?r=REVISION&a=ARTIFACT.
//
// It is a string type, so it can be used anywhere a string is expected.
type Kref string

// krefPattern mirrors the Python gold standard. Go's RE2 \w is ASCII-only, so
// Unicode letter/number classes are used explicitly to keep Unicode path
// segments (e.g. Hangul) valid. Path traversal and control characters are
// rejected by ValidateKref's explicit checks, not this pattern.
var krefPattern = regexp.MustCompile(
	`^kref://((/[\p{L}\p{N}_][\p{L}\p{N}_.\-]*)+|[\p{L}\p{N}_][\p{L}\p{N}_.\-]*(/[\p{L}\p{N}_][\p{L}\p{N}_.\-]*)*)(\?r=\d+(&a=[a-zA-Z0-9._\-]+)?)?$`,
)

// ValidateKref checks a kref URI for security and correctness. It rejects path
// traversal (".."), control characters, and anything not matching the grammar.
func ValidateKref(uri string) error {
	if strings.Contains(uri, "..") {
		return &KrefValidationError{Msg: fmt.Sprintf("invalid kref URI %q: path traversal (..) not allowed", uri)}
	}
	for _, r := range uri {
		if r < 32 || r == 0x7f {
			return &KrefValidationError{Msg: fmt.Sprintf("invalid kref URI %q: control characters not allowed", uri)}
		}
	}
	if !krefPattern.MatchString(uri) {
		return &KrefValidationError{Msg: fmt.Sprintf("invalid kref URI %q: must be format kref://project/space/item.kind", uri)}
	}
	return nil
}

// IsValidKref reports whether uri is a valid kref.
func IsValidKref(uri string) bool { return ValidateKref(uri) == nil }

// NewKref parses and validates a kref URI.
func NewKref(uri string) (Kref, error) {
	if err := ValidateKref(uri); err != nil {
		return "", err
	}
	return Kref(uri), nil
}

// krefFromPB wraps a trusted, server-returned protobuf Kref without validation.
func krefFromPB(k *pb.Kref) Kref {
	if k == nil {
		return ""
	}
	return Kref(k.GetUri())
}

func (k Kref) pb() *pb.Kref { return &pb.Kref{Uri: string(k)} }

// URI returns the underlying URI string.
func (k Kref) URI() string { return string(k) }

// String implements fmt.Stringer.
func (k Kref) String() string { return string(k) }

// Path returns the path component (after "kref://", before any "?").
func (k Kref) Path() string {
	s := string(k)
	if i := strings.Index(s, "://"); i >= 0 {
		s = s[i+3:]
	}
	if i := strings.IndexByte(s, '?'); i >= 0 {
		s = s[:i]
	}
	return s
}

// Project returns the first path segment.
func (k Kref) Project() string {
	p := k.Path()
	if i := strings.IndexByte(p, '/'); i >= 0 {
		return p[:i]
	}
	return p
}

// Space returns the segments between project and item, or "" if none.
func (k Kref) Space() string {
	parts := strings.Split(k.Path(), "/")
	if len(parts) <= 2 {
		return ""
	}
	return strings.Join(parts[1:len(parts)-1], "/")
}

// ItemName returns the last path segment (e.g. "hero.model"), or "".
func (k Kref) ItemName() string {
	p := k.Path()
	if i := strings.LastIndexByte(p, '/'); i >= 0 {
		return p[i+1:]
	}
	return ""
}

// Kind returns the item kind (after the first "." in the item name), or "".
func (k Kref) Kind() string {
	name := k.ItemName()
	if i := strings.IndexByte(name, '.'); i >= 0 {
		return name[i+1:]
	}
	return ""
}

// Revision returns the revision number from "?r=", defaulting to 1.
func (k Kref) Revision() int {
	s := string(k)
	i := strings.Index(s, "?r=")
	if i < 0 {
		return 1
	}
	rest := s[i+3:]
	end := 0
	for end < len(rest) && rest[end] >= '0' && rest[end] <= '9' {
		end++
	}
	if n, err := strconv.Atoi(rest[:end]); err == nil {
		return n
	}
	return 1
}

// ArtifactName returns the artifact name from "&a=", or "" if absent.
func (k Kref) ArtifactName() string {
	s := string(k)
	i := strings.Index(s, "&a=")
	if i < 0 {
		return ""
	}
	rest := s[i+3:]
	if j := strings.IndexByte(rest, '&'); j >= 0 {
		return rest[:j]
	}
	return rest
}
