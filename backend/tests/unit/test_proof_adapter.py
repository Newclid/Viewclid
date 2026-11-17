from types import SimpleNamespace

import pytest
from newclid.justifications.justification import DirectConsequence
from newclid.numerical.geometries import PointNum
from newclid.predicate_types import PredicateArgument
from newclid.predicates.collinearity import Coll
from newclid.proof_data import PredicateInProof, ProofData, ProofId, ProofStep
from newclid.proof_writing import write_proof_sections
from newclid.symbols.points_registry import Point
from newclid_backend import proof_adapter


def _proof_step(predicate_id: str, applied_on: list[str]) -> SimpleNamespace:
    return SimpleNamespace(
        proven_predicate=SimpleNamespace(id=predicate_id),
        applied_on_predicates=applied_on,
    )


def _proof_data(*steps: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(proof_steps=list(steps))


def test_maps_known_premise_ids_to_step_indices() -> None:
    proof_data = _proof_data(
        _proof_step("step-a", []),
        _proof_step("step-b", ["step-a"]),
    )
    assert proof_adapter._build_step_premise_indices(proof_data) == [[], [0]]


def test_ignores_unknown_premise_ids() -> None:
    proof_data = _proof_data(
        _proof_step("step-a", []),
        _proof_step("step-b", ["construction-assumption", "unknown"]),
    )
    assert proof_adapter._build_step_premise_indices(proof_data) == [[], []]


def test_deduplicates_repeated_premise_ids() -> None:
    proof_data = _proof_data(
        _proof_step("step-a", []),
        _proof_step("step-b", ["step-a", "step-a", "step-a"]),
    )
    assert proof_adapter._build_step_premise_indices(proof_data) == [[], [0]]


def test_sorts_premise_indices_ascending() -> None:
    proof_data = _proof_data(
        _proof_step("step-a", []),
        _proof_step("step-b", []),
        _proof_step("step-c", []),
        _proof_step("step-d", ["step-c", "step-a", "step-b"]),
    )
    assert proof_adapter._build_step_premise_indices(proof_data) == [
        [],
        [],
        [],
        [0, 1, 2],
    ]


def test_handles_mixed_known_and_unknown_references() -> None:
    proof_data = _proof_data(
        _proof_step("step-a", []),
        _proof_step("step-b", []),
        _proof_step("step-c", ["unknown", "step-b", "step-a", "step-b"]),
    )
    assert proof_adapter._build_step_premise_indices(proof_data) == [[], [], [0, 1]]


@pytest.fixture
def proof_data() -> ProofData:
    a, b, c, d = [
        Point(name=PredicateArgument(name), num=PointNum(x=float(i), y=0.0))
        for i, name in enumerate("abcd")
    ]
    assumption = PredicateInProof(id=ProofId("C0"), predicate=Coll(points=(a, b, c, d)))
    first = PredicateInProof(id=ProofId("0"), predicate=Coll(points=(a, b, c)))
    second = PredicateInProof(id=ProofId("1"), predicate=Coll(points=(a, b, d)))
    return ProofData(
        points=[a, b, c, d],
        construction_assumptions=[assumption],
        numerical_checks=[],
        trivial_predicates=[],
        proven_goals=[second, first],
        unproven_goals=[],
        proof_steps=[
            ProofStep(
                proven_predicate=first,
                justification=DirectConsequence(
                    predicate=first.predicate, premises=(assumption.predicate,)
                ),
                applied_on_predicates=(assumption.id,),
            ),
            ProofStep(
                proven_predicate=second,
                justification=DirectConsequence(
                    predicate=second.predicate,
                    premises=(assumption.predicate, first.predicate),
                ),
                applied_on_predicates=(assumption.id, first.id),
            ),
        ],
    )


def test_builds_signatures_in_proof_order(proof_data: ProofData) -> None:
    sections = proof_adapter.build_proof_sections(proof_data)

    assert sections.construction_signatures == ["coll a b c d"]
    assert sections.step_signatures == ["coll a b c", "coll a b d"]
    assert sections.goal_signatures == ["coll a b d", "coll a b c"]
    assert sections.step_premise_indices == [[], [0]]


def test_preserves_formatted_sections_and_proof_data(proof_data: ProofData) -> None:
    original_data = proof_data.model_dump()
    formatted = write_proof_sections(proof_data).model_dump()
    sections = proof_adapter.build_proof_sections(proof_data).model_dump()

    for name in (
        "points",
        "assumptions",
        "numerical_checks",
        "trivial_predicates",
        "proven_goals",
        "unproven_goals",
        "proof_steps",
        "appendix_ar",
    ):
        assert sections[name] == formatted[name]
    assert proof_data.model_dump() == original_data


def test_handles_empty_proof() -> None:
    data = ProofData(
        points=[],
        construction_assumptions=[],
        numerical_checks=[],
        trivial_predicates=[],
        proven_goals=[],
        unproven_goals=[],
        proof_steps=[],
    )
    sections = proof_adapter.build_proof_sections(data)

    assert sections.construction_signatures == []
    assert sections.step_signatures == []
    assert sections.goal_signatures == []
    assert sections.step_premise_indices == []
