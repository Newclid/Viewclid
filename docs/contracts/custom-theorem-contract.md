# Custom theorem contract

Custom theorems let a user extend the solver with their own named lemmas,
without touching the backend or Newclid itself. This page is the shape that
both sides agree on; see
[frontend custom theorems](../frontend/modules/custom-theorems.md) and
[backend custom theorems](../backend/modules/custom-theorems.md) for how each
side implements it.

## Shape

A theorem is a name, an optional description, and two lists of predicates.

=== "Wire format (sent to the backend)"

    Part of the `custom_theorems` array on `POST /api/jobs` — see
    [Solver job lifecycle](solver-job-lifecycle.md).

    | Field | Type | Meaning |
    |---|---|---|
    | `name` | `string` | Unique id for this theorem, within this job. |
    | `description` | `string` | Human-readable description. |
    | `premises` | `string[]` | Predicate assumptions, one clause per string. |
    | `conclusions` | `string[]` | Predicate conclusions, one clause per string. |

    ```json
    {
      "name": "my_lemma",
      "description": "A short lemma",
      "premises": ["cong a b a c"],
      "conclusions": ["perp a d b c"]
    }
    ```

=== "Frontend model (`CustomTheorem`)"

    Defined in `src/types/theorem.ts`, persisted to `localStorage` via
    `TheoremStore`.

    | Field | Type | Meaning |
    |---|---|---|
    | `id` | `string` | Local identifier. |
    | `name` | `string` | Same as the wire `name`. |
    | `description` | `string` | Same as the wire `description`. |
    | `premises` | `TheoremPredicate[]` | Structured `{ predicateId, args[] }`, serialized to JGEX strings before sending. |
    | `conclusions` | `TheoremPredicate[]` | Same shape as `premises`. |
    | `createdAt` | `string` | Timestamp, local bookkeeping only. |

    `predicateToJgex()` converts each `TheoremPredicate` into the wire
    format's predicate strings.

## Validation

The backend rejects (as a synchronous `4xx`, before the job is queued):

| Rule | Applies to |
|---|---|
| Non-empty | `name` |
| ≤ 100 characters | `name` |
| No spaces or unsupported punctuation | `name` |
| ≤ 500 characters | `description` |
| Non-empty list | `premises`, `conclusions` |
| Non-empty, single-line strings | each predicate in `premises`/`conclusions` |
| Unique within the job request | `name`, across all custom theorems |

!!! note "Where semantics are checked"
    These are transport-level checks only. Whether the theorem's predicates
    are *semantically* valid, and whether they actually help prove a goal, is
    decided by Newclid/Yuclid once the job runs — a theorem can pass all of
    the checks above and still fail to prove anything useful. See
    [backend custom theorems: failure modes](../backend/modules/custom-theorems.md#failure-modes).

## Conversion to a Newclid rule

Once past validation, the backend converts this wire format into a Newclid
`Rule` — an internal step the frontend never sees. See
[backend custom theorems: conversion](../backend/modules/custom-theorems.md#conversion)
for the mapping.
