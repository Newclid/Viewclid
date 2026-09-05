# Custom theorems

Custom theorems let the frontend submit additional rule schemas with a
solver job. The backend validates the payload, converts it into Newclid rule
fields, and passes the resulting rules to the solver builder. The public
shape is the [custom theorem contract](../../contracts/custom-theorem-contract.md);
this page covers the backend's part of it.

Source: `schemas.py`, `runner_helpers.py`, `newclid_runner.py`

## Request model

`CustomTheoremRequest` in `schemas.py` — see the
[contract](../../contracts/custom-theorem-contract.md#shape) for the field
table.

## Validation

Backend validation rejects:

- empty names
- names longer than 100 characters
- names with spaces or unsupported punctuation
- empty premise or conclusion lists
- empty predicate lines
- multi-line predicate strings
- duplicate theorem names within one job request

These are API-level checks only. Predicate semantics are still handled by
Newclid when the runner constructs `Rule` objects.

## Conversion

`runner_helpers.py` converts the public request into Newclid rule keyword
arguments:

```text
name         -> id
description  -> description, or name if empty
premises     -> premises_txt
conclusions  -> conclusions_txt
```

`newclid_runner.py` then constructs `Rule` objects and passes them to
`GeometricSolverBuilder.with_additional_rules`.

## Ownership boundary

The backend validates the *shape* of a request and converts it into what
Newclid expects. It doesn't duplicate Newclid's rule parser — predicate
semantics and generic rule matching belong to Newclid/Yuclid.

## Failure modes

When debugging a custom theorem, separate these cases:

| Case | Where it's caught |
|---|---|
| API validation failed before enqueueing | Synchronous `4xx`, before the job exists. |
| Runner conversion failed constructing `Rule` objects | Job result, `status: "failed"`. |
| Newclid accepted the rule, but it didn't help prove the goal | Job result, `status: "failed"`, no exception. |
| Yuclid's generic matcher accepted the rule but found no useful candidates | Job result, `status: "failed"`, no exception. |

Only the first case should ever return a synchronous HTTP validation error —
the rest are job results, not request failures.
