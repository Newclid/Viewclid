# JGEX problem input

This is the contract for how a geometry problem is sent from the frontend to
the backend. It's the input side of a solver job — see
[Solver job lifecycle](solver-job-lifecycle.md) for what happens after
submission.

## Request fields

A job is created with `POST /api/jobs`. The two fields that describe the
problem itself are:

| Field | Type | Meaning |
|---|---|---|
| `input_type` | `"jgex"` | The problem format. Currently only JGEX is supported. |
| `problem_input` | `string` | The full JGEX problem text. |

```json
{
  "input_type": "jgex",
  "problem_input": "a b c = triangle a b c ? cong a b a b"
}
```

!!! note
    The backend strips leading/trailing whitespace from `problem_input`
    before queueing the job, but does **not** parse it. JGEX parsing happens
    inside the worker, in the [runner](../backend/modules/runner.md), via
    `JGEXProblemBuilder`. A malformed problem is reported as a **failed job**,
    not a synchronous `4xx` validation error — see
    [Debugging job failures](../backend/guides/debug-job-failures.md).

## JGEX syntax, briefly

A JGEX string is one or more clauses, separated by `;`:

```text
a b c = triangle a b c ? cong a b a b
```

- **Construction clauses** — `<points> = <construction> <args>`, e.g.
  `a b c = triangle a b c`. These define the geometric objects.
- **Goal clauses** — prefixed with `?`, e.g. `? perp a d b c`. These are the
  predicates the solver must prove. Multiple goals can appear, one per line.

Point labels are arbitrary identifiers — lowercase is used throughout this
page, but case doesn't matter to the solver. Frontend examples elsewhere in
these docs use uppercase (`A`, `B`, …) since that's what the UI displays;
it's the same syntax either way.

```text title="Multiple goals"
a b c = triangle a b c
d = on_tline d b a c, on_tline d c a b
? perp a d b c
? cong a b a c
```

## Where this comes from

The frontend never asks the user to write JGEX by hand for the common case —
it's generated from the canvas:

1. The user constructs the problem visually (points, lines, circles, …).
2. `main.ts` serializes the scene to a JGEX string via the
   [JGEX emission layer](../frontend/modules/jgex-emission.md) when a proof is
   submitted.
3. Goals come from either typed JGEX (advanced users) or the proof-by-points
   panel — see [Adding a goal](../frontend/guides/add-a-goal.md).
4. `BackendClient.submitJob()` sends the resulting string as `problem_input`.

Advanced users can also type JGEX directly, bypassing the visual builder
entirely — the contract is the same either way.

## Custom theorems

`problem_input` only carries the base problem. User-defined theorems travel
as a separate field on the same request — see the
[custom theorem contract](custom-theorem-contract.md).
