import pytest
from newclid_backend.newclid_runner import run_newclid_from_jgex


@pytest.mark.slow
def test_run_newclid_from_valid_jgex_returns_successful_result(
    valid_jgex_problem: str,
) -> None:
    result = run_newclid_from_jgex(valid_jgex_problem)

    assert result.status == "succeeded"
    assert result.message == "Newclid completed successfully."

    assert result.proof_text is not None
    assert "Proof" in result.proof_text

    assert result.proof_sections is not None
    assert result.proof_sections.proof_steps
    sections = result.proof_sections
    assert sections.construction_signatures
    assert len(sections.construction_signatures) == len(sections.assumptions)
    assert len(sections.step_signatures) == len(sections.proof_steps)
    assert len(sections.goal_signatures) == len(sections.proven_goals)
    assert sections.goal_signatures == ["perp a d b c"]

    assert result.run_info is not None
    assert result.run_info["success"] is True

    assert result.sketch_points
    assert all(point.name for point in result.sketch_points)

    assert result.stdout == ""
    assert result.stderr == ""


@pytest.mark.slow
def test_run_newclid_from_invalid_jgex_returns_failed_result() -> None:
    result = run_newclid_from_jgex("this is not valid jgex")

    assert result.status == "failed"
    assert result.message.startswith("Newclid failed:")

    assert result.proof_text is None
    assert result.proof_sections is None
    assert result.run_info is None
    assert result.sketch_points == []

    assert result.stdout == ""
    assert result.stderr
