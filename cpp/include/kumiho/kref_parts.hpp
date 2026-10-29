/**
 * @file kref_parts.hpp
 * @brief The structured kref parser.
 *
 * parseKref() reads a kref once, with the grammar in spec/kref/README.md that
 * kumiho-db and every Kumiho SDK share, and returns a KrefParts. It is the only
 * place a kref string is cut into pieces for an item lookup: the GetItem request
 * comes from KrefParts::getItemTuple(), and Kref::getItemName() and
 * Kref::getKind() read the same split.
 *
 * The parser never throws. A string the kumiho-db kernel refuses comes back with
 * KrefParts::error_class set and no reading. Whether a string is *accepted* is a
 * separate question, answered by validateKref() and not changed by the parser: a
 * kref the kernel refuses but this SDK sends anyway (`?r=0`, a 33rd segment, the
 * legacy `kref:///space` spelling) is still sent, and the backend decides.
 */

#pragma once

#include <cstdint>
#include <optional>
#include <string>
#include <vector>

namespace kumiho {
namespace api {

/** Why the kernel refuses a kref, in the order it checks. None means it accepts. */
enum class KrefErrorClass {
    None,
    Scheme,             ///< not `kref://` (the scheme is case-sensitive)
    FragmentOrPercent,  ///< a `#` or `%` outside a tag selector
    TagReservedChar,    ///< a `#`, `%` or `&` inside a tag selector
    Path,               ///< the base breaks a path rule
    QueryPair,          ///< a query pair that is not `key=value`
    UnknownKey,         ///< a query key other than `r`, `t`, `a`
    DuplicateKey,       ///< a query key given twice
    RAndT,              ///< both `r` and `t`
    RevisionNumber,     ///< an `r` that is not a positive u64 (or `latest`)
    Tag,                ///< a `t` that is not a valid tag
    Artifact,           ///< an `a` without `r`/`t`, or not a valid artifact name
};

/** The corpus spelling of an error class, for example "revision_number"; "" for None. */
const char* toString(KrefErrorClass error);

/** A namespace a base can satisfy, in the order the kernel parser and resolver try them. */
enum class KrefShape {
    RootItem,  ///< an item directly under the project: exactly two segments
    Item,      ///< an item in a space: three or more segments
    Space,     ///< a space: two or more segments
    Project,   ///< a project: one segment
};

/** The corpus spelling of a shape, for example "root_item". */
const char* toString(KrefShape shape);

/** The GetItem request for an item kref. */
struct KrefItemTuple {
    std::string parent_path;  ///< "/" plus everything before the last '/' of the path
    std::string item_name;    ///< the leaf up to its last '.'
    std::string kind;         ///< the leaf after its last '.'
};

/** The purely textual split of a kref: no grammar is applied. */
struct KrefLexical {
    std::string path;                       ///< after the first "://", before the first '?'
    std::optional<std::string> parent;      ///< everything before the last '/' of path
    std::optional<std::string> leaf;        ///< everything after the last '/' of path
    std::optional<std::string> leaf_name;   ///< the leaf up to its last '.'
    std::optional<std::string> leaf_kind;   ///< the leaf after its last '.'
};

/**
 * @brief Split a leaf (`name.kind`) at its LAST '.'.
 *
 * Item names may contain dots; kinds never do. Returns false, leaving the
 * outputs untouched, when the leaf has no '.'.
 */
bool splitLeaf(const std::string& leaf, std::string& name, std::string& kind);

/**
 * @brief Cut a kref at the first "://", the first '?', the last '/' and the last '.'.
 *
 * This is the one place a kref is split into parent path, item name and kind. It
 * never fails: leaf_name and leaf_kind are empty when the leaf has no '.', and
 * parent and leaf are empty when the path has no '/'. Item names may contain
 * dots; kinds never do.
 */
KrefLexical splitKref(const std::string& uri);

/**
 * @brief A kref read once: the kernel's reading plus the textual split.
 *
 * The kernel's reading (error_class, base, shapes and the fields below) follows
 * spec/kref/README.md. A kref the kernel refuses has error_class set and no
 * reading: base and every field are empty and shapes is empty.
 *
 * item_name, kind and is_project_root_item describe the *first* shape the base
 * satisfies; item_name and kind are empty when that shape is a space or a project.
 *
 * The textual split (path, parent, leaf, leaf_name, leaf_kind) does not depend on
 * the kernel's verdict. getItemTuple() uses it, so a kref this SDK passes through
 * to the backend still yields its request.
 */
struct KrefParts {
    std::string uri;  ///< the string that was parsed
    KrefErrorClass error_class = KrefErrorClass::None;

    std::optional<std::string> base;  ///< the text between "kref://" and the first '?'
    std::vector<KrefShape> shapes;    ///< every namespace the base satisfies, in resolver order
    std::optional<std::string> project;
    std::optional<std::vector<std::string>> space_path;
    std::optional<std::string> item_name;
    std::optional<std::string> kind;
    std::optional<bool> is_project_root_item;
    std::optional<std::uint64_t> revision;  ///< from `r=`
    std::optional<std::string> tag;         ///< from `t=` (`r=latest` reads as the tag "latest")
    std::optional<std::string> artifact;    ///< from `a=`

    std::string path;
    std::optional<std::string> parent;
    std::optional<std::string> leaf;
    std::optional<std::string> leaf_name;
    std::optional<std::string> leaf_kind;

    /** Whether the kumiho-db kernel accepts this kref. */
    bool valid() const { return error_class == KrefErrorClass::None; }

    /**
     * @brief The GetItem request (parent_path, item_name, kind) for this kref.
     *
     * The parent path is "/" plus everything before the LAST '/' of the path, so
     * it holds the project and every nested space. The leaf after it is split at
     * its LAST '.': item names may contain dots, kinds never do. The query is
     * dropped.
     *
     * This is the one split used for every item lookup. It depends on the text
     * only, never on the kernel's verdict.
     *
     * @throws ValidationError if the path has no '/' or its leaf has no '.'. A
     *         leaf without a dot (`kref://p/s.v1/x`) names a space, not an item.
     */
    KrefItemTuple getItemTuple() const;
};

/**
 * @brief Parse a kref once into a KrefParts. Never throws.
 *
 * A string the kernel refuses comes back with KrefParts::error_class set.
 */
KrefParts parseKref(const std::string& uri);

} // namespace api
} // namespace kumiho
