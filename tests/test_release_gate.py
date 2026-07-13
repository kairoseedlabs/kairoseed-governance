import pytest

from kairoseed.governance import Decision
from kairoseed.release_gate import ControlOutcome, ReleaseEvidence, evaluate_release


SOURCE = "0123456789abcdef"
LAST_APPROVED = "release-2026.07.1"


def evidence(**overrides: object) -> ReleaseEvidence:
    values: dict[str, object] = {
        "required_checks": ControlOutcome.PASS.value,
        "evidence_complete": ControlOutcome.PASS.value,
        "authority_valid": ControlOutcome.PASS.value,
        "candidate_source": SOURCE,
        "evidence_source": SOURCE,
        "authority_source": SOURCE,
        "last_approved_release": LAST_APPROVED,
    }
    values.update(overrides)
    return ReleaseEvidence(**values)  # type: ignore[arg-type]


def test_complete_contract_returns_pass() -> None:
    result = evaluate_release(evidence())

    assert result.decision is Decision.PASS
    assert result.release_allowed
    assert result.reasons == ("defined verification contract satisfied",)


@pytest.mark.parametrize(
    "outcome",
    [
        ControlOutcome.BLOCK.value,
        ControlOutcome.TIMEOUT.value,
        ControlOutcome.MISSING.value,
        ControlOutcome.UNAUTHORIZED_SKIP.value,
        ControlOutcome.FLAKY.value,
        ControlOutcome.INCONCLUSIVE.value,
        "pass",
        "UNKNOWN",
        "",
        None,
    ],
)
@pytest.mark.parametrize(
    "field",
    ["required_checks", "evidence_complete", "authority_valid"],
)
def test_every_non_pass_control_fails_closed(field: str, outcome: str | None) -> None:
    result = evaluate_release(evidence(**{field: outcome}))

    assert result.decision is Decision.BLOCK
    assert not result.release_allowed
    assert result.preserved_release == LAST_APPROVED


@pytest.mark.parametrize(
    "overrides",
    [
        {"candidate_source": None},
        {"candidate_source": ""},
        {"evidence_source": "other"},
        {"authority_source": "other"},
        {"evidence_source": None},
        {"authority_source": None},
    ],
)
def test_missing_or_mismatched_source_binding_blocks(
    overrides: dict[str, str | None],
) -> None:
    result = evaluate_release(evidence(**overrides))

    assert result.decision is Decision.BLOCK
    assert "SourceBound is BLOCK" in result.reasons
    assert result.preserved_release == LAST_APPROVED


def test_block_preserves_last_known_approved_release() -> None:
    result = evaluate_release(
        evidence(required_checks=ControlOutcome.TIMEOUT.value)
    )

    assert result.decision is Decision.BLOCK
    assert result.preserved_release == LAST_APPROVED


def test_result_serialization_records_decision_and_preserved_release() -> None:
    result = evaluate_release(
        evidence(authority_valid=ControlOutcome.UNAUTHORIZED_SKIP.value)
    )

    assert result.as_dict() == {
        "decision": "BLOCK",
        "reasons": ["AuthorityValid is UNAUTHORIZED_SKIP, not PASS"],
        "preserved_release": LAST_APPROVED,
        "release_allowed": False,
    }
