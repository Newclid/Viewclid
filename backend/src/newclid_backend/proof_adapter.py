from newclid.proof_data import ProofData
from newclid.proof_writing import write_proof_sections

from newclid_backend.runner_models import NewclidProofSections


def build_proof_sections(proof_data: ProofData) -> NewclidProofSections:
    sections = write_proof_sections(proof_data).model_dump()
    sections.update(
        construction_signatures=[
            repr(item.predicate) for item in proof_data.construction_assumptions
        ],
        step_signatures=[
            repr(step.proven_predicate.predicate) for step in proof_data.proof_steps
        ],
        goal_signatures=[repr(goal.predicate) for goal in proof_data.proven_goals],
        step_premise_indices=_build_step_premise_indices(proof_data),
    )
    return NewclidProofSections.model_validate(sections)


def _build_step_premise_indices(proof_data: ProofData) -> list[list[int]]:
    id_to_step_idx = {
        step.proven_predicate.id: i for i, step in enumerate(proof_data.proof_steps)
    }
    return [
        sorted(
            {
                id_to_step_idx[pid]
                for pid in step.applied_on_predicates
                if pid in id_to_step_idx
            }
        )
        for step in proof_data.proof_steps
    ]
