# Shared contracts

Contracts document the data shared across the frontend/backend/engine
boundary. When you change something on one side that affects the other, the
contract page is what both owners should update together — link to it from
both implementations rather than duplicating the description.

| Contract | Covers |
|---|---|
| [JGEX problem input](jgex-problem-input.md) | How a geometry problem is sent to the backend. |
| [Solver job lifecycle](solver-job-lifecycle.md) | Job statuses, the three job endpoints, and polling behavior. |
| [Proof result model](proof-result-model.md) | The shape of a finished job's result: proof text, structured sections, sketch points. |
| [Custom theorem contract](custom-theorem-contract.md) | How user-defined theorems are represented, validated, and converted into Newclid rules. |
