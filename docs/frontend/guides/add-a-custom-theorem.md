# Adding a predicate to the theorem manager

Custom theorems let a user extend the solver with their own lemmas, without
touching the backend — each theorem is a named set of premise and conclusion
predicates, picked from a dropdown in the theorem manager UI. See
[Custom theorems](../modules/custom-theorems.md) for how the frontend and
backend divide responsibility for it, and the
[user guide](../../user-guide/custom-theorems.md) if you want to see the
feature from the end-user side first.

Use this guide when the predicate a user needs isn't in the theorem
manager's dropdown yet.

!!! warning "This catalogue is not shared with the proof-by-points panel"
    The theorem manager and the proof-by-points panel (used for
    [goals](add-a-goal.md)) look similar but read from two **separate**
    catalogues with two different data shapes. Adding a predicate here does
    **not** make it available as a goal, and vice versa — see
    [Adding a goal](add-a-goal.md) if that's what you actually need.

## The catalogue

Every predicate the theorem manager can use is one `PredicateDef` entry in
`PREDICATE_DEFINITIONS` (`src/types/theorem.ts`):

```typescript
export interface PredicateDef {
  id: string;                 // (1)!
  jgexName: string;           // (2)!
  label: string;               // dropdown label
  shorthand: (args: string[]) => string;  // (3)!
  icon: string;                 // dropdown icon (a short glyph, not an SVG)
  minArgs: number;
  argLabels: string[];
  argTypes: ArgType[];          // (4)!
  variableArgs?: boolean;       // (5)!
  groups?: { label: string; count: number }[];  // (6)!
}
```

1. The catalogue key, and the value stored in a saved theorem's
   `TheoremPredicate.predicateId`. Must be unique across
   `PREDICATE_DEFINITIONS`.
2. The wire-format name sent to the backend as JGEX — see the
   [custom theorem contract](../../contracts/custom-theorem-contract.md).
   `id` and `jgexName` are **not required to match**: `eqangle6` and
   `eqangle8` are two different UI entries (6-argument and 8-argument forms
   of "equal angles") that both serialize to the same `jgexName: 'eqangle'`.
   Reach for this pattern whenever one JGEX predicate has more than one
   natural UI shape.
3. Renders the human-readable form shown while building a theorem — display
   only, never sent anywhere.
4. `ArgType` is `'point' | 'fraction'`. Both are already fully wired up —
   the argument inputs and their validation
   (`src/types/theoremValidation.ts`) switch on `argTypes[i]` generically,
   so a new predicate using these two kinds needs no UI code, only a
   catalogue entry.
5. Set this for predicates that take a variable number of points (e.g.
   `coll`, `cyclic`) instead of a fixed arity. `minArgs` becomes a floor,
   not the exact count.
6. Purely visual — groups the argument inputs under sub-labels (e.g. "Line
   1" / "Line 2"). Omit it for a predicate with no natural grouping, like
   `obtuse_angle`.

## How a saved theorem becomes JGEX

`predicateToJgex()`, in the same file, is what actually turns a saved
predicate into the string the backend receives:

```typescript
export function predicateToJgex(pred: TheoremPredicate): string {
  const def = PREDICATE_BY_ID.get(pred.predicateId);
  if (!def) throw new Error(`Unknown predicate: ${pred.predicateId}`);
  return `${def.jgexName} ${pred.args.join(' ')}`;
}
```

It looks the definition up by `id` and emits `"<jgexName> <args>"` — nothing
more. This is called from `main.ts` when a theorem is submitted, over every
premise and conclusion. **A new catalogue entry needs no changes here**:
`predicateToJgex` is fully generic, which is why adding a predicate is a
one-file change as long as `jgexName` + space-joined args is enough to
express it.

## Two real entries to copy from

A fixed-arity predicate with a constant argument, `rconst` (ratio equals a
constant):

```typescript
{
  id: 'rconst', jgexName: 'rconst',
  label: 'Ratio Dist = Const',
  shorthand: (a) => `${p(a,0)}${p(a,1)}/${p(a,2)}${p(a,3)} = ${a[4]?.trim() || 'k'}`,
  icon: 'r=k',
  minArgs: 5, argLabels: ['A', 'B', 'C', 'D', 'k'],
  argTypes: ['point', 'point', 'point', 'point', 'fraction'],
  groups: [{ label: 'Ratio', count: 4 }, { label: 'Constant', count: 1 }],
},
```

A variable-arity predicate, `coll` (collinear — three or more points):

```typescript
{
  id: 'coll', jgexName: 'coll',
  label: 'Collinear',
  shorthand: (a) => a.length > 0
    ? a.map((v, i) => v?.trim() || `P${i + 1}`).join(', ') + ' collinear'
    : 'collinear',
  icon: '—',
  minArgs: 3, argLabels: ['A', 'B', 'C'],
  argTypes: ['point', 'point', 'point'],
  variableArgs: true,
},
```

`shorthand` receives the raw argument strings and must handle the
placeholder case (empty slots not yet filled in) — the `p(args, i)` helper
at the top of the file does this for fixed-arity entries: it returns the
trimmed value, or a positional placeholder like `P3` if the slot is still
empty.

## Steps

1. Open `src/types/theorem.ts` and add an entry to `PREDICATE_DEFINITIONS`,
   copying whichever example above is closer to your shape.
2. Nothing else needs to change to get it serialized — see
   [How a saved theorem becomes JGEX](#how-a-saved-theorem-becomes-jgex)
   above.
3. Run `npm run typecheck` to confirm there are no type errors.
4. Verify: run `npm run dev`, open **Advanced Options → User-Defined
   Theorems**, confirm the new
   predicate appears in the dropdown, build a theorem using it, and submit a
   proof to check that the theorem's clause appears correctly in the
   request payload's `custom_theorems` array (DevTools → Network →
   `POST /api/jobs`).

!!! warning "A genuinely new argument type is a bigger change"
    This guide covers adding predicates that use the existing `'point'` and
    `'fraction'` argument kinds. Adding a third kind means also updating the
    input rendering and validation switches in `theoremManager.ts` and
    `theoremValidation.ts` — check both before assuming a catalogue entry
    alone is enough.

## If the change needs to reach the solver, not just the UI

A new predicate here only changes what a user can *pick*. If it also needs
new backend handling — for example, a field the current conversion doesn't
forward — see the backend's
[ownership boundary](../../backend/modules/custom-theorems.md#ownership-boundary)
and [extending custom theorems](../../backend/guides/extend-custom-theorems.md).
