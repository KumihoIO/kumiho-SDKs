"""Generate spec/kref/vectors.json, the shared kref conformance corpus.

Run from the repository root:

    python spec/kref/tools/gen_vectors.py

Inputs (all pinned, read-only):
  * spec/kref/tools/snapshots/kref_a7f155e.py  - python/python/kumiho/kref.py at
    origin/main a7f155e (the CURRENT Python SDK client-side grammar), executed
    as-is with its protobuf import stubbed.
  * python/python/kumiho/kref.py (the working tree)  - the fix branch's own
    kref.py, executed live, so the corpus records what the SDK being tested
    sends, not a copy of it. There is no second snapshot to go stale.
  * The kumiho-db kernel parser (src/kernel/model/catalog.rs,
    src/kernel/keys/catalog_components.rs, src/kernel/commands/catalog/reads.rs
    at kumiho-db f013b04c) is ported in `Kernel` below. The port is checked
    against the hand-written expectation of every case here, and the real
    kernel checks the emitted corpus in kumiho-db's
    `kref_vectors_tests` (tests/data/kref-vectors.json). The kernel is the
    authority: if they disagree, this file and the corpus are fixed.
  * kumiho-server 0e4906c `is_valid_kref` (src/utils.rs:56-79) and GetItem
    (src/item.rs:14-31, 436-456) are ported in `Server` below.

The script asserts every hand-written expectation, so a change to any of the
ported rules that moves a case fails loudly instead of silently rewriting the
corpus.
"""

from __future__ import annotations

import json
import re
import sys
import types
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "vectors.json"

# --------------------------------------------------------------------------
# Real Python SDK code (current = a7f155e, fix = branch head).
# --------------------------------------------------------------------------


def _load_sdk(path: Path, name: str):
    source = path.read_text(encoding="utf-8")
    source = source.replace("from .proto import kumiho_pb2", "kumiho_pb2 = None")
    module = types.ModuleType(name)
    # dataclasses resolves string annotations through sys.modules.
    sys.modules[name] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


SDK_CUR = _load_sdk(HERE / "snapshots" / "kref_a7f155e.py", "kref_a7f155e")
SDK_FIX = _load_sdk(HERE.parents[2] / "python" / "python" / "kumiho" / "kref.py", "kref_fix")


def _err(exc: Exception) -> dict:
    return {"error": type(exc).__name__, "message": str(exc)}


def cur_split(kref_uri: str):
    """a7f155e client.py:915-936 get_item_by_kref, verbatim logic."""
    kref = SDK_CUR.Kref(kref_uri)
    item_path = kref.get_path()
    if "/" not in item_path:
        raise ValueError(f"Invalid item kref format: {kref}")
    space_path, item_name_kind = item_path.split("/", 1)
    parent_path = f"/{space_path}"
    if "." not in item_name_kind:
        raise ValueError(f"Invalid item name.kind format: {item_name_kind}")
    item_name, kind = item_name_kind.split(".", 1)
    return parent_path, item_name, kind


def cur_bundle_refetch(kref_uri: str):
    """a7f155e client.py:974-981 (the second GetItem of get_bundle_by_kref)."""
    kref = SDK_CUR.Kref(kref_uri)
    item_path = kref.get_path()
    space_path, item_name_kind = item_path.split("/", 1)
    parent_path = f"/{space_path}"
    bundle_name, _ = item_name_kind.split(".", 1)
    return parent_path, bundle_name, "bundle"


def fix_split(kref_uri: str):
    """The fix branch's client.get_item_by_kref: ``Kref(uri)`` validates, then the
    request is ``parts.get_item_request()`` (kref.py ``KrefParts``)."""
    return SDK_FIX.Kref(kref_uri).parts.get_item_request()


def fix_bundle_refetch(kref_uri: str):
    parent_path, bundle_name, _ = fix_split(kref_uri)
    return parent_path, bundle_name, "bundle"


def cur_get_revision(kref_uri: str) -> dict:
    """a7f155e client.py:1284-1330 get_revision (no client-side validation)."""
    base_kref, tag, time = kref_uri, None, None
    if "?" in kref_uri:
        base_kref, params = kref_uri.split("?", 1)
        for param in params.split("&"):
            if param.startswith("t=") or param.startswith("tag="):
                tag = param.split("=")[1]
            elif param.startswith("time="):
                time = param.split("=")[1]
                if not re.match(r"^\d{12}$", time):
                    return {"error": "ValueError", "message": "time must be in YYYYMMDDHHMM format"}
    if tag is not None or time is not None:
        return {"rpc": "ResolveKref", "kref": base_kref, "tag": tag, "time": time}
    return {"rpc": "GetRevision", "kref": kref_uri}


def cur_resolve(kref: str) -> dict:
    """a7f155e client.py:1859-1888 resolve: the WHOLE kref (query included) plus
    the tag/time it copies out of the query, to ResolveLocation."""
    tag = time = None
    if "?" in kref:
        _, params = kref.split("?", 1)
        for param in params.split("&"):
            if param.startswith("t=") or param.startswith("tag="):
                tag = param.split("=")[1]
            elif param.startswith("time="):
                time = param.split("=")[1]
    return {"rpc": "ResolveLocation", "kref": kref, "tag": tag, "time": time}


def get_item_req(tup) -> dict:
    parent_path, item_name, kind = tup
    return {"rpc": "GetItem", "parent_path": parent_path, "item_name": item_name, "kind": kind}


def call(fn, *args):
    try:
        return fn(*args)
    except Exception as exc:  # noqa: BLE001 - the SDK raises ValueError subclasses
        return exc


ACCESSORS = ["get_path", "get_project", "get_space", "get_item_name", "get_kind",
             "get_revision", "get_artifact_name"]


def accessors(module, uri: str) -> dict:
    kref = module.Kref(uri, validate=False)
    return {name: getattr(kref, name)() for name in ACCESSORS}


# --------------------------------------------------------------------------
# Kernel port (kumiho-db f013b04c). Unicode \w is the Rust regex crate's:
# Alphabetic | M | Nd | Pc | Join_Control (approximated with categories).
# --------------------------------------------------------------------------


def rust_word(ch: str) -> bool:
    cat = unicodedata.category(ch)
    return cat[0] in "LM" or cat in ("Nd", "Nl", "Pc") or ch in "‌‍"


def rust_digit(ch: str) -> bool:
    return unicodedata.category(ch) == "Nd"


def has_control(text: str) -> bool:
    return any(unicodedata.category(ch) == "Cc" for ch in text)


def segment_ok(seg: str) -> bool:
    return (bool(seg) and rust_word(seg[0])
            and all(rust_word(ch) or ch in ".-" for ch in seg[1:]))


MAX_KREF_BYTES = 1024
MAX_KREF_SEGMENTS = 32
MAX_TAG_BYTES = 1024
MAX_ARTIFACT_NAME_BYTES = 256
NAMESPACES = ["root_item", "item", "space", "project"]  # parse_kref / resolve order


def valid_kref_path(ns: str, text: str) -> bool:
    if (not text or len(text.encode()) > MAX_KREF_BYTES or ".." in text
            or has_control(text)):
        return False
    segs = text.split("/")
    count_ok = {"project": len(segs) == 1, "space": len(segs) >= 2,
                "item": len(segs) >= 3, "root_item": len(segs) == 2}[ns]
    if not count_ok or len(segs) > MAX_KREF_SEGMENTS:
        return False
    if not all(segment_ok(s) for s in segs):
        return False
    if ns in ("item", "root_item"):
        name, dot, kind = segs[-1].rpartition(".")
        return bool(dot) and bool(name) and bool(kind)
    return True


def valid_tag(text: str) -> bool:
    return (bool(text) and len(text.encode()) <= MAX_TAG_BYTES
            and '"' not in text and "\\" not in text and not has_control(text))


def valid_artifact_name(text: str) -> bool:
    return (bool(text) and len(text.encode()) <= MAX_ARTIFACT_NAME_BYTES
            and all(ch.isascii() and (ch.isalnum() or ch in "._-") for ch in text))


TAG_SELECTOR_ERROR = "tag selector cannot contain '&', '#' or '%'"
ERROR_CLASS = {
    "a kref starts with kref://": "scheme",
    "a kref has no fragment and no percent escape": "fragment_or_percent",
    TAG_SELECTOR_ERROR: "tag_reserved_char",
    "invalid kref path": "path",
    "a kref query pair is key=value": "query_pair",
    "unknown kref query key": "unknown_key",
    "duplicate kref query key": "duplicate_key",
    "a kref names r or t, not both": "r_and_t",
    "a revision number is a positive integer": "revision_number",
    "invalid tag": "tag",
    "an artifact needs a revision selector and a valid name": "artifact",
}


class KernelError(Exception):
    pass


def parse_number(text: str) -> int:
    digits = bool(text) and all(ch in "0123456789" for ch in text)
    if digits and not text.startswith("0"):
        number = int(text)
        if 1 <= number <= 2**64 - 1:
            return number
    raise KernelError("a revision number is a positive integer")


def kernel_parse(text: str, ns: str):
    if not text.startswith("kref://"):
        raise KernelError("a kref starts with kref://")
    rest = text[len("kref://"):]
    base, sep, query = rest.partition("?")
    query = query if sep else None
    if "#" in rest or "%" in rest:
        reserved = query is not None and any(
            p.startswith("t=") and ("#" in p[2:] or "%" in p[2:]) for p in query.split("&"))
        raise KernelError(TAG_SELECTOR_ERROR if reserved
                          else "a kref has no fragment and no percent escape")
    if not valid_kref_path(ns, base):
        raise KernelError("invalid kref path")
    revision = tag = artifact = None
    if query is not None:
        slots = {"r": None, "t": None, "a": None}
        for pair in query.split("&"):
            key, eq, value = pair.partition("=")
            if not eq:
                raise KernelError(TAG_SELECTOR_ERROR if slots["t"] is not None
                                  else "a kref query pair is key=value")
            if key not in slots:
                raise KernelError("unknown kref query key")
            if slots[key] is not None:
                raise KernelError("duplicate kref query key")
            slots[key] = value
        r, t, a = slots["r"], slots["t"], slots["a"]
        if r is not None and t is not None:
            raise KernelError("a kref names r or t, not both")
        if r == "latest":
            tag = "latest"
        elif r is not None:
            revision = parse_number(r)
        elif t is not None:
            if not valid_tag(t):
                raise KernelError("invalid tag")
            tag = t
        if a is not None:
            if (revision is None and tag is None) or not valid_artifact_name(a):
                raise KernelError("an artifact needs a revision selector and a valid name")
            artifact = a
    return base, revision, tag, artifact


def kernel_parse_kref(text: str):
    """reads.rs:143-164 parse_kref: first namespace that parses wins; the error
    is that of the first namespace whose path fits, else of the last tried."""
    matched = last = None
    base_of = None
    if text.startswith("kref://"):
        base_of = text[len("kref://"):].partition("?")[0]
    for ns in NAMESPACES:
        try:
            return kernel_parse(text, ns)
        except KernelError as exc:
            fits = base_of is not None and valid_kref_path(ns, base_of)
            if fits and matched is None:
                matched = exc
            last = exc
    raise matched or last


# --------------------------------------------------------------------------
# kumiho-server port (0e4906c).
# --------------------------------------------------------------------------

_SERVER_QUERY = re.compile(r"r=\d+(&a=[a-zA-Z0-9._-]+)?")  # \d is Unicode Nd in both


def server_is_valid_kref(kref: str) -> bool:
    """src/utils.rs:56-79 (KREF_REGEX + is_valid_kref)."""
    if ".." in kref or ("//" in kref and not kref.startswith("kref://")):
        return False
    if any(unicodedata.category(c) == "Cc" for c in kref):
        return False
    if not kref.startswith("kref://"):
        return False
    path, sep, query = kref[len("kref://"):].partition("?")
    if not all(segment_ok(s) for s in path.split("/")):
        return False
    return not sep or _SERVER_QUERY.fullmatch(query) is not None


def server_normalize_space_path(path: str) -> str:
    """src/item.rs:14-31."""
    trimmed = path.strip()
    if not trimmed:
        return "/"
    without_trailing = trimmed.rstrip("/")
    if not without_trailing:
        return "/"
    without_leading = without_trailing.lstrip("/")
    return "/" if not without_leading else f"/{without_leading}"


def server_get_item_kref(req: dict) -> str:
    """src/item.rs:443-449: the exact p.kref string GetItem matches."""
    base_path = server_normalize_space_path(req["parent_path"]).lstrip("/")
    if not base_path:
        return f"kref://{req['item_name']}.{req['kind']}"
    return f"kref://{base_path}/{req['item_name']}.{req['kind']}"


# --------------------------------------------------------------------------
# kumiho-db adapter GetItem (crates/kumiho-db-adapter/src/convert/item_reads.rs:69-96).
# --------------------------------------------------------------------------


def kdb_path_of(text: str) -> str:
    if text.startswith("kref://"):
        return text[len("kref://"):]
    if text.startswith("/"):
        return text[1:]
    return text


def kdb_get_item(req: dict) -> str:
    parent = kdb_path_of(req["parent_path"])
    name, kind = req["item_name"], req["kind"]
    if not parent:
        return "INVALID_ARGUMENT: parent_path is required"
    if not name or not kind:
        return "INVALID_ARGUMENT: item_name and kind are required"
    if "/" in name or "." in kind or "/" in kind:
        return "INVALID_ARGUMENT: the kref names no item"
    kref = f"kref://{parent}/{name}.{kind}"
    base = f"{parent}/{name}.{kind}"
    ns = "root_item" if valid_kref_path("root_item", kdb_path_of(kref.partition("?")[0])) else "item"
    try:
        got_base, rev, tag, art = kernel_parse(kref, ns)
    except KernelError:
        try:
            kernel_parse_kref(kref)
        except KernelError as exc:
            return f"INVALID_ARGUMENT: {exc}"
        return f"resolves {kref} (not an item path)"
    if rev is not None or tag is not None or art is not None or got_base != base:
        return "INVALID_ARGUMENT: the kref names no item"
    return f"resolves {kref}"


# --------------------------------------------------------------------------
# The cases. (id, category, input, valid, error_class, note)
# --------------------------------------------------------------------------

I = "kref://p/s/x.k"  # the plain item every query case hangs off

LONG_SEG_1024 = "a" * (MAX_KREF_BYTES - len("p/") - len("/x.k"))
HANGUL_1024 = "가" * 339 + "a"  # 339*3 + 1 = 1018 bytes
assert len(("p/" + HANGUL_1024 + "/x.k").encode()) == 1024
SEGS_32 = "p/" + "/".join(["s"] * 30) + "/x.k"
SEGS_33 = "p/" + "/".join(["s"] * 31) + "/x.k"
SPACE_32 = "/".join(["p"] + ["s"] * 31)
SPACE_33 = "/".join(["p"] + ["s"] * 32)
TAG_1024 = "t" * 1024
ART_256 = "a" * 256

CASES = [
    # --- items: depth -------------------------------------------------------
    ("root-item", "root_item", "kref://p/x.k", True, None, "project-root item: exactly two segments"),
    ("root-item-dotted-name", "root_item", "kref://p/my.file.k", True, None, None),
    ("root-item-revision", "root_item", "kref://p/x.k?r=2", True, None, None),
    ("item-depth-1", "nested_spaces", "kref://p/a/x.k", True, None, None),
    ("item-depth-2", "nested_spaces", "kref://p/a/b/x.k", True, None, None),
    ("item-depth-3", "nested_spaces", "kref://p/a/b/c/x.k", True, None, None),
    ("item-depth-4", "nested_spaces", "kref://p/a/b/c/d/x.k", True, None, None),
    ("item-depth-5", "nested_spaces", "kref://p/a/b/c/d/e/x.k", True, None, None),
    ("item-depth-3-revision-artifact", "nested_spaces", "kref://p/a/b/c/x.k?r=7&a=mesh", True, None, None),
    # --- dotted names -------------------------------------------------------
    ("item-dotted-name", "dotted_names", "kref://p/s/my.file.v2.k", True, None,
     "the kind is the text after the LAST dot of the last segment"),
    ("item-version-like-name", "dotted_names", "kref://p/s/v1.0.k", True, None, None),
    ("item-dotted-name-nested", "dotted_names", "kref://p/a/b/shot.010.plate", True, None, None),
    ("kind-with-dot-unrepresentable", "dotted_names", "kref://p/s/x.tar.gz", True, None,
     "a kind can never contain a dot: this kref is item 'x.tar' of kind 'gz'. "
     "A GetItem asking kind 'tar.gz' is refused by kumiho-db (item_reads.rs:85-87)"),
    ("space-dotted-name", "dotted_names", "kref://p/s.v1/x.k", True, None, None),
    ("spaces-and-name-dotted", "dotted_names", "kref://p/a.b/c.d/x.y.k", True, None, None),
    ("project-dotted-name", "dotted_names", "kref://p.io/s/x.k", True, None, None),
    ("two-segment-dotted-ambiguous", "dotted_names", "kref://p/s.v1", True, None,
     "ambiguous: project-root item 's' of kind 'v1' OR space 'p/s.v1'; the kernel "
     "resolver tries the root item first (resolve.rs:165-184)"),
    # --- bundles ------------------------------------------------------------
    ("bundle", "bundles", "kref://p/s/set.bundle", True, None, None),
    ("bundle-root", "bundles", "kref://p/set.bundle", True, None, None),
    ("bundle-nested", "bundles", "kref://p/a/b/set.bundle", True, None, None),
    ("bundle-dotted-name", "bundles", "kref://p/s/my.set.bundle", True, None,
     "a7f155e get_bundle_by_kref re-fetches kref://p/s/my.bundle (a different node)"),
    ("bundle-in-dotted-space", "bundles", "kref://p/s.v1/set.bundle", True, None,
     "a7f155e get_bundle_by_kref re-fetches kref://p/s.bundle (a different node)"),
    ("bundle-revision", "bundles", "kref://p/s/set.bundle?r=3", True, None, None),
    ("bundle-tag", "bundles", "kref://p/s/set.bundle?t=published", True, None, None),
    # --- spaces and projects -----------------------------------------------
    ("project", "project_space", "kref://p", True, None, None),
    ("space", "project_space", "kref://p/a", True, None, None),
    ("space-depth-5", "project_space", "kref://p/a/b/c/d/e", True, None, None),
    ("item-without-dot-is-space", "missing_kind", "kref://p/s/x", True, None,
     "no dot in the last segment: only a space path"),
    ("dotted-space-leaf-without-dot", "missing_kind", "kref://p/s.v1/x", True, None,
     "a space path; the current SDK still sends GetItem('/p', 's', 'v1/x'), the fix raises"),
    ("missing-kind-is-space", "missing_kind", "kref://p/s/x.", True, None,
     "empty kind: not an item, but 'x.' is a valid space segment"),
    ("missing-kind-root", "missing_kind", "kref://p/x.", True, None, "a space path, not a root item"),
    ("missing-name", "missing_kind", "kref://p/s/.k", False, "path", "a segment starts with a word character"),
    ("project-with-selector", "project_space", "kref://p?r=1", True, None,
     "parses; resolve refuses a selector on a project or space (resolve.rs:196-198)"),
    ("space-with-tag", "project_space", "kref://p/s?t=published", True, None,
     "parses; resolve refuses a selector on a project or space (resolve.rs:196-198)"),
    # --- revision selector r -----------------------------------------------
    ("r-1", "query_r", I + "?r=1", True, None, None),
    ("r-42", "query_r", I + "?r=42", True, None, None),
    ("r-latest", "query_r", I + "?r=latest", True, None, "r=latest is the tag 'latest', not a number"),
    ("r-u64-max", "query_r", I + "?r=18446744073709551615", True, None, None),
    ("r-u64-overflow", "query_r", I + "?r=18446744073709551616", False, "revision_number", None),
    ("r-zero", "query_r", I + "?r=0", False, "revision_number", None),
    ("r-leading-zero", "query_r", I + "?r=01", False, "revision_number", None),
    ("r-negative", "query_r", I + "?r=-1", False, "revision_number", None),
    ("r-plus-sign", "query_r", I + "?r=+1", False, "revision_number", None),
    ("r-empty", "query_r", I + "?r=", False, "revision_number", None),
    ("r-decimal", "query_r", I + "?r=1.5", False, "revision_number", None),
    ("r-unicode-digit", "query_r", I + "?r=٣", False, "revision_number",
     "ASCII digits only; Python \\d and the server's Rust \\d accept U+0663"),
    ("r-second-question-mark", "query_r", I + "?r=1?a=b", False, "revision_number",
     "only the first '?' starts the query"),
    # --- tag selector t -----------------------------------------------------
    ("t-published", "query_t", I + "?t=published", True, None, None),
    ("t-latest", "query_t", I + "?t=latest", True, None, None),
    ("t-dotted", "query_t", I + "?t=v1.0", True, None, None),
    ("t-korean", "query_t", I + "?t=검토", True, None, None),
    ("t-space", "query_t", I + "?t=my tag", True, None, "tags may hold spaces (tag_rules.rs:22-32)"),
    ("t-equals", "query_t", I + "?t=a=b", True, None,
     "the pair splits at its first '='; a7f155e get_revision sends tag 'a'"),
    ("t-question-mark", "query_t", I + "?t=a?b", True, None, None),
    ("t-max-bytes", "query_t", I + "?t=" + TAG_1024, True, None, "1,024-byte tag"),
    ("t-over-max-bytes", "query_t", I + "?t=" + TAG_1024 + "t", False, "tag", "1,025-byte tag"),
    ("t-empty", "query_t", I + "?t=", False, "tag", None),
    ("t-double-quote", "query_t", I + '?t=a"b', False, "tag", None),
    ("t-backslash", "query_t", I + "?t=a\\b", False, "tag", None),
    ("t-ampersand", "query_t", I + "?t=a&b", False, "tag_reserved_char", None),
    ("t-percent", "query_t", I + "?t=a%20b", False, "tag_reserved_char", None),
    ("t-hash", "query_t", I + "?t=a#b", False, "tag_reserved_char", None),
    # --- artifact a ---------------------------------------------------------
    ("a-with-r", "query_a", I + "?r=2&a=mesh", True, None, None),
    ("a-before-r", "query_a", I + "?a=mesh&r=2", True, None, "key order is free"),
    ("a-with-t", "query_a", I + "?t=published&a=mesh.fbx", True, None, None),
    ("a-with-r-latest", "query_a", I + "?r=latest&a=mesh", True, None, None),
    ("a-double-dot", "query_a", I + "?r=1&a=x..y", True, None,
     "'..' is checked in the base path only"),
    ("a-max-bytes", "query_a", I + "?r=1&a=" + ART_256, True, None, "256-byte artifact name"),
    ("a-over-max-bytes", "query_a", I + "?r=1&a=" + ART_256 + "a", False, "artifact", None),
    ("a-without-selector", "query_a", I + "?a=mesh", False, "artifact", "an artifact needs r or t"),
    ("a-empty", "query_a", I + "?r=1&a=", False, "artifact", None),
    ("a-non-ascii", "query_a", I + "?r=1&a=mésh", False, "artifact", None),
    ("a-slash", "query_a", I + "?r=1&a=dir/mesh", False, "artifact", None),
    ("bundle-artifact-parses", "query_a", "kref://p/s/set.bundle?r=1&a=mesh", True, None,
     "parses; the resolver decides whether a bundle revision has artifacts"),
    # --- combinations, duplicates, unknown keys, pair syntax ---------------
    ("r-and-t", "query_combination", I + "?r=1&t=published", False, "r_and_t", None),
    ("t-and-r", "query_combination", I + "?t=published&r=1", False, "r_and_t", None),
    ("dup-r", "duplicate_keys", I + "?r=1&r=1", False, "duplicate_key", None),
    ("dup-t", "duplicate_keys", I + "?t=a&t=b", False, "duplicate_key", None),
    ("dup-a", "duplicate_keys", I + "?r=1&a=x&a=y", False, "duplicate_key", None),
    ("legacy-v", "unknown_keys", I + "?v=1", False, "unknown_key", "the legacy ?v= spelling"),
    ("time-in-kref", "unknown_keys", I + "?time=202406011330", False, "unknown_key",
     "time is never a kref key: it travels in ResolveKrefRequest.time"),
    ("t-and-time", "unknown_keys", I + "?t=published&time=202406011330", False, "unknown_key", None),
    ("tag-long-key", "unknown_keys", I + "?tag=published", False, "unknown_key", "only 't', not 'tag'"),
    ("uppercase-key", "unknown_keys", I + "?R=1", False, "unknown_key", "keys are case-sensitive"),
    ("empty-key", "unknown_keys", I + "?=1", False, "unknown_key", None),
    ("r-then-unknown", "unknown_keys", I + "?r=1&v=2", False, "unknown_key", None),
    ("empty-query", "query_pair", I + "?", False, "query_pair", None),
    ("trailing-ampersand", "query_pair", I + "?r=1&", False, "query_pair", None),
    ("leading-ampersand", "query_pair", I + "?&r=1", False, "query_pair", None),
    ("key-without-value", "query_pair", I + "?r", False, "query_pair", None),
    # --- scheme, fragment, percent -----------------------------------------
    ("no-scheme", "scheme", "p/s/x.k", False, "scheme", None),
    ("empty-string", "scheme", "", False, "scheme", None),
    ("uppercase-scheme", "scheme", "KREF://p/s/x.k", False, "scheme", None),
    ("kumiho-scheme", "scheme", "kumiho://p/s/x.k", False, "scheme", "the C++ SDK accepts it"),
    ("single-slash-scheme", "scheme", "kref:/p/s/x.k", False, "scheme", None),
    ("fragment", "fragment_percent", I + "#frag", False, "fragment_or_percent", None),
    ("fragment-after-query", "fragment_percent", I + "?r=1#x", False, "fragment_or_percent", None),
    ("percent-in-path", "fragment_percent", "kref://p/s/x%2Ey.k", False, "fragment_or_percent",
     "no percent decoding anywhere"),
    # --- path shape: empty segments, slashes, characters -------------------
    ("scheme-only", "empty_segments", "kref://", False, "path", None),
    ("legacy-leading-slash-item", "empty_segments", "kref:///s/x.k", False, "path",
     "the legacy root-level spelling; the current Python SDK accepts it"),
    ("legacy-leading-slash-root-item", "empty_segments", "kref:///x.k", False, "path",
     "legacy root-level spelling with no space"),
    ("legacy-leading-slash-nested", "empty_segments", "kref:///s/t/x.k", False, "path", None),
    ("legacy-leading-slash-space", "empty_segments", "kref:///s", False, "path", None),
    ("empty-middle-segment", "empty_segments", "kref://p//x.k", False, "path", None),
    ("trailing-slash-space", "trailing_slash", "kref://p/s/", False, "path", None),
    ("trailing-slash-item", "trailing_slash", "kref://p/s/x.k/", False, "path", None),
    ("trailing-slash-project", "trailing_slash", "kref://p/", False, "path", None),
    ("dot-segment", "path_characters", "kref://p/./x.k", False, "path", None),
    ("dotdot-segment", "path_characters", "kref://p/../x.k", False, "path", None),
    ("dotdot-inside-name", "path_characters", "kref://p/s/x..k", False, "path", "no '..' anywhere in the base"),
    ("hyphen-first", "path_characters", "kref://p/-s/x.k", False, "path", None),
    ("dot-first", "path_characters", "kref://p/s/.x.k", False, "path", None),
    ("space-in-name", "path_characters", "kref://p/s/my item.k", False, "path", None),
    ("trailing-space", "path_characters", "kref://p/s/x.k ", False, "path", None),
    ("control-char", "path_characters", "kref://p/s/x\u0007.k", False, "path", None),
    ("hyphen-underscore-digits", "path_characters", "kref://my-proj/_s/2024-01/item_1.my-kind", True, None, None),
    ("case-preserved", "path_characters", "kref://P/S/X.K", True, None, "exact bytes, no case folding"),
    # --- unicode ------------------------------------------------------------
    ("unicode-korean", "unicode", "kref://프로젝트/공간/캐릭터.모델", True, None, None),
    ("unicode-cjk", "unicode", "kref://映画/キャラ/主人公.model", True, None, None),
    ("unicode-latin-nfc", "unicode", "kref://café/résumé/naïve.doc", True, None, None),
    ("unicode-nfd-read", "unicode", "kref://p/s/é.k", True, None,
     "reads accept a combining mark (Rust \\w includes \\p{M}); creating such a name is "
     "refused (not NFC, kref_write_rules.rs); Python's \\w rejects it"),
    ("unicode-zwj-read", "unicode", "kref://p/s/a‍b.k", True, None,
     "reads accept U+200D (Rust \\w includes Join_Control); creating it is refused by default"),
    ("unicode-arabic-digit-segment", "unicode", "kref://p/s/item٣.k", True, None, None),
    ("unicode-emoji", "unicode", "kref://p/s/\U0001F98A.k", False, "path", "emoji is not \\w"),
    # --- limits -------------------------------------------------------------
    ("limit-1024-bytes", "limits", "kref://p/" + LONG_SEG_1024 + "/x.k", True, None,
     "base exactly 1,024 bytes (scheme and query not counted)"),
    ("limit-1025-bytes", "limits", "kref://p/" + LONG_SEG_1024 + "a/x.k", False, "path", None),
    ("limit-1024-bytes-hangul", "limits", "kref://p/" + HANGUL_1024 + "/x.k", True, None,
     "the limit counts UTF-8 bytes, not characters"),
    ("limit-1025-bytes-hangul", "limits", "kref://p/" + HANGUL_1024 + "a/x.k", False, "path", None),
    ("limit-query-not-counted", "limits", "kref://p/" + LONG_SEG_1024 + "/x.k?t=" + TAG_1024, True, None,
     "a 1,024-byte base plus a 1,024-byte tag"),
    ("limit-32-segments", "limits", "kref://" + SEGS_32, True, None, None),
    ("limit-33-segments", "limits", "kref://" + SEGS_33, False, "path", None),
    ("limit-32-segment-space", "limits", "kref://" + SPACE_32, True, None, None),
    ("limit-33-segment-space", "limits", "kref://" + SPACE_33, False, "path", None),
]


# --------------------------------------------------------------------------
# Derivation.
# --------------------------------------------------------------------------


def primary_reading(base: str, shapes: list) -> dict:
    segs = base.split("/")
    out = {"project": segs[0], "space_path": [], "item_name": None, "kind": None,
           "is_project_root_item": False, "get_item_tuple": None}
    first = shapes[0]
    if first in ("item", "root_item"):
        name, _, kind = segs[-1].rpartition(".")
        out.update(space_path=segs[1:-1], item_name=name, kind=kind,
                   is_project_root_item=first == "root_item",
                   get_item_tuple={"parent_path": "/" + "/".join(segs[:-1]),
                                   "item_name": name, "kind": kind})
    elif first == "space":
        out["space_path"] = segs[1:]
    return out


def sdk_policy(kernel_valid: bool, sdk_accepts: bool) -> str:
    if kernel_valid and sdk_accepts:
        return "accept"
    if not kernel_valid and not sdk_accepts:
        return "reject"
    if sdk_accepts:
        return "pass_through"  # the backend decides; the SDK keeps sending it
    return "sdk_may_relax"  # the kernel accepts; the SDK may (not must) accept later


SERVER_GET_ITEM_CITE = ("kumiho-server 0e4906c src/item.rs:436-456: GetItem builds "
                        "kref://{normalize_space_path(parent_path) without leading '/'}/{item_name}.{kind} "
                        "(item.rs:14-31) and matches p.kref by exact string; no other request field "
                        "selects the node")


def equivalence(old, new) -> dict | None:
    old_ok = not isinstance(old, Exception)
    new_ok = not isinstance(new, Exception)
    if not old_ok and not new_ok:
        return None
    entry = {
        "old_request": get_item_req(old) if old_ok else _err(old),
        "new_request": get_item_req(new) if new_ok else _err(new),
        "identical_request": old_ok and new_ok and old == new,
        "server_kref_old": server_get_item_kref(get_item_req(old)) if old_ok else None,
        "server_kref_new": server_get_item_kref(get_item_req(new)) if new_ok else None,
        "kumiho_db_old": kdb_get_item(get_item_req(old)) if old_ok else None,
        "kumiho_db_new": kdb_get_item(get_item_req(new)) if new_ok else None,
        "citation": SERVER_GET_ITEM_CITE,
    }
    if old_ok and new_ok:
        entry["equivalent"] = entry["server_kref_old"] == entry["server_kref_new"]
    else:
        entry["equivalent"] = False
    entry["flag"] = None
    if not entry["equivalent"]:
        if old_ok and not new_ok:
            entry["flag"] = ("FIX IS STRICTER: the current SDK sends this request and the fix raises "
                             "before sending")
        elif new_ok and not old_ok:
            entry["flag"] = "the fix sends a request where the current SDK raised"
        else:
            entry["flag"] = ("NOT EQUIVALENT: the current SDK's request names a different node "
                             f"({entry['server_kref_old']}) than the fix ({entry['server_kref_new']})")
    return entry


def build_case(case) -> dict:
    cid, category, text, exp_valid, exp_class, note = case
    rec = {"id": cid, "category": category, "input": text}
    try:
        base, revision, tag, artifact = kernel_parse_kref(text)
        valid, kernel_error = True, None
    except KernelError as exc:
        valid, kernel_error = False, str(exc)
    error_class = ERROR_CLASS[kernel_error] if kernel_error else None
    if (valid, error_class) != (exp_valid, exp_class):
        sys.exit(f"{cid}: port says valid={valid} class={error_class}, "
                 f"expected valid={exp_valid} class={exp_class}")
    rec.update(valid=valid, error_class=error_class, kernel_error=kernel_error)
    if valid:
        shapes = [ns for ns in NAMESPACES if valid_kref_path(ns, base)]
        reading = primary_reading(base, shapes)
        rec.update(base=base, shapes=shapes, project=reading["project"],
                   space_path=reading["space_path"], item_name=reading["item_name"],
                   kind=reading["kind"], is_project_root_item=reading["is_project_root_item"],
                   revision=revision, tag=tag, artifact=artifact, time=None,
                   get_item_tuple=reading["get_item_tuple"])
    else:
        rec.update(base=None, shapes=[], project=None, space_path=None, item_name=None,
                   kind=None, is_project_root_item=None, revision=None, tag=None,
                   artifact=None, time=None, get_item_tuple=None)

    server_ok = server_is_valid_kref(text)
    sdk_ok = SDK_CUR.is_valid_kref(text)
    rec["server_accepts"] = server_ok
    rec["sdk_current_accepts"] = sdk_ok
    rec["sdk_policy"] = sdk_policy(valid, sdk_ok)

    cur = call(cur_split, text)
    fix = call(fix_split, text)
    # get_bundle_by_kref re-fetches only after the first GetItem returned an item
    # of kind 'bundle' (client.py:965-971); a bundle's kref ends in '.bundle'.
    is_bundle = not isinstance(fix, Exception) and fix[2] == "bundle"
    skipped = {"skipped": "not a bundle kref: get_bundle_by_kref raises ValueError after "
                          "the first GetItem (a7f155e client.py:965-971)"}
    if is_bundle:
        cur_b2 = call(cur_bundle_refetch, text) if not isinstance(cur, Exception) else cur
        fix_b2 = call(fix_bundle_refetch, text)
    else:
        cur_b2 = fix_b2 = None
    rec["sdk_current_request"] = {
        "get_item_by_kref": get_item_req(cur) if not isinstance(cur, Exception) else _err(cur),
        "get_bundle_by_kref_refetch": (skipped if cur_b2 is None else
                                       get_item_req(cur_b2) if not isinstance(cur_b2, Exception)
                                       else _err(cur_b2)),
        "get_revision": cur_get_revision(text),
        "resolve": cur_resolve(text),
    }
    rec["sdk_fix_request"] = {
        "get_item_by_kref": get_item_req(fix) if not isinstance(fix, Exception) else _err(fix),
        "get_bundle_by_kref_refetch": (skipped if fix_b2 is None else
                                       get_item_req(fix_b2) if not isinstance(fix_b2, Exception)
                                       else _err(fix_b2)),
    }
    eq_item = equivalence(cur, fix)
    eq_bundle = equivalence(cur_b2, fix_b2) if is_bundle else None
    rec["server_equivalent_old_new"] = (
        None if eq_item is None and eq_bundle is None
        else {"get_item_by_kref": eq_item, "get_bundle_by_kref_refetch": eq_bundle})

    if sdk_ok:
        old_acc, new_acc = accessors(SDK_CUR, text), accessors(SDK_FIX, text)
        rec["sdk_current_accessors"] = old_acc
        rec["sdk_fix_accessor_changes"] = {
            k: {"current": old_acc[k], "fix": new_acc[k]}
            for k in ACCESSORS if old_acc[k] != new_acc[k]} or None
    else:
        rec["sdk_current_accessors"] = None
        rec["sdk_fix_accessor_changes"] = None
    rec["note"] = note
    return rec


INVISIBLE = {"́": "\\u0301", "‍": "\\u200d"}


def main() -> None:
    ids = [c[0] for c in CASES]
    assert len(ids) == len(set(ids)), "duplicate case id"
    cases = [build_case(c) for c in CASES]
    # Root-level item requests must stay byte-identical (owner constraint 4):
    # every exception is flagged in the case and printed here.
    for rec in cases:
        eq = rec["server_equivalent_old_new"]
        root = rec["valid"] and rec["is_project_root_item"]
        legacy_root = rec["input"].startswith("kref:///")
        if not ((root or legacy_root) and eq):
            continue
        for slot, entry in eq.items():
            if entry and not entry["identical_request"]:
                entry["flag"] = ("ROOT-LEVEL REQUEST CHANGED"
                                 + (" (legacy kref:/// spelling)" if legacy_root else "")
                                 + " (server-equivalent: "
                                 f"{entry['equivalent']}); " + (entry["flag"] or ""))
                print(f"FLAG {rec['id']} {slot}: {entry['old_request']} -> {entry['new_request']}")
    doc = {
        "schema": "kumiho-kref-vectors/1",
        "spec": "spec/kref/README.md",
        "sources": {
            "kernel": "kumiho-db f013b04c: src/kernel/commands/catalog/reads.rs:143-164 parse_kref, "
                      "src/kernel/model/catalog.rs:136-237 KrefQuery, "
                      "src/kernel/keys/catalog_components.rs:17-205, src/kernel/keys/tag_rules.rs:8-32",
            "server": "kumiho-server 0e4906c: src/utils.rs:56-79 is_valid_kref, src/item.rs:14-31 "
                      "normalize_space_path, src/item.rs:436-456 get_item",
            "sdk_current": "kumiho SDKs a7f155e: python/python/kumiho/kref.py:70-123 _KREF_PATTERN/"
                           "validate_kref, client.py:915-981 get_item_by_kref/get_bundle_by_kref, "
                           "client.py:1284-1330 get_revision, client.py:1859-1888 resolve",
            "sdk_fix": "branch fix/kref-structured-parser-20261029: python/python/kumiho/kref.py "
                       "parse_kref / KrefParts.get_item_request / Kref.get_kind, executed live by "
                       "gen_vectors.py; client.py get_item_by_kref, get_bundle_by_kref, "
                       "get_item_from_revision",
        },
        "fields": {
            "valid / error_class / kernel_error": "kumiho-db kernel parse_kref verdict and exact message",
            "base": "the path between kref:// and the first '?'",
            "shapes": "every namespace whose path rule the base satisfies, in resolver order "
                      "(root_item, item, space, project); the item fields describe the first",
            "time": "always null: time is not a kref key (it travels in ResolveKrefRequest.time)",
            "get_item_tuple": "the GetItem (parent_path, item_name, kind) the grammar gives the "
                              "first item reading; null when the base is not an item",
            "server_accepts": "kumiho-server is_valid_kref (enforced only where it builds a kref: "
                              "create_item, batch rows); its read RPCs match stored strings",
            "sdk_current_accepts": "Python SDK a7f155e validate_kref (Kref() constructor)",
            "sdk_policy": "accept | reject | pass_through (SDK sends, backend decides) | "
                          "sdk_may_relax (kernel accepts, today's SDK refuses)",
            "sdk_current_request": "requests the a7f155e Python SDK sends for this string",
            "sdk_fix_request": "requests the split-fix branch sends",
            "server_equivalent_old_new": "whether kumiho-server resolves the old and new request "
                                         "to the same p.kref (null when neither sends one)",
        },
        "cases": cases,
    }
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    for ch, esc in INVISIBLE.items():
        text = text.replace(ch, esc)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
