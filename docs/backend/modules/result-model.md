# Result model

The runner returns Pydantic models defined in `runner_models.py`. These are
the internal source for the JSON returned by the job result endpoint — the
public shape they produce is documented in the
[proof result model contract](../../contracts/proof-result-model.md); this
page covers the internal Python side.

Source: `runner_models.py`

## `NewclidRunResult`

The top-level model. Field meanings are in the
[contract](../../contracts/proof-result-model.md#top-level-fields); this is
the same shape, as Python types rather than JSON.

## `NewclidProofSections`

Twelve fields total — see the
[contract's full field table](../../contracts/proof-result-model.md#proof-sections)
for all of them. Eleven mirror Newclid's own structured proof output
directly; one, `step_premise_indices: list[list[int]]`, is added by the
backend. Each entry corresponds to one proof step and lists the earlier step
indices used as its premises, built from Newclid's predicate ids so a UI
*could* render proof dependencies without knowing anything about Newclid
internals — see the contract page for the caveat that this field isn't
actually wired up on the frontend yet.

## `SketchPoint`

```python
name: str
x: float
y: float
```

The model validates that `name` is non-empty. Coordinates are converted to
plain floats before leaving the runner.

## Stability rule

Frontend code should depend on this result model, not on Newclid's internal
objects. When Newclid changes its own proof internals, this layer — not the
frontend — is responsible for adapting to the stable fields in the
[contract](../../contracts/proof-result-model.md).
