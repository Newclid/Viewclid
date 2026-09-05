# Proof result model

This is the canonical shape of the `result` object returned by
`GET /api/jobs/{job_id}/result` once a job reaches a terminal status (see
[Solver job lifecycle](solver-job-lifecycle.md)). The backend produces it in
the [runner](../backend/modules/runner.md) and
[result model](../backend/modules/result-model.md) layers; the frontend
consumes it in the
[backend-integration](../frontend/modules/backend-integration.md) and
[proof UI](../frontend/modules/proof-ui.md) layers.

## Top-level fields

| Field | Type | Meaning |
|---|---|---|
| `status` | `"succeeded" \| "failed" \| "timed_out"` | Runner-level outcome. `timed_out` is reserved and not currently produced — see [solver job lifecycle](solver-job-lifecycle.md#status-state-machine). |
| `message` | `string` | Human-readable summary. |
| `proof_text` | `string \| null` | Full proof text, or `null` if unavailable. |
| `proof_sections` | [`ProofSections`](#proof-sections) `\| null` | Structured proof, or `null` if unavailable. |
| `run_info` | [`RunInfo`](#run-info) `\| null` | Solver statistics, when available. |
| `sketch_points` | [`SketchPoint[]`](#sketch-points) | Final point coordinates for drawing the solved sketch. |
| `stdout` | `string` | Always empty today — the runner calls Newclid in-process, so there's no subprocess output to capture. Reserved for a future runner design. |
| `stderr` | `string` | Captured diagnostics, e.g. a truncated exception traceback. |

```json title="A succeeded result (real output)"
{
  "status": "succeeded",
  "message": "Newclid completed successfully.",
  "proof_text": "...",
  "proof_sections": {
    "points": ["- A(0.28, 0.33)", "- B(1.84, -0.06)"],
    "assumptions": ["[C0] : AB ⟂ CD"],
    "numerical_checks": [],
    "trivial_predicates": [],
    "proven_goals": ["AD ⟂ BC : Proved [0]"],
    "unproven_goals": [],
    "proof_steps": ["000. | AB ⟂ CD [C0] =(r43 Orthocenter theorem)> AD ⟂ BC [0]"],
    "appendix_ar": [],
    "construction_signatures": ["perp a b c d"],
    "step_signatures": ["perp a d b c"],
    "goal_signatures": ["perp a d b c"],
    "step_premise_indices": [[]]
  },
  "run_info": {
    "runtime": 0.011,
    "success": true,
    "steps": 2,
    "success_per_goal": { "AD ⟂ BC succeeded": true },
    "agent_stats": { "agent_type": "follow_deductions", "n_deductions_stored": 1, "n_deductions_followed": 1 }
  },
  "sketch_points": [
    { "name": "a", "x": -0.32, "y": -0.79 },
    { "name": "b", "x": -1.32, "y": 0.29 }
  ],
  "stdout": "",
  "stderr": ""
}
```

## Proof sections

`proof_sections` mirrors Newclid's own structured proof output field for
field, plus one field the backend adds specifically for the frontend:

| Field | Type | Meaning |
|---|---|---|
| `points` | `string[]` | One line per constructed point, with its solved coordinates. |
| `assumptions` | `string[]` | The problem's given assumptions, as proof-reference lines (`[C0]`, `[C1]`, …). |
| `numerical_checks` | `string[]` | Numerical sanity checks the solver ran. |
| `trivial_predicates` | `string[]` | Predicates true by construction, not worth a proof step. |
| `proven_goals` | `string[]` | Each goal that was proved, with its final proof-reference. |
| `unproven_goals` | `string[]` | Goals the solver could not prove. |
| `proof_steps` | `string[]` | The proof itself, one line per step, in Newclid's own step-text format. |
| `appendix_ar` | `string[]` | Algebraic-reasoning deductions, shown as a proof appendix. |
| `construction_signatures` | `string[]` | Canonical signatures of the problem's constructions. |
| `step_signatures` | `string[]` | Canonical signatures of each proof step's conclusion. |
| `goal_signatures` | `string[]` | Canonical signatures of each goal. |
| `step_premise_indices` | `list[list[int]]` | Backend-added. For each proof step, the indices of earlier steps used as premises. |

!!! info "Why `step_premise_indices` exists"
    Newclid's internal proof data references premises by predicate id, which
    is meaningless to the frontend. The backend maps those ids to
    proof-**step** indices so a UI *could* render "this step depends on steps
    0 and 2" without knowing anything about Newclid internals.

!!! warning "Not actually consumed yet"
    The current proof panel (`frontend/src/ui/proofPanel.ts`) doesn't read
    this field — it resolves premise references (`[C0]`, `[N1]`) by
    regex-parsing the free-text `proof_steps` strings instead, which is
    exactly the kind of internals-parsing this field exists to avoid. If
    you're touching proof-step rendering, wiring the UI to
    `step_premise_indices` instead of text-parsing is a good, self-contained
    cleanup — see [Exposing new proof data](../backend/guides/expose-new-proof-data.md)
    for the shape of that kind of change.

## Run info

`run_info` is Newclid's own `RunInfos` model, passed through as-is
(`model_dump()`, no reshaping):

| Field | Type | Meaning |
|---|---|---|
| `runtime` | `float` | Wall-clock solve time, in seconds. |
| `success` | `bool` | Whether every goal was proved. |
| `steps` | `int` | Number of proof steps produced. |
| `success_per_goal` | `dict[str, bool]` | Per-goal pass/fail, keyed by a human-readable goal description. |
| `agent_stats` | `object \| null` | Internals of whichever solving strategy ran (e.g. `follow_deductions`); shape isn't part of this contract and may change with Newclid versions. |

## Sketch points

| Field | Type | Meaning |
|---|---|---|
| `name` | `string` | Point label (non-empty). |
| `x` | `float` | X coordinate in the solver's coordinate space. |
| `y` | `float` | Y coordinate in the solver's coordinate space. |

The frontend uses these to draw the final solved sketch on the canvas — see
[Rendering](../frontend/modules/rendering.md).

## Stability guarantee

Frontend code depends on **this page**, not on Newclid's internal objects.
When Newclid changes its own proof internals, the backend runner is
responsible for adapting to these stable fields — the frontend should never
need to change in response to an internal Newclid refactor.
