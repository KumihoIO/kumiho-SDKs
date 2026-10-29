package kumiho

// The structured kref parser.
//
// ParseKref reads a kref once, with the grammar in spec/kref/README.md that
// kumiho-db and every Kumiho SDK share, and returns a KrefParts. It is the only
// place a kref string is cut into pieces for an item lookup: the GetItem request
// comes from KrefParts.GetItemTuple, and Kref.ItemName and Kref.Kind read the
// same split.
//
// The parser never fails. A string the kumiho-db kernel refuses comes back with
// KrefParts.ErrorClass set and no reading. Whether a string is accepted is a
// separate question, answered by ValidateKref and not changed here: a kref the
// kernel refuses but this SDK accepts ("?r=0", a 33rd segment, the legacy
// "kref:///space" spelling) is still sent, and the backend decides.

import (
	"regexp"
	"strconv"
	"strings"
	"unicode"
)

const krefScheme = "kref://"

// Limits of the kref grammar.
const (
	MaxKrefBytes         = 1024 // longest base (scheme and query not counted), in UTF-8 bytes
	MaxKrefSegments      = 32   // most "/"-separated segments in a base
	MaxTagBytes          = 1024 // longest tag selector, in UTF-8 bytes
	MaxArtifactNameBytes = 256  // longest artifact selector, in bytes
)

// KrefErrorClass says why the kernel refuses a kref, in the order it checks.
// The empty class means the kernel accepts.
type KrefErrorClass string

// The error classes, spelled as in the corpus.
const (
	KrefErrScheme            KrefErrorClass = "scheme"              // not "kref://" (case-sensitive)
	KrefErrFragmentOrPercent KrefErrorClass = "fragment_or_percent" // a '#' or '%' outside a tag selector
	KrefErrTagReservedChar   KrefErrorClass = "tag_reserved_char"   // a '#', '%' or '&' inside a tag selector
	KrefErrPath              KrefErrorClass = "path"                // the base breaks a path rule
	KrefErrQueryPair         KrefErrorClass = "query_pair"          // a query pair that is not key=value
	KrefErrUnknownKey        KrefErrorClass = "unknown_key"         // a query key other than r, t, a
	KrefErrDuplicateKey      KrefErrorClass = "duplicate_key"       // a query key given twice
	KrefErrRAndT             KrefErrorClass = "r_and_t"             // both r and t
	KrefErrRevisionNumber    KrefErrorClass = "revision_number"     // an r that is not a positive u64 (or "latest")
	KrefErrTag               KrefErrorClass = "tag"                 // a t that is not a valid tag
	KrefErrArtifact          KrefErrorClass = "artifact"            // an a without r/t, or not a valid artifact name
)

// KrefShape is a namespace a base can satisfy, in the order the kernel parser
// and the resolver try them.
type KrefShape string

// The shapes, spelled as in the corpus.
const (
	KrefShapeRootItem KrefShape = "root_item" // an item directly under the project: exactly two segments
	KrefShapeItem     KrefShape = "item"      // an item in a space: three or more segments
	KrefShapeSpace    KrefShape = "space"     // a space: two or more segments
	KrefShapeProject  KrefShape = "project"   // a project: one segment
)

// KrefParts is a kref read once: the kernel's reading plus the textual split.
//
// The kernel's reading (ErrorClass, Base, Shapes and the fields below) follows
// spec/kref/README.md. A kref the kernel refuses has ErrorClass set and no
// reading: Base and every field are nil and Shapes is empty.
//
// ItemName, Kind and IsProjectRootItem describe the first shape the base
// satisfies; ItemName and Kind are nil when that shape is a space or a project.
//
// The textual split (Path, Parent, Leaf, LeafName, LeafKind) does not depend on
// the kernel's verdict. GetItemTuple uses it, so a kref this SDK passes through
// to the backend still yields its request.
type KrefParts struct {
	URI        string         // the string that was parsed
	ErrorClass KrefErrorClass // why the kernel refuses it; "" when it accepts

	Base              *string     // the text between "kref://" and the first "?"
	Shapes            []KrefShape // every namespace the base satisfies, in resolver order
	Project           *string     // the first segment
	SpacePath         []string    // the spaces between the project and the item (all of them for a space)
	ItemName          *string     // the leaf up to its last "."
	Kind              *string     // the leaf after its last "."
	IsProjectRootItem *bool       // whether the item sits directly under the project
	Revision          *uint64     // the revision number from r=
	Tag               *string     // the tag from t= ("r=latest" reads as the tag "latest")
	Artifact          *string     // the artifact name from a=

	Path     string  // the text after the first "://" and before the first "?"
	Parent   *string // everything before the last "/" of Path
	Leaf     *string // everything after the last "/" of Path
	LeafName *string // the leaf up to its last "."
	LeafKind *string // the leaf after its last "."
}

// Valid reports whether the kumiho-db kernel accepts this kref.
func (p KrefParts) Valid() bool { return p.ErrorClass == "" }

// GetItemTuple returns the GetItem request (parentPath, itemName, kind) for
// this kref.
//
// The parent path is "/" plus everything before the LAST "/" of the path, so it
// holds the project and every nested space. The leaf after it is split at its
// LAST ".": item names may contain dots, kinds never do. The query is dropped.
//
// This is the one split used for every item lookup. It depends on the text
// only, never on the kernel's verdict.
//
// It returns an *InvalidArgumentError if the path has no "/" or its leaf has no
// ".". A leaf without a dot ("kref://p/s.v1/x") names a space, not an item.
func (p KrefParts) GetItemTuple() (parentPath, itemName, kind string, err error) {
	if p.Parent == nil || p.Leaf == nil {
		return "", "", "", &InvalidArgumentError{Msg: "invalid item kref: " + p.URI}
	}
	if p.LeafName == nil || p.LeafKind == nil {
		return "", "", "", &InvalidArgumentError{Msg: "invalid item name.kind: " + *p.Leaf}
	}
	return "/" + *p.Parent, *p.LeafName, *p.LeafKind, nil
}

// lexical is the purely textual split of a kref: no grammar is applied.
type lexical struct {
	path                             string
	parent, leaf, leafName, leafKind *string
}

// splitLexical cuts uri at the first "://", the first "?", the last "/" and the
// last ".". It is the one place a kref is split into parent path, item name and
// kind, and it never fails: leafName and leafKind are nil when the leaf has no
// ".", and parent and leaf are nil when the path has no "/".
func splitLexical(uri string) lexical {
	path := uri
	if i := strings.Index(path, "://"); i >= 0 {
		path = path[i+3:]
	}
	if i := strings.IndexByte(path, '?'); i >= 0 {
		path = path[:i]
	}
	lex := lexical{path: path}
	slash := strings.LastIndexByte(path, '/')
	if slash < 0 {
		return lex
	}
	parent, leaf := path[:slash], path[slash+1:]
	lex.parent, lex.leaf = &parent, &leaf
	// Item names may contain dots; kinds never do.
	if dot := strings.LastIndexByte(leaf, '.'); dot >= 0 {
		name, kind := leaf[:dot], leaf[dot+1:]
		lex.leafName, lex.leafKind = &name, &kind
	}
	return lex
}

// ParseKref parses uri once into a KrefParts. It never fails: a string the
// kernel refuses comes back with ErrorClass set.
func ParseKref(uri string) KrefParts {
	lex := splitLexical(uri)
	parts := KrefParts{
		URI:      uri,
		Path:     lex.path,
		Parent:   lex.parent,
		Leaf:     lex.leaf,
		LeafName: lex.leafName,
		LeafKind: lex.leafKind,
	}
	reading, class := readKref(uri)
	if class != "" {
		parts.ErrorClass = class
		return parts
	}
	parts.Base = &reading.base
	parts.Shapes = reading.shapes
	parts.Project = &reading.project
	parts.SpacePath = reading.spacePath
	parts.ItemName = reading.itemName
	parts.Kind = reading.kind
	parts.IsProjectRootItem = &reading.isProjectRootItem
	parts.Revision = reading.revision
	parts.Tag = reading.tag
	parts.Artifact = reading.artifact
	return parts
}

type krefReading struct {
	base              string
	shapes            []KrefShape
	project           string
	spacePath         []string
	itemName, kind    *string
	isProjectRootItem bool
	revision          *uint64
	tag, artifact     *string
}

// readKref returns the kernel's verdict and reading of uri.
func readKref(uri string) (krefReading, KrefErrorClass) {
	var none krefReading
	if !strings.HasPrefix(uri, krefScheme) {
		return none, KrefErrScheme
	}
	rest := uri[len(krefScheme):]
	base, query, hasQuery := strings.Cut(rest, "?")
	if strings.ContainsAny(rest, "#%") {
		inTag := false
		if hasQuery {
			for _, pair := range strings.Split(query, "&") {
				if v, ok := strings.CutPrefix(pair, "t="); ok && strings.ContainsAny(v, "#%") {
					inTag = true
				}
			}
		}
		if inTag {
			return none, KrefErrTagReservedChar
		}
		return none, KrefErrFragmentOrPercent
	}
	shapes := pathShapes(base)
	if len(shapes) == 0 {
		return none, KrefErrPath
	}
	var revision *uint64
	var tag, artifact *string
	if hasQuery {
		var class KrefErrorClass
		revision, tag, artifact, class = readQuery(query)
		if class != "" {
			return none, class
		}
	}

	segments := strings.Split(base, "/")
	reading := krefReading{
		base:      base,
		shapes:    shapes,
		project:   segments[0],
		spacePath: []string{},
		revision:  revision,
		tag:       tag,
		artifact:  artifact,
	}
	switch shapes[0] {
	case KrefShapeRootItem, KrefShapeItem:
		leaf := segments[len(segments)-1]
		dot := strings.LastIndexByte(leaf, '.')
		name, kind := leaf[:dot], leaf[dot+1:]
		reading.spacePath = append(reading.spacePath, segments[1:len(segments)-1]...)
		reading.itemName, reading.kind = &name, &kind
		reading.isProjectRootItem = shapes[0] == KrefShapeRootItem
	case KrefShapeSpace:
		reading.spacePath = append(reading.spacePath, segments[1:]...)
	}
	return reading, ""
}

// isWordRune reports whether r is in the kernel's word class, the `\w` of its
// segment rule ^\w[\w.-]*$.
func isWordRune(r rune) bool {
	// The kernel's \w: Alphabetic | Mark | Decimal_Number | Connector_Punctuation
	// | Join_Control. Alphabetic is the letters, Nl and Other_Alphabetic.
	return unicode.IsLetter(r) || unicode.IsMark(r) ||
		unicode.Is(unicode.Nd, r) || unicode.Is(unicode.Nl, r) || unicode.Is(unicode.Pc, r) ||
		unicode.Is(unicode.Other_Alphabetic, r) || unicode.Is(unicode.Join_Control, r)
}

func hasControl(text string) bool {
	for _, r := range text {
		if unicode.Is(unicode.Cc, r) {
			return true
		}
	}
	return false
}

func segmentOK(segment string) bool {
	if segment == "" {
		return false
	}
	for i, r := range segment {
		if i == 0 {
			if !isWordRune(r) {
				return false
			}
			continue
		}
		if !isWordRune(r) && r != '.' && r != '-' {
			return false
		}
	}
	return true
}

// pathShapes returns every namespace whose path rule base satisfies, in
// resolver order.
func pathShapes(base string) []KrefShape {
	if base == "" || len(base) > MaxKrefBytes || strings.Contains(base, "..") || hasControl(base) {
		return nil
	}
	segments := strings.Split(base, "/")
	if len(segments) > MaxKrefSegments {
		return nil
	}
	for _, s := range segments {
		if !segmentOK(s) {
			return nil
		}
	}
	leaf := segments[len(segments)-1]
	dot := strings.LastIndexByte(leaf, '.')
	namesAnItem := dot > 0 && dot < len(leaf)-1
	count := len(segments)
	var shapes []KrefShape
	if count == 2 && namesAnItem {
		shapes = append(shapes, KrefShapeRootItem)
	}
	if count >= 3 && namesAnItem {
		shapes = append(shapes, KrefShapeItem)
	}
	if count >= 2 {
		shapes = append(shapes, KrefShapeSpace)
	}
	if count == 1 {
		shapes = append(shapes, KrefShapeProject)
	}
	return shapes
}

func validTag(text string) bool {
	return text != "" && len(text) <= MaxTagBytes &&
		!strings.ContainsAny(text, "\"\\") && !hasControl(text)
}

var artifactNamePattern = regexp.MustCompile(`^[A-Za-z0-9._-]+$`)

func validArtifactName(text string) bool {
	return text != "" && len(text) <= MaxArtifactNameBytes && artifactNamePattern.MatchString(text)
}

// readRevision reads a revision number: ASCII digits, no leading zero,
// 1..=u64::MAX.
func readRevision(text string) *uint64 {
	if text == "" || text[0] == '0' {
		return nil
	}
	for i := 0; i < len(text); i++ {
		if text[i] < '0' || text[i] > '9' {
			return nil
		}
	}
	n, err := strconv.ParseUint(text, 10, 64)
	if err != nil || n < 1 {
		return nil
	}
	return &n
}

// readQuery reads the r, t and a selectors of the text after "?".
func readQuery(query string) (revision *uint64, tag, artifact *string, class KrefErrorClass) {
	var r, t, a *string
	for _, pair := range strings.Split(query, "&") {
		key, value, ok := strings.Cut(pair, "=")
		if !ok {
			// A tag holding '&' leaves a pair without '=' behind.
			if t != nil {
				return nil, nil, nil, KrefErrTagReservedChar
			}
			return nil, nil, nil, KrefErrQueryPair
		}
		var slot **string
		switch key {
		case "r":
			slot = &r
		case "t":
			slot = &t
		case "a":
			slot = &a
		default:
			return nil, nil, nil, KrefErrUnknownKey
		}
		if *slot != nil {
			return nil, nil, nil, KrefErrDuplicateKey
		}
		v := value
		*slot = &v
	}
	if r != nil && t != nil {
		return nil, nil, nil, KrefErrRAndT
	}
	switch {
	case r != nil && *r == "latest":
		latest := "latest"
		tag = &latest
	case r != nil:
		if revision = readRevision(*r); revision == nil {
			return nil, nil, nil, KrefErrRevisionNumber
		}
	case t != nil:
		if !validTag(*t) {
			return nil, nil, nil, KrefErrTag
		}
		tag = t
	}
	if a != nil {
		if (revision == nil && tag == nil) || !validArtifactName(*a) {
			return nil, nil, nil, KrefErrArtifact
		}
		artifact = a
	}
	return revision, tag, artifact, ""
}
