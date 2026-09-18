"""Value types for the Kumiho ``Evaluate`` RPC.

:meth:`kumiho.evaluate` judges caller-supplied text fragments against
caller-supplied questions using a server-managed evaluation provider. This
module holds the plain records that call takes and returns; the proto mapping
itself lives in :mod:`kumiho.client`, as it does for every other RPC.

Evaluation is a Kumiho Cloud feature on paid tiers. It is not available in
self-hosted CE, and it never touches the graph: nothing here is a kref, and
nothing here is read from or written to a project.

Example:
    Scoring three fragments on one question::

        import kumiho

        result = kumiho.evaluate(
            query="What did we decide about the release cadence?",
            fragments=[
                {"id": "a", "text": "We ship on the first Tuesday."},
                {"id": "b", "text": "The logo is green."},
                {"id": "c", "text": "Cadence stays monthly for now."},
            ],
            questions=[
                {
                    "id": "relevant",
                    "type": "noul",
                    "instructions": "Does {fragment} answer the query?",
                }
            ],
        )
        for fragment in result.fragments:
            print(fragment.fragment_id, fragment.answers["relevant"].noul)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Union


@dataclass(frozen=True)
class EvaluationFragment:
    """One piece of text to judge.

    Attributes:
        fragment_id: Caller-scoped id, unique within the request, echoed back
            on the matching :class:`FragmentEvaluation`. It is never sent to
            the evaluation provider, so it must not be a kref.
        text: The text to judge. This *is* sent to the provider.
        metadata: Optional non-identifying hints (e.g. ``{"origin": "user"}``)
            merged into the fragment the provider sees. Billed as input
            tokens, so keep it small.
    """

    fragment_id: str
    text: str
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationQuestion:
    """One question asked of every fragment.

    Attributes:
        question_id: Unique within the request. Must not contain ``__``, which
            the server reserves for its own per-fragment question ids.
        type: One of ``"noul"``, ``"choice"`` or ``"score"``.
        instructions: Natural-language instructions, billed on every provider
            request. May contain the literal placeholder ``{fragment}``, which
            the server replaces with its own private label for each fragment.
        criteria: ``"noul"`` — optional, keys ``"true"``/``"false"``.
            ``"choice"`` — required, option name to description.
            ``"score"`` — ignored; use ``levels``.
        levels: ``"score"`` only: two or more ordered level descriptions.
    """

    question_id: str
    type: str
    instructions: str
    criteria: Dict[str, str] = field(default_factory=dict)
    levels: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class NoulAnswer:
    """Answer to a ``"noul"`` question: a float in [0, 1]."""

    noul: float


@dataclass(frozen=True)
class ChoiceAnswer:
    """Answer to a ``"choice"`` question: the chosen option plus its odds."""

    choice: str
    probabilities: Dict[str, float]
    confidence: float


@dataclass(frozen=True)
class ScoreAnswer:
    """Answer to a ``"score"`` question: a level, with the legend it indexes."""

    score: float
    legend: List[str]
    probabilities: List[float]
    confidence: float


#: Any one answer. Which member you get is decided by the question's ``type``.
EvaluationAnswer = Union[NoulAnswer, ChoiceAnswer, ScoreAnswer]


@dataclass(frozen=True)
class FragmentEvaluation:
    """Every answer for one fragment.

    Attributes:
        fragment_id: The caller's own id for this fragment.
        answers: Question id to answer. Empty when ``error`` is set.
        error: Per-fragment failure, e.g. the provider request carrying this
            fragment failed while others succeeded (the ``"partial"`` status).
            Empty when the fragment was answered.
    """

    fragment_id: str
    answers: Dict[str, EvaluationAnswer]
    error: str


@dataclass(frozen=True)
class EvaluationUsage:
    """What the call cost, and where the month stands after it.

    Attributes:
        input_tokens: Provider-reported and billable; 0 on a cache hit.
        output_tokens: Provider-reported.
        provider_requests: Chunks actually sent to the provider.
        cached_fragments: Fragments served from cache, which are not metered.
        month_tokens_used: Monthly input tokens used, after this request.
        month_tokens_limit: Monthly allowance; ``-1`` means unlimited.
    """

    input_tokens: int
    output_tokens: int
    provider_requests: int
    cached_fragments: int
    month_tokens_used: int
    month_tokens_limit: int


@dataclass(frozen=True)
class EvaluationResult:
    """The outcome of one :meth:`kumiho.evaluate` call.

    Attributes:
        status: One of ``"ok"``, ``"partial"``, ``"over_limit"``,
            ``"not_entitled"``, ``"provider_unavailable"`` or
            ``"invalid_request"``. A server that answers with an enum this SDK
            does not know reports ``"unspecified"``.
        fragments: One entry per request fragment, in request order. On a
            non-``"ok"`` status this can be empty.
        usage: Token and request counts for this call.
        model_id: The provider's resolved, versioned model id (e.g.
            ``"judge-1.2.0"``). Empty when the request never reached the
            provider.
        rubric_version: Echoed back from the request.
        message: Human-readable detail for non-``"ok"`` statuses. Never
            contains fragment text or anything from the provider's response.
    """

    status: str
    fragments: List[FragmentEvaluation]
    usage: EvaluationUsage
    model_id: str
    rubric_version: str
    message: str

    def by_id(self) -> Dict[str, "FragmentEvaluation"]:
        """Return :attr:`fragments` keyed by ``fragment_id``.

        Returns:
            Dict[str, FragmentEvaluation]: One entry per fragment.

        Example:
            >>> result.by_id()["a"].answers["relevant"].noul
            0.82
        """
        return {fragment.fragment_id: fragment for fragment in self.fragments}
