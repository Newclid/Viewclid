# Custom theorems

Lets users extend the solver with domain-specific lemmas without touching
the backend. Each theorem is a list of premise predicates and a list of
conclusion predicates; it's serialized to JGEX and sent with every proof
request — see the [custom theorem contract](../../contracts/custom-theorem-contract.md).

Source: `src/types/theorem.ts`, `src/types/theoremValidation.ts`,
`src/ui/theoremManager.ts`

## Data model

Defined in `src/types/theorem.ts`:

| Type | Shape |
|---|---|
| `TheoremPredicate` | `{ predicateId, args[] }` — `args` are point labels. |
| `CustomTheorem` | Full record: `id`, `name`, `description`, `premises`, `conclusions`, `createdAt`. |
| `PredicateDef` | One predicate's definition: label, icon, expected argument count. |
| `PREDICATE_DEFINITIONS` | Built-in catalogue: `cong`, `para`, `perp`, `midp`, `eqangle`, and others. |

`predicateToJgex(predicate)` serializes a single `TheoremPredicate` to a
JGEX clause string.

## Validation

`src/types/theoremValidation.ts` validates a `CustomTheorem` before it's
saved: every predicate's argument count must match its `PredicateDef`, and
all required fields must be present.

## Theorem manager UI

`src/ui/theoremManager.ts` is a modal for creating and editing theorems:

1. Name and description fields.
2. A visual predicate builder for premises — pick a predicate from a
   dropdown, then fill in point-argument inputs.
3. The same builder for conclusions.
4. Save/delete buttons — save writes to `TheoremStore` (`localStorage`).

To add a new predicate kind, add an entry to `PREDICATE_DEFINITIONS` in
`src/types/theorem.ts` — see
[Adding a custom theorem](../guides/add-a-custom-theorem.md) for the full
workflow.
