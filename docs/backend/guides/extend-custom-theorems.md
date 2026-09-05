# Extending custom theorems

Use this guide when changing the custom theorem payload, or how custom
theorems get converted into Newclid `Rule` objects. A custom theorem is a
client-supplied rule (premises → conclusions) that gets added to the solver
for one job — see the
[custom theorem contract](../../contracts/custom-theorem-contract.md) for
the public shape.

## The pipeline

Before a custom theorem can influence a proof, it crosses two independent
validation layers — and they fail in very different ways, which matters when
something goes wrong.

**Layer 1 — API validation (`schemas.py`).** Pydantic checks shape, before a
job is even queued:

```python
class CustomTheoremRequest(BaseModel):
    name: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_-]*$", ...)
    description: str = Field(default="", ...)
    premises: list[str] = Field(min_length=1, ...)
    conclusions: list[str] = Field(min_length=1, ...)

    @field_validator("premises", "conclusions")
    ...  # strips whitespace, rejects empty or multi-line predicate strings
```

`CreateJobRequest` also has a model validator rejecting duplicate theorem
`name`s **within one request** — there's no persistence or global registry,
so the same name is free to reuse across separate jobs.

**Layer 2 — conversion (`runner_helpers._build_custom_rule_fields`)**, which
runs inside the worker, after the job has already been queued:

```python
rule_kwargs.append({
    "id": name,
    "description": description or name,
    "premises_txt": tuple(theorem["premises"]),
    "conclusions_txt": tuple(theorem["conclusions"]),
})
```

`newclid_runner._build_custom_rules` then does `Rule(**fields)` for each
entry, and the result is passed to
`solver_builder.with_additional_rules(...)`.

!!! warning "`Rule(**fields)` is not type-checked against Pydantic"
    Nothing here confirms `Rule` (from Newclid) actually accepts the
    `premises_txt`/`conclusions_txt` shape you're passing — that's Newclid's
    contract, not something `schemas.py` can enforce. If a new field or a
    changed conversion produces a shape `Rule` rejects, you won't see a
    validation error: the job runs in the worker, raises inside
    `run_newclid_from_jgex`'s `except Exception`, and comes back as an
    ordinary `status: "failed"` with a traceback in `stderr`. See
    [debugging job failures](debug-job-failures.md) — the "`stderr` contains
    a traceback" symptom — to tell this apart from a real solver failure.

## Steps

1. **Update the contract first.** Start with the
   [custom theorem contract](../../contracts/custom-theorem-contract.md) so
   frontend and backend owners agree on the public shape before either side
   changes code.
2. **Add the field to `CustomTheoremRequest` in `schemas.py`.** Keep API
   validation focused on transport-level checks — required fields, lengths,
   duplicates, single-line predicate strings — not on whether Newclid will
   accept the value.
3. **Add it to the dict `_build_custom_rule_fields` returns** in
   `runner_helpers.py`, using the same key `Rule` expects.
4. **Only touch `_build_custom_rules` in `newclid_runner.py`** if the
   conversion into `Rule` objects itself needs to change (e.g. a new keyword
   Newclid's `Rule` doesn't map 1:1 from the request).
5. **Add tests** at all three points: a schema test for validation, a
   helper test asserting the dict shape `_build_custom_rule_fields` produces,
   and one end-to-end test that actually runs a job with the new field so a
   `Rule`-rejects-this-shape bug is caught before it reaches production.

## Non-goals

See [custom theorems: ownership boundary](../modules/custom-theorems.md#ownership-boundary)
for what the backend is and isn't responsible for validating.

## Failure modes

See [custom theorems: failure modes](../modules/custom-theorems.md#failure-modes)
for how to separate an API validation failure from a runner conversion
failure from "Newclid just couldn't use this rule."
