"""Privacy utilities for PII detection and redaction.

Detection here is **probabilistic and best-effort**, not a guarantee.  The
patterns are regexes tuned for precision on common, well-known shapes; they
will miss novel, obfuscated, or split-across-lines secrets, and they may
occasionally over- or under-match.  Treat :meth:`PIIRedactor.reject_credentials`
as a defence-in-depth screen at the cloud-storage boundary, **never** as a
proof that text is credential-free.  Do not weaken upstream handling of
secrets on the assumption that this gate will catch everything.

Credential families currently covered by ``CREDENTIAL_PATTERNS``:

* AWS access key ids (``AKIA``/``ABIA``/``ACCA``/``ASIA`` + 16).
* HTTP ``Bearer`` tokens.
* OpenAI-style API keys, classic and hyphenated project/vendor forms
  (``sk-``/``pk-``/``rk-``/``ak-`` including ``sk-proj-…`` and ``sk-ant-…``).
* JSON Web Tokens (three base64url segments, ``eyJ``-anchored header+payload).
* Google API keys (``AIza`` + 35).
* Slack tokens (``xoxb``/``xoxa``/``xoxp``/``xoxr``/``xoxs`` + payload).
* PEM private-key headers.
* GitHub tokens (``ghp_``/``gho_``/``ghu_``/``ghs_``/``ghr_`` + 36).
* Database connection URLs that embed an inline password
  (``postgres``/``postgresql``/``mysql``/``mongodb(+srv)``/``redis``/``amqp``).
* Generic ``key = "value"`` secret assignments.

Notably *not* covered (non-exhaustive): passwords in prose, base64-encoded
secrets without a recognisable prefix, Azure/GCP service-account JSON,
provider formats not listed above, and — importantly — any form of Unicode
normalization.  The patterns run on the RAW string, so a single zero-width
space or a fullwidth ``＠`` defeats them (``alice​@example.com`` and
``alice＠example.com`` both pass through untouched).  NFKC-normalizing first
would close those cases but would also rewrite ordinary CJK text, which this
package's primary corpus is full of, so the raw-string behaviour is retained
deliberately.  This module detects accidents, not adversaries.

``PATTERNS`` is otherwise US-ASCII-shaped: it recognises no international phone
format beyond the Korean shapes below, and no non-ASCII email local part.  The
two Korean shapes that matter most for this package's primary locale — mobile
numbers and resident registration numbers — are defined once at module scope
and shared by BOTH directions, so a screened query and the stored index always
agree on the descriptor for the same input.

Query egress
------------
:meth:`PIIRedactor.screen_query` and :func:`screen_query_for_egress` are the
READ-direction screen (#140).  They use a deliberately NARROWER pattern set
than the write path — see :attr:`PIIRedactor.QUERY_PII_PATTERNS` for the
measured reasoning.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class CredentialDetectedError(ValueError):
    """Raised when credential-like patterns are detected in text meant for cloud storage."""
    pass


# Korean national shapes, defined ONCE and shared by both directions.
#
# They live at module scope rather than inside either pattern set because the
# read and write paths must produce the SAME descriptor for the same input.
# When only the query side recognised these, screening a Korean phone number
# turned a query into ``[phone]`` while the index still held the raw digits —
# a match before this screen existed became a miss after it, which is the
# opposite of the intended effect.  Sharing the definition makes that class of
# drift impossible rather than merely absent.
#
# Both require separators, for the same reason the ASCII phone shape does: a
# bare ``01012345678`` is an 11-digit run and indistinguishable from an id.
_KR_RRN = r"(?<![0-9])\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])-[1-8]\d{6}(?![0-9])"
_KR_MOBILE = r"(?<![0-9])01[016789]-\d{3,4}-\d{4}(?![0-9])"


def _luhn_ok(digits: str) -> bool:
    """True when ``digits`` (separators allowed) satisfies the Luhn checksum.

    Every real payment card does.  An arbitrary numeric run has a ~1-in-10
    chance, so gating the bare (separator-less) card shape on this turns a
    measured false positive — a 15/16-digit order or ledger id being rewritten
    to ``[credit_card]`` — into a rare one, without weakening detection of an
    actual pasted card number.
    """
    stripped = [c for c in digits if c.isdigit()]
    if not 13 <= len(stripped) <= 19:
        return False
    total = 0
    for index, char in enumerate(reversed(stripped)):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


class PIIRedactor:
    """Detect and redact common PII patterns."""

    PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        # Korean mobile first: the ASCII shape would otherwise consume part of
        # it and emit a differently-bounded span.
        "phone": (
            rf"(?:{_KR_MOBILE}|"
            r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b)"
        ),
        "ssn": rf"(?:{_KR_RRN}|\b\d{{3}}-\d{{2}}-\d{{4}}\b)",
        "credit_card": r"\b(?:\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}|\d{4}[-\s]?\d{6}[-\s]?\d{5})\b",
        "ip_address": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
    }

    CREDENTIAL_PATTERNS = {
        "aws_access_key": r"\b(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b",
        "bearer_token": r"\bBearer\s+[A-Za-z0-9\-._~+/]+=*\b",
        # Classic ``sk-<entropy>`` AND hyphenated project/vendor forms
        # (``sk-proj-…``, ``sk-ant-…``).  Hyphens/underscores are allowed in
        # the tail so ``sk-proj-`` labels don't defeat the match, but a
        # lookahead still requires a >=20-char *unbroken alphanumeric* run
        # somewhere in the tail.  That run is the entropy signature of a real
        # key; dictionary-word prose like ``sk-learn-based-approach-is-better``
        # (longest alnum run 8) never satisfies it, so hyphenated words don't
        # false-positive.
        "api_key_generic": r"\b(?:sk|pk|rk|ak)-(?=[A-Za-z0-9_-]*[A-Za-z0-9]{20})[A-Za-z0-9_-]{20,}\b",
        # JWT: three base64url segments.  Both header and payload base64url of
        # a JSON object ``{"...`` always begin ``eyJ`` — anchoring both keeps
        # precision high (a bare ``a.b.c`` never matches).
        "jwt": r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
        "google_api_key": r"\bAIza[0-9A-Za-z_-]{35}\b",
        "slack_token": r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b",
        "private_key_header": r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "github_token": r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b",
        # DB connection URLs — flag ONLY when an inline password is present
        # (``scheme://[user]:password@``).  The userinfo is optional so
        # password-only ``redis://:pass@host`` is caught, while password-less
        # URLs (``postgres://host/db``, ``redis://test``) are not.
        "db_url_with_password": r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://[^:\s]*:[^@\s]+@",
        "generic_secret_assignment": r"""(?:api[_-]?key|secret|token|password|passwd|credential)\s*[:=]\s*['"][^'"]{8,}['"]""",
    }

    # Multi-line credential BLOCKS.  Everything in ``CREDENTIAL_PATTERNS`` is a
    # single-line shape, and for PEM keys that shape is the BEGIN *header* only
    # — the key material itself is bare base64, explicitly uncovered (see the
    # module docstring).  Line-oriented screening therefore removes the label
    # and keeps the secret.  These patterns span the whole block so
    # :meth:`redact_credentials` excises the key, not just its header.  A block
    # with no END marker matches to end-of-text (the ``\Z`` branch) — fail
    # closed rather than let an unterminated key body through.
    CREDENTIAL_BLOCK_PATTERNS = {
        "private_key_block": (
            r"-----BEGIN (?:[A-Z][A-Z0-9 ]*)?PRIVATE KEY-----"
            r"[\s\S]*?"
            r"(?:-----END (?:[A-Z][A-Z0-9 ]*)?PRIVATE KEY-----|\Z)"
        ),
    }

    # ------------------------------------------------------------------
    # QUERY-side screening (#140) — a deliberately NARROWER pattern set
    # ------------------------------------------------------------------
    # A search query is not a transcript.  On the WRITE path a false positive
    # costs one descriptor inside a stored summary that still has hundreds of
    # other tokens; on the READ path it costs a SEARCH TERM, and the terms this
    # package's users search on are disproportionately numeric-technical.  The
    # write-path shapes were measured against ordinary developer queries and
    # three of them false-positive hard:
    #
    #   ``phone``       separators are optional, so ANY bare 10-digit run
    #                   matches — every Unix epoch-seconds timestamp, order id
    #                   and invoice number.  ("logs around 1753000000" ->
    #                   "[phone]".)
    #   ``credit_card`` ``[-\s]?`` between groups means four space-separated
    #                   4-digit groups match — i.e. any list of years.
    #                   ("compare 2020 2021 2022 2023" -> "[credit_card]".)
    #   ``ip_address``  indistinguishable from a four-segment version string.
    #                   ("bump to 1.20.3.4", "kernel 5.15.0.91" ->
    #                   "[ip_address]".)
    #
    # So the query set (a) requires a SEPARATOR for phone shapes, (b) drops the
    # whitespace separator from ``credit_card``, and (c) OMITS ``ip_address``
    # entirely.  (c) is the one deliberate privacy concession: an IP in a recall
    # query is by some distance the weakest of these signals — loopback and
    # RFC1918 addresses are not identifying at all — and no tightening
    # distinguishes ``127.0.0.1`` from ``1.20.3.4``.  Trading it for the
    # byte-identity of every version string and IP literal in a code-memory
    # corpus is the better bargain, and it is a stated bargain, not an oversight.
    #
    # Retained with known, accepted false positives:
    #   ``ssn``  ``123-45-6789`` is also a plausible part number.  Kept: a real
    #            SSN is high-value, the shape is rare in prose either way.
    #
    # Descriptors deliberately reuse the WRITE-path vocabulary (``[ssn]``,
    # ``[phone]``, ``[email]``, ``[credit_card]``) so a screened query and the
    # stored index share literal tokens instead of inventing read-only ones.
    #
    # Ordered: ``email`` first (it can contain digits), the tighter national
    # shapes before the looser generic ones.
    QUERY_PII_PATTERNS: Tuple[Tuple[str, str], ...] = (
        ("email", PATTERNS["email"]),
        # Korean shapes, shared with the write path (see the module-level
        # definitions) so both directions emit the same descriptor.
        ("ssn", _KR_RRN),
        ("ssn", PATTERNS["ssn"]),
        # ``credit_card`` minus the whitespace separator (see above).  The
        # separator-less alternative is additionally Luhn-gated — see
        # QUERY_PII_VALIDATORS.
        ("credit_card", r"\b(?:\d{4}-?\d{4}-?\d{4}-?\d{4}|\d{4}-?\d{6}-?\d{5})\b"),
        ("phone", _KR_MOBILE),
        # ``phone`` with a MANDATORY separator between groups.  ``(555) `` is
        # matched via the lookbehind rather than ``\b``, which does not hold
        # before ``(``.
        #
        # The separator class is ``[-.]``, matching the write path EXACTLY.
        # It must not include a space: ``NNN NNN NNNN`` is overwhelmingly
        # ordinary numeric prose in this corpus, not a phone number.  Measured
        # on realistic developer queries, a space in this class rewrote 11 of
        # 16 — "benchmark 512 256 1024 tokens per batch" became
        # "benchmark [phone] tokens per batch", destroying every search term.
        # That is the same false-positive class this set exists to close, so
        # admitting a space here reopened it one line below the comment saying
        # it was fixed.
        ("phone", r"(?<![0-9A-Za-z])(?:\+?1[-.])?\(?\d{3}\)?[-.]\d{3}[-.]\d{4}(?![0-9])"),
    )

    # Descriptor -> extra predicate a candidate span must satisfy to be
    # rewritten.  Only ``credit_card`` needs one: its separator-less form is
    # just "13-19 digits in a row", which is also every long order id, ledger
    # entry and snowflake id.  Luhn separates the two without weakening
    # detection of a genuinely pasted card.
    QUERY_PII_VALIDATORS = {"credit_card": _luhn_ok}

    # Credentials on the query side are the write-path set with ONE precision
    # tightening: ``bearer_token`` as shipped matches the prose "Bearer
    # authentication scheme", because it requires no entropy after the keyword.
    # The lookahead borrowed from ``api_key_generic`` demands a >=20-char
    # unbroken alphanumeric run, which no English word satisfies.  Dropping the
    # pattern outright was the alternative and is strictly worse: a real
    # ``Bearer <opaque>`` in a query would then egress.
    #
    # ``generic_secret_assignment`` is retained as-is.  Its remaining false
    # positive (``token = "abcdefghijk"`` written out in prose) requires the
    # keyword AND an assignment operator AND quotes AND 8+ characters, which is
    # enough structure that treating it as a secret is the right default.
    QUERY_CREDENTIAL_PATTERNS = {
        **CREDENTIAL_PATTERNS,
        "bearer_token": (
            r"\bBearer\s+(?=[A-Za-z0-9\-._~+/]*[A-Za-z0-9]{20})"
            r"[A-Za-z0-9\-._~+/]+=*"
        ),
    }

    # Hard cap on the text handed to the query screen.
    #
    # The ``email`` pattern is quadratic in the length of an unbroken
    # ``[A-Za-z0-9._%+-]`` run with no ``@``: it rescans the run from every
    # word boundary.  Measured on this machine — 2 KB of hyphen-joined slug
    # 3.1 ms, 8 KB 35.6 ms, 32 KB 621 ms, and ``'sk-' + 'a-'*32000`` 4.85 s.
    # ``handle_user_message`` feeds the screen the caller's raw message with no
    # length bound, and the screen is a synchronous call inside an ``async
    # def``, so a pasted 32 KB log line or hyphen-joined UUID list would stall
    # the whole event loop.
    #
    # Truncating is safe (the tail is dropped, never forwarded) and costs
    # nothing real: no retriever scores on 32 KB of query, and every embedding
    # backend this package targets truncates far below this cap anyway.  It is
    # the ONE documented exception to byte-identical passthrough — queries at
    # or under the cap are unaffected, and the cap is ~4x the largest query the
    # package itself constructs (``_background_assess``'s 3-turn buffer, ~900
    # chars).
    QUERY_MAX_CHARS = 4096

    def __init__(self) -> None:
        self.entity_counter: Dict[str, int] = {}

    def redact(self, text: str) -> Tuple[str, Dict[str, List[Dict[str, str]]]]:
        """Redact PII from text and return entities found."""
        redacted = text
        entities: List[Dict[str, str]] = []

        for entity_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text):
                original = match.group(0)
                self.entity_counter[entity_type] = self.entity_counter.get(entity_type, 0) + 1
                placeholder = f"{entity_type.upper()}_{self.entity_counter[entity_type]:03d}"
                redacted = redacted.replace(original, f"[{placeholder}]")
                entities.append(
                    {
                        "type": entity_type,
                        "placeholder": placeholder,
                        "original": "[REDACTED]",
                    }
                )

        return redacted, {"entities": entities}

    def anonymize_summary(self, summary: str) -> str:
        """Anonymize summary by replacing PII with generic descriptors."""
        redacted, entities = self.redact(summary)
        for entity in entities["entities"]:
            placeholder = f"[{entity['placeholder']}]"
            descriptor = f"[{entity['type']}]"
            redacted = redacted.replace(placeholder, descriptor)
        return redacted

    def redact_credentials(self, text: str) -> Tuple[str, int]:
        """Excise credential SPANS in place; return ``(redacted, count)``.

        The span-level counterpart to :meth:`reject_credentials`, which raises
        on the whole text.  A hard reject (or dropping the containing line) is
        the right blast radius for a diff, where one dropped line out of
        hundreds still leaves the model plenty to work with.  It is the wrong
        one for a chat turn, which is typically a SINGLE line: there,
        drop-the-line degenerates into drop-the-whole-turn, and a benign phrase
        that trips a pattern (``"use Bearer token auth"`` matches
        ``bearer_token``) costs the entire message.  Excising only the matched
        span keeps the surrounding prose.

        Blocks are excised before single-line patterns so a PEM body can never
        outlive its header.

        Best-effort, like everything in this module: it removes what the
        patterns match and nothing more.  Use :meth:`reject_credentials` after
        it as a verification pass — never treat this as proof text is clean.
        """
        redacted = text
        count = 0
        patterns = list(self.CREDENTIAL_BLOCK_PATTERNS.values()) + list(
            self.CREDENTIAL_PATTERNS.values()
        )
        for pattern in patterns:
            redacted, found = re.subn(pattern, "[redacted]", redacted)
            count += found
        return redacted, count

    def screen_query(self, query: str) -> Tuple[str, int, bool]:
        """Screen a SEARCH QUERY for egress; return ``(screened, dropped, failed)``.

        The read-direction primitive (#140).  Same three-stage ORDER as the
        write path — credentials excised span-wise on the raw text first, PII
        anonymized in place second, a raising verification pass third — but
        over :attr:`QUERY_PII_PATTERNS` / :attr:`QUERY_CREDENTIAL_PATTERNS`
        rather than the write-path sets.  The narrowing is measured and
        documented at those attributes; it is a deliberate direction-specific
        precision tier, not drift.

        The verification pass uses the SAME credential set as the excision
        pass.  Verifying against a looser set would make every excision fail
        its own check and collapse the query to ``[redacted]``.

        ``failed`` is returned SEPARATELY from ``dropped`` on purpose.  A
        residual credential match after excision is a screening FAILURE, not a
        credential hit, and reporting it as "removed 1 credential span" would
        point an operator at a secret that was never there.

        Text above :attr:`QUERY_MAX_CHARS` is truncated before matching; the
        tail is dropped, never forwarded.
        """
        text = query[: self.QUERY_MAX_CHARS]
        dropped = 0

        cred_patterns = list(self.CREDENTIAL_BLOCK_PATTERNS.values()) + list(
            self.QUERY_CREDENTIAL_PATTERNS.values()
        )

        # [1] credentials first, on the raw text
        for pattern in cred_patterns:
            text, found = re.subn(pattern, "[redacted]", text)
            dropped += found

        # [2] PII in place, into the write path's descriptor vocabulary
        for descriptor, pattern in self.QUERY_PII_PATTERNS:
            validator = self.QUERY_PII_VALIDATORS.get(descriptor)
            if validator is None:
                text = re.sub(pattern, f"[{descriptor}]", text)
                continue

            def _replace(
                match: "re.Match[str]",
                _descriptor: str = descriptor,
                _validator: Any = validator,
            ) -> str:
                span = match.group(0)
                return f"[{_descriptor}]" if _validator(span) else span

            text = re.sub(pattern, _replace, text)

        # [3] verify: a residual match means excision did not hold
        for pattern in cred_patterns:
            if re.search(pattern, text):
                return "[redacted]", dropped, True

        return text, dropped, False

    def reject_credentials(self, text: str) -> None:
        """Reject text containing credential patterns.

        Should be called before storing to the cloud graph to prevent
        secrets from crossing the privacy boundary (spec section 10.4.5).

        Raises:
            CredentialDetectedError: If a credential pattern is detected.
        """
        for cred_type, pattern in self.CREDENTIAL_PATTERNS.items():
            if re.search(pattern, text):
                raise CredentialDetectedError(
                    f"Credential pattern detected ({cred_type}). "
                    "Text containing secrets must not be stored in the "
                    "cloud graph. Remove the credential and retry."
                )


class _QueryScreenFailed:
    """Sentinel type for :data:`QUERY_SCREEN_FAILED`."""

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "<QUERY_SCREEN_FAILED>"


#: Returned by :func:`screen_query_for_egress` when screening did not complete.
#: Callers MUST treat it as "this query must not leave the machine" and fall
#: back to their safe no-op — an empty result set, or the unranked input.
#: Deliberately NOT a redacted string: issuing ``"[redacted]"`` as the query
#: would not be inert, it would be a live search term that lexically matches
#: exactly those stored memories whose own text was credential-redacted, i.e. a
#: screening failure would return a ranked list biased toward the most
#: sensitive rows in the store.
QUERY_SCREEN_FAILED = _QueryScreenFailed()

#: Screening is done with a module-owned redactor, never a caller-injected one.
#: ``UniversalMemoryManager(pii_redactor=...)`` is documented as the SUMMARY
#: anonymizer; routing queries through it would silently widen that contract
#: (an SDK consumer's product-name masking would start rewriting every search
#: string with no opt-out) and would make the byte-identical-passthrough
#: property unprovable, since the pattern set would be the caller's.  That
#: property is the entire reason this ships without a benchmark run, so the
#: pattern set has to be ours.  :meth:`PIIRedactor.screen_query` keeps no
#: cross-call state, so one shared instance is safe.
_QUERY_REDACTOR = PIIRedactor()


def screen_query_for_egress(query: Any) -> Any:
    """Screen a search query before it crosses any machine boundary (#140).

    Returns the screened query, or :data:`QUERY_SCREEN_FAILED` if screening did
    not complete — fail CLOSED.

    THE DECISIVE PROPERTY: a query matching no pattern is returned as the
    IDENTICAL object.  Retrieval is then provably, not arguably, unchanged for
    it.  The exceptions are enumerated and bounded — the shapes in
    :attr:`PIIRedactor.QUERY_PII_PATTERNS` and
    :attr:`PIIRedactor.QUERY_CREDENTIAL_PATTERNS`, plus text over
    :attr:`PIIRedactor.QUERY_MAX_CHARS`.

    Credentials are DROPPED span-wise, never raised on: a raise would abort the
    caller's whole turn on a pasted secret and would do so again on every
    retry, since the message is unchanged.  Only drops are logged, counts only
    — never the matched span, never the pre-screen query.

    Containers (``dict``/``list``/``tuple``) are screened element-wise rather
    than passed through.  The write-direction twin
    (``_redact_value_for_llm``) does the same for multimodal content-block
    lists, and the MCP boundary forwards ``args["query"]`` with no type check,
    so a JSON client can hand this a list.  Passing a non-``str`` through
    unscreened would be a hole in a helper whose whole claim is that it covers
    every caller by construction.  Non-container scalars have no text to
    screen and pass through.
    """
    if isinstance(query, str):
        if not query:
            return query
        try:
            screened, dropped, failed = _QUERY_REDACTOR.screen_query(query)
        except Exception:  # noqa: BLE001 — fail closed, never crash a recall
            logger.exception(
                "recall query screening FAILED (redactor raised) — the query "
                "will not be sent; this is a screening fault, not a credential"
            )
            return QUERY_SCREEN_FAILED
        if failed:
            logger.error(
                "recall query screening FAILED (a credential pattern survived "
                "span excision) — the query will not be sent"
            )
            return QUERY_SCREEN_FAILED
        if dropped:
            logger.warning(
                "recall query screening removed %d credential span(s) before "
                "the query left the machine",
                dropped,
            )
        # Identity, not just equality: a clean query is the caller's own object.
        return query if screened == query else screened

    if isinstance(query, dict):
        out: Dict[Any, Any] = {}
        unchanged = True
        for key, value in query.items():
            screened_value = screen_query_for_egress(value)
            if screened_value is QUERY_SCREEN_FAILED:
                return QUERY_SCREEN_FAILED
            unchanged = unchanged and screened_value is value
            out[key] = screened_value
        return query if unchanged else out

    if isinstance(query, (list, tuple)):
        items: List[Any] = []
        unchanged = True
        for value in query:
            screened_value = screen_query_for_egress(value)
            if screened_value is QUERY_SCREEN_FAILED:
                return QUERY_SCREEN_FAILED
            unchanged = unchanged and screened_value is value
            items.append(screened_value)
        if unchanged:
            return query
        return tuple(items) if isinstance(query, tuple) else items

    return query
