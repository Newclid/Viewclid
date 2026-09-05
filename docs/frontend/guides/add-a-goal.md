# Adding a goal predicate

A goal is a JGEX predicate the solver must prove — for example "these two
segments are equal length." This guide is about adding a new kind of goal
predicate to the **proof-by-points panel**, the point-and-click UI for
building a goal without typing JGEX. See
[JGEX emission](../modules/jgex-emission.md) and
[Proof UI](../modules/proof-ui.md) for background, or the
[user guide](../../user-guide/defining-a-goal.md) to see the panel from the
end-user side first.

!!! warning "This catalogue is not shared with the theorem manager"
    The proof-by-points panel and the theorem manager (used for
    [custom theorems](add-a-custom-theorem.md)) look similar but read from
    two **separate** catalogues with two different data shapes. Adding a
    predicate here does **not** make it available as a theorem premise or
    conclusion, and vice versa — see
    [Adding a predicate to the theorem manager](add-a-custom-theorem.md) if
    that's what you actually need.

## Not every goal needs a code change

Any predicate the solver understands can already be typed directly in the
JGEX input panel, prefixed with `?` — that path has no catalogue at all.
This guide only matters for making a predicate available through the
point-and-click panel, which is a convenience wrapper, not the only way to
express a goal.

## The catalogue

The panel's predicates live in `GOAL_PREDICATES`
(`src/ui/proofByPointsPanel.ts`) as `GoalPredicate` entries:

```typescript
interface GoalPredicate {
  id: string;
  label: string;
  shorthand: string;              // (1)!
  icon: string;
  slotLabels: string[];           // (2)!
  slotGroups?: SlotGroup[];       // (3)!
  variableSlots?: boolean;        // (4)!
  hidden?: boolean;               // (5)!
  description?: string;           // (6)!
  buildJgex(jgexNames: string[]): string;  // (7)!
}
```

1. A **static** string shown as the button's tooltip and above the slot
   list — unlike the theorem manager's `shorthand`, this is not a function.
2. Base slot names, in click order (e.g. `['A', 'B', 'C', 'D']`). The panel
   asks the user to click one canvas point per slot.
3. Purely visual — groups slots under sub-labels (e.g. "Line 1" / "Line 2")
   and gives each group its own highlight color on the canvas while the user
   fills it in.
4. Lets the user add or remove slots beyond the base set with `+`/`−`
   buttons — the real use case is `coll` (collinear), which accepts three or
   more points.
5. Registers the predicate without showing it in the picker grid — see the
   real example below.
6. Extra help text rendered under the slot list. Use it for anything the
   slot labels alone don't make obvious.
7. Turns the resolved point names into the JGEX goal clause, e.g.
   `(ns) => \`perp ${ns.join(' ')}\``. Unlike the theorem manager's
   `predicateToJgex`, there's no shared/generic version — every entry
   provides its own.

## Two real entries to copy from

A fixed-arity predicate with groups, `perp`:

```typescript
{
  id: 'perp', label: 'Perpendicular', shorthand: 'AB ⊥ CD', icon: '⊥',
  slotLabels: ['A', 'B', 'C', 'D'],
  slotGroups: [{ label: 'Line 1', count: 2 }, { label: 'Line 2', count: 2 }],
  buildJgex: (ns) => `perp ${ns.join(' ')}`,
},
```

A variable-arity predicate, `coll`:

```typescript
{
  id: 'coll', label: 'Collinear', shorthand: 'A, B, C, … on line', icon: '—',
  slotLabels: ['A', 'B', 'C'],
  variableSlots: true,
  buildJgex: (ns) => `coll ${ns.join(' ')}`,
},
```

## `hidden` is a real, currently-used escape hatch

`obtuse_angle` is fully defined in `GOAL_PREDICATES` — id, labels,
`buildJgex`, everything — but has `hidden: true`, and the picker grid
filters it out (`GOAL_PREDICATES.filter(p => !p.hidden)`). Use the same
pattern to land a new predicate's plumbing without exposing it in the UI
yet, rather than commenting the entry out or keeping it on a branch.

## Steps

1. Open `src/ui/proofByPointsPanel.ts` and add an entry to
   `GOAL_PREDICATES`, copying whichever example above is closer to your
   shape.
2. Write `buildJgex` — this predicate's own conversion function, not a
   shared one.
3. If two predicates need the same vertex-order caveat that `contri` and
   `contrir` have (see their real `description` text in the source — vertex
   correspondence and orientation matter for those two), add a
   `description` explaining it; don't rely on `slotLabels` alone to carry
   that nuance.
4. Run `npm run typecheck` to confirm there are no type errors.
5. Verify: run `npm run dev`, click **Define Goal**, confirm the new
   predicate appears (or, if you set `hidden: true`, confirm it does *not*
   appear), select it, click through its slots, and check the JGEX preview
   text shown above the submit button before actually submitting. Then
   submit and check `proof_sections.proven_goals` /
   `proof_sections.unproven_goals` in the result — see the
   [proof result model contract](../../contracts/proof-result-model.md#proof-sections).
