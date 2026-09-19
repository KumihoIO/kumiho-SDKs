"""Unit tests for the Evaluate RPC wrapper.

Evaluate is the one RPC whose whole job is translation: strings in the Python
API become wire enums, two input shapes (dataclass and mapping) become one
message, and three answer kinds come back through a oneof. So these tests are
mostly about the mapping in both directions, plus the handful of client-side
checks that make a bad call obvious before it costs provider tokens.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import grpc

import kumiho
from kumiho.proto import kumiho_pb2

import mock_helpers


@pytest.mark.parametrize("code", [
    grpc.StatusCode.DEADLINE_EXCEEDED,
    grpc.StatusCode.UNAVAILABLE,
    grpc.StatusCode.INTERNAL,
])
def test_review_regression_paid_evaluate_is_not_retried(monkeypatch, code):
    from kumiho.client import _ClientCallDetails, _TransientRetryInterceptor

    interceptor = _TransientRetryInterceptor()
    monkeypatch.setattr("kumiho.client.time.sleep", lambda _: None)
    response = MagicMock()
    response.code.return_value = code
    continuation = MagicMock(return_value=response)
    details = _ClientCallDetails(
        method="/kumiho.KumihoService/Evaluate", timeout=1.0, metadata=(),
        credentials=None, wait_for_ready=False, compression=None,
    )
    assert interceptor.intercept_unary_unary(continuation, details, object()) is response
    assert continuation.call_count == 1, "Evaluate has no provider idempotency guarantee"


def test_review_regression_other_rpcs_keep_transient_retries(monkeypatch):
    from kumiho.client import _ClientCallDetails, _TransientRetryInterceptor

    interceptor = _TransientRetryInterceptor()
    monkeypatch.setattr("kumiho.client.time.sleep", lambda _: None)
    response = MagicMock()
    response.code.return_value = grpc.StatusCode.UNAVAILABLE
    continuation = MagicMock(return_value=response)
    details = _ClientCallDetails(
        method="/kumiho.KumihoService/GetProjects", timeout=1.0, metadata=(),
        credentials=None, wait_for_ready=False, compression=None,
    )
    interceptor.intercept_unary_unary(continuation, details, object())
    assert continuation.call_count == interceptor.max_attempts


def test_review_regression_zero_timeout_keeps_server_default_budget(mock_client):
    _, stub = mock_client
    _ok(stub)
    kumiho.evaluate(
        query="q",
        fragments=[{"id": "a", "text": "text"}],
        questions=[{"id": "q", "type": "noul", "instructions": "Relevant?"}],
        timeout_ms=0,
    )
    assert stub.Evaluate.call_args.args[0].timeout_ms == 0
    assert "timeout" not in stub.Evaluate.call_args.kwargs


@pytest.fixture
def mock_client(monkeypatch):
    original_client = kumiho._default_client
    stub = MagicMock()
    monkeypatch.setattr(
        "kumiho.client.kumiho_pb2_grpc.KumihoServiceStub",
        lambda channel: stub,
    )
    client = kumiho.connect(endpoint="localhost:50051", token="mock-token")
    kumiho.configure_default_client(client)
    try:
        yield client, stub
    finally:
        kumiho._default_client = original_client


def _ok(stub, fragments=None, **kwargs):
    """Point the stub at an OK response and return it."""
    response = mock_helpers.mock_evaluate_response(fragments=fragments, **kwargs)
    stub.Evaluate.return_value = response
    return response


# --- Request mapping -------------------------------------------------------


def test_mapping_inputs_become_one_request(mock_client) -> None:
    client, stub = mock_client
    _ok(stub)

    kumiho.evaluate(
        query="what did we decide about cadence?",
        fragments=[
            {"id": "m1", "text": "We ship on the first Tuesday."},
            {"id": "m2", "text": "The logo is green.", "metadata": {"origin": "user"}},
        ],
        questions=[
            {
                "id": "relevant",
                "type": "noul",
                "instructions": "Does {fragment} answer the query?",
                "criteria": {"true": "it does", "false": "it does not"},
            }
        ],
        extra_context="today is 2026-09-18",
        rubric_version="rubric-7",
    )

    request = stub.Evaluate.call_args.args[0]
    assert request.task.query == "what did we decide about cadence?"
    assert request.task.extra_context == "today is 2026-09-18"
    assert request.rubric_version == "rubric-7"
    assert [f.fragment_id for f in request.fragments] == ["m1", "m2"]
    assert request.fragments[0].text == "We ship on the first Tuesday."
    assert dict(request.fragments[0].metadata) == {}
    assert dict(request.fragments[1].metadata) == {"origin": "user"}
    assert [q.question_id for q in request.questions] == ["relevant"]
    assert request.questions[0].type == kumiho_pb2.QUESTION_TYPE_NOUL
    assert dict(request.questions[0].criteria) == {
        "true": "it does",
        "false": "it does not",
    }


def test_dataclass_inputs_produce_the_same_request(mock_client) -> None:
    """The two input shapes are two spellings of one message, not two paths."""
    client, stub = mock_client
    _ok(stub)

    kumiho.evaluate(
        query="q",
        fragments=[
            kumiho.EvaluationFragment(fragment_id="m1", text="first"),
            kumiho.EvaluationFragment(
                fragment_id="m2", text="second", metadata={"origin": "user"}
            ),
        ],
        questions=[
            kumiho.EvaluationQuestion(
                question_id="tier",
                type="score",
                instructions="Rate {fragment}.",
                levels=["poor", "fine", "good"],
            )
        ],
    )
    from_dataclasses = stub.Evaluate.call_args.args[0]

    kumiho.evaluate(
        query="q",
        fragments=[
            {"id": "m1", "text": "first"},
            {"id": "m2", "text": "second", "metadata": {"origin": "user"}},
        ],
        questions=[
            {
                "id": "tier",
                "type": "score",
                "instructions": "Rate {fragment}.",
                "levels": ["poor", "fine", "good"],
            }
        ],
    )
    from_mappings = stub.Evaluate.call_args.args[0]

    assert from_dataclasses == from_mappings
    assert list(from_dataclasses.questions[0].criteria_levels) == [
        "poor",
        "fine",
        "good",
    ]


@pytest.mark.parametrize(
    "mode,expected",
    [
        ("", kumiho_pb2.EVALUATION_MODE_UNSPECIFIED),
        ("batched", kumiho_pb2.EVALUATION_MODE_BATCHED),
        ("per_fragment", kumiho_pb2.EVALUATION_MODE_PER_FRAGMENT),
    ],
)
def test_mode_strings_map_to_the_wire_enum(mock_client, mode, expected) -> None:
    client, stub = mock_client
    _ok(stub)

    kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[{"id": "q1", "type": "noul", "instructions": "i"}],
        mode=mode,
    )

    assert stub.Evaluate.call_args.args[0].mode == expected


@pytest.mark.parametrize(
    "question_type,expected",
    [
        ("noul", kumiho_pb2.QUESTION_TYPE_NOUL),
        ("choice", kumiho_pb2.QUESTION_TYPE_CHOICE),
        ("score", kumiho_pb2.QUESTION_TYPE_SCORE),
    ],
)
def test_question_types_map_to_the_wire_enum(
    mock_client, question_type, expected
) -> None:
    client, stub = mock_client
    _ok(stub)

    kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[{"id": "q1", "type": question_type, "instructions": "i"}],
    )

    assert stub.Evaluate.call_args.args[0].questions[0].type == expected


@pytest.mark.parametrize("allow_cache", [True, False])
def test_allow_cache_is_always_set_explicitly(mock_client, allow_cache) -> None:
    """The field has explicit presence, so send it either way rather than
    leaving the server to infer the default from its absence."""
    client, stub = mock_client
    _ok(stub)

    kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[{"id": "q1", "type": "noul", "instructions": "i"}],
        allow_cache=allow_cache,
    )

    request = stub.Evaluate.call_args.args[0]
    assert request.HasField("allow_cache")
    assert request.allow_cache is allow_cache


def test_fragment_placeholder_is_passed_through_untouched(mock_client) -> None:
    """`{fragment}` is the server's to render — the SDK must not format it."""
    client, stub = mock_client
    _ok(stub)
    instructions = "Does memory {fragment} address the subject of the query?"
    criteria = {"true": "{fragment} is on topic", "false": "{fragment} is not"}

    kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[
            {
                "id": "q1",
                "type": "noul",
                "instructions": instructions,
                "criteria": criteria,
            }
        ],
    )

    question = stub.Evaluate.call_args.args[0].questions[0]
    assert question.instructions == instructions
    assert dict(question.criteria) == criteria


# --- Deadline --------------------------------------------------------------


def test_timeout_ms_sets_the_hint_and_the_deadline(mock_client) -> None:
    client, stub = mock_client
    _ok(stub)

    kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[{"id": "q1", "type": "noul", "instructions": "i"}],
        timeout_ms=8000,
    )

    assert stub.Evaluate.call_args.args[0].timeout_ms == 8000
    # 8s hint plus the margin that lets the server's own answer win the race.
    assert stub.Evaluate.call_args.kwargs["timeout"] == pytest.approx(10.0)


def test_no_timeout_leaves_the_deadline_to_the_interceptor(mock_client) -> None:
    client, stub = mock_client
    _ok(stub)

    kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[{"id": "q1", "type": "noul", "instructions": "i"}],
    )

    assert stub.Evaluate.call_args.args[0].timeout_ms == 0
    assert "timeout" not in stub.Evaluate.call_args.kwargs


# --- Response mapping ------------------------------------------------------


def test_noul_answers_are_mapped(mock_client) -> None:
    client, stub = mock_client
    _ok(
        stub,
        fragments=[
            mock_helpers.mock_fragment_evaluation(
                "m1", [mock_helpers.mock_noul_answer("relevant", 0.82)]
            )
        ],
        model_id="judge-1.2.0",
        rubric_version="rubric-7",
    )

    result = kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[{"id": "relevant", "type": "noul", "instructions": "i"}],
    )

    assert result.status == "ok"
    assert result.model_id == "judge-1.2.0"
    assert result.rubric_version == "rubric-7"
    answer = result.fragments[0].answers["relevant"]
    assert isinstance(answer, kumiho.NoulAnswer)
    assert answer.noul == pytest.approx(0.82, abs=1e-6)


def test_choice_answers_are_mapped(mock_client) -> None:
    client, stub = mock_client
    _ok(
        stub,
        fragments=[
            mock_helpers.mock_fragment_evaluation(
                "m1",
                [
                    mock_helpers.mock_choice_answer(
                        "kind",
                        "decision",
                        probabilities={"decision": 0.7, "trivia": 0.3},
                        confidence=0.64,
                    )
                ],
            )
        ],
    )

    result = kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[
            {
                "id": "kind",
                "type": "choice",
                "instructions": "i",
                "criteria": {"decision": "", "trivia": ""},
            }
        ],
    )

    answer = result.fragments[0].answers["kind"]
    assert isinstance(answer, kumiho.ChoiceAnswer)
    assert answer.choice == "decision"
    assert answer.confidence == pytest.approx(0.64, abs=1e-6)
    assert sorted(answer.probabilities) == ["decision", "trivia"]
    assert answer.probabilities["decision"] == pytest.approx(0.7, abs=1e-6)


def test_score_answers_are_mapped(mock_client) -> None:
    client, stub = mock_client
    _ok(
        stub,
        fragments=[
            mock_helpers.mock_fragment_evaluation(
                "m1",
                [
                    mock_helpers.mock_score_answer(
                        "tier",
                        2.0,
                        legend=["poor", "fine", "good"],
                        probabilities=[0.1, 0.2, 0.7],
                        confidence=0.9,
                    )
                ],
            )
        ],
    )

    result = kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[
            {
                "id": "tier",
                "type": "score",
                "instructions": "i",
                "levels": ["poor", "fine", "good"],
            }
        ],
    )

    answer = result.fragments[0].answers["tier"]
    assert isinstance(answer, kumiho.ScoreAnswer)
    assert answer.score == pytest.approx(2.0)
    assert answer.legend == ["poor", "fine", "good"]
    assert answer.probabilities == pytest.approx([0.1, 0.2, 0.7], abs=1e-6)
    assert answer.confidence == pytest.approx(0.9, abs=1e-6)


def test_usage_and_by_id_are_mapped(mock_client) -> None:
    client, stub = mock_client
    _ok(
        stub,
        fragments=[
            mock_helpers.mock_fragment_evaluation(
                "m1", [mock_helpers.mock_noul_answer("relevant", 0.5)]
            ),
            mock_helpers.mock_fragment_evaluation(
                "m2", [mock_helpers.mock_noul_answer("relevant", 0.25)]
            ),
        ],
        usage=mock_helpers.mock_evaluation_usage(
            input_tokens=1200,
            output_tokens=48,
            provider_requests=1,
            cached_fragments=1,
            month_tokens_used=98000,
            month_tokens_limit=-1,
        ),
    )

    result = kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "a"}, {"id": "m2", "text": "b"}],
        questions=[{"id": "relevant", "type": "noul", "instructions": "i"}],
    )

    assert result.usage == kumiho.EvaluationUsage(
        input_tokens=1200,
        output_tokens=48,
        provider_requests=1,
        cached_fragments=1,
        month_tokens_used=98000,
        month_tokens_limit=-1,
    )
    assert [f.fragment_id for f in result.fragments] == ["m1", "m2"]
    assert sorted(result.by_id()) == ["m1", "m2"]
    assert result.by_id()["m2"].answers["relevant"].noul == pytest.approx(
        0.25, abs=1e-6
    )


#: Every EvaluationStatus the proto defines, and the string it surfaces as.
STATUS_CASES = [
    (kumiho_pb2.EVALUATION_STATUS_UNSPECIFIED, "unspecified"),
    (kumiho_pb2.EVALUATION_STATUS_OK, "ok"),
    (kumiho_pb2.EVALUATION_STATUS_PARTIAL, "partial"),
    (kumiho_pb2.EVALUATION_STATUS_OVER_LIMIT, "over_limit"),
    (kumiho_pb2.EVALUATION_STATUS_NOT_ENTITLED, "not_entitled"),
    (kumiho_pb2.EVALUATION_STATUS_PROVIDER_UNAVAILABLE, "provider_unavailable"),
    (kumiho_pb2.EVALUATION_STATUS_INVALID_REQUEST, "invalid_request"),
]


@pytest.mark.parametrize("enum_value,expected", STATUS_CASES)
def test_every_status_enum_value_has_a_name(mock_client, enum_value, expected) -> None:
    client, stub = mock_client
    _ok(stub, status=enum_value, message="detail")

    result = kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[{"id": "q1", "type": "noul", "instructions": "i"}],
    )

    assert result.status == expected
    assert result.message == "detail"


def test_status_parametrisation_covers_the_whole_enum() -> None:
    """If the proto gains a status, the table above has to gain a row."""
    covered = {enum_value for enum_value, _ in STATUS_CASES}
    assert covered == {v.number for v in kumiho_pb2.EvaluationStatus.DESCRIPTOR.values}


def test_partial_carries_a_per_fragment_error(mock_client) -> None:
    client, stub = mock_client
    _ok(
        stub,
        status=kumiho_pb2.EVALUATION_STATUS_PARTIAL,
        fragments=[
            mock_helpers.mock_fragment_evaluation(
                "m1", [mock_helpers.mock_noul_answer("relevant", 0.9)]
            ),
            mock_helpers.mock_fragment_evaluation(
                "m2", error="provider request failed"
            ),
        ],
        message="1 of 2 fragments could not be judged",
    )

    result = kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "a"}, {"id": "m2", "text": "b"}],
        questions=[{"id": "relevant", "type": "noul", "instructions": "i"}],
    )

    assert result.status == "partial"
    assert result.message == "1 of 2 fragments could not be judged"
    answered, failed = result.fragments
    assert answered.error == ""
    assert answered.answers["relevant"].noul == pytest.approx(0.9, abs=1e-6)
    assert failed.error == "provider request failed"
    assert failed.answers == {}


def test_an_answer_with_no_value_set_is_dropped(mock_client) -> None:
    """A oneof this SDK cannot read is left out rather than guessed at."""
    client, stub = mock_client
    _ok(
        stub,
        fragments=[
            mock_helpers.mock_fragment_evaluation(
                "m1",
                [
                    kumiho_pb2.EvaluationAnswer(question_id="unset"),
                    mock_helpers.mock_noul_answer("relevant", 0.4),
                ],
            )
        ],
    )

    result = kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[{"id": "relevant", "type": "noul", "instructions": "i"}],
    )

    assert list(result.fragments[0].answers) == ["relevant"]


# --- Client-side validation ------------------------------------------------


@pytest.mark.parametrize("query", ["", "   "])
def test_empty_query_is_rejected(mock_client, query) -> None:
    client, stub = mock_client

    with pytest.raises(ValueError, match="non-empty query"):
        kumiho.evaluate(
            query=query,
            fragments=[{"id": "m1", "text": "t"}],
            questions=[{"id": "q1", "type": "noul", "instructions": "i"}],
        )
    stub.Evaluate.assert_not_called()


def test_empty_fragment_id_is_rejected(mock_client) -> None:
    client, stub = mock_client

    with pytest.raises(ValueError, match=r"fragments\[1\] has an empty fragment id"):
        kumiho.evaluate(
            query="q",
            fragments=[{"id": "m1", "text": "a"}, {"id": "", "text": "b"}],
            questions=[{"id": "q1", "type": "noul", "instructions": "i"}],
        )
    stub.Evaluate.assert_not_called()


def test_repeated_fragment_id_is_rejected(mock_client) -> None:
    client, stub = mock_client

    with pytest.raises(ValueError, match=r"fragments\[2\] repeats fragment id 'm1'"):
        kumiho.evaluate(
            query="q",
            fragments=[
                {"id": "m1", "text": "a"},
                {"id": "m2", "text": "b"},
                {"id": "m1", "text": "c"},
            ],
            questions=[{"id": "q1", "type": "noul", "instructions": "i"}],
        )
    stub.Evaluate.assert_not_called()


def test_unknown_question_type_is_rejected(mock_client) -> None:
    client, stub = mock_client

    with pytest.raises(ValueError, match=r"questions\[0\] has unknown type 'rank'"):
        kumiho.evaluate(
            query="q",
            fragments=[{"id": "m1", "text": "t"}],
            questions=[{"id": "q1", "type": "rank", "instructions": "i"}],
        )
    stub.Evaluate.assert_not_called()


def test_double_underscore_in_a_question_id_is_rejected(mock_client) -> None:
    """The server builds its per-fragment question ids with `__`."""
    client, stub = mock_client

    with pytest.raises(ValueError, match="reserves"):
        kumiho.evaluate(
            query="q",
            fragments=[{"id": "m1", "text": "t"}],
            questions=[{"id": "is__relevant", "type": "noul", "instructions": "i"}],
        )
    stub.Evaluate.assert_not_called()


def test_unknown_mode_is_rejected(mock_client) -> None:
    """A typo here cannot reach the server as an error — it would silently
    become the zero value and change which provider path runs."""
    client, stub = mock_client

    with pytest.raises(ValueError, match="Unknown evaluation mode 'batch'"):
        kumiho.evaluate(
            query="q",
            fragments=[{"id": "m1", "text": "t"}],
            questions=[{"id": "q1", "type": "noul", "instructions": "i"}],
            mode="batch",
        )
    stub.Evaluate.assert_not_called()


# --- Plumbing --------------------------------------------------------------


def test_the_client_method_and_the_module_wrapper_agree(mock_client) -> None:
    client, stub = mock_client
    _ok(stub)

    client.evaluate(
        "q",
        [{"id": "m1", "text": "t"}],
        [{"id": "q1", "type": "noul", "instructions": "i"}],
        mode="batched",
        rubric_version="v1",
        allow_cache=False,
    )
    direct = stub.Evaluate.call_args.args[0]

    kumiho.evaluate(
        query="q",
        fragments=[{"id": "m1", "text": "t"}],
        questions=[{"id": "q1", "type": "noul", "instructions": "i"}],
        mode="batched",
        rubric_version="v1",
        allow_cache=False,
    )
    via_wrapper = stub.Evaluate.call_args.args[0]

    assert direct == via_wrapper
