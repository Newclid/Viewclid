# Adding a construction

Constructions are `CatalogEntry` objects. `ConstructionTool` handles all
click routing, snapping, undo, and preview automatically — you describe the
slots, the geometry to emit, and (if the construction should be solvable)
how it maps to JGEX. See [Constructions](../modules/constructions.md) for a
reference overview of the types used here.

This guide builds a real, working example: `midpoint`, the simplest
two-point construction in the catalogue (`src/construction/entries/midpoint.ts`).
Use it as your template — copy the file and adjust rather than starting from
a blank one.

## 1. Create the entry file

Add `src/construction/entries/my_construction.ts`.

## 2. Define identity fields

```typescript
import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

export const myConstruction: CatalogEntry = {
  name: 'my-construction', // (1)!
  label: 'My construction', // (2)!
  shortcut: 'X', // (3)!
  icon: () => // (4)!
    iconWrap([
      svgEl('circle', { cx: '11', cy: '11', r: '2', fill: 'currentColor' }),
    ]),
  // ...slots, edges, circles, sketch, jgex go here
};
```

1. Must be unique across the whole catalogue (`src/construction/catalog.ts`)
   — this is the key it's registered under.
2. Toolbar tooltip text.
3. A single unused letter — check `src/construction/catalog.ts` for what's
   already taken.
4. `icon` is a **factory function returning a fresh `<svg>` element**, built
   from the `svgEl`/`iconWrap` helpers in `src/ui/icon-helpers.ts` — not a
   string. SVG nodes can't be reused in two places in the DOM, so a cached
   node would break the second toolbar button that needed it.

## 3. Define slots

`slots: SlotSpec[]` is one entry per click the user must make, in order:

| Kind | Behavior |
|---|---|
| `'pick'` | Snaps to an existing point, or creates a new one, whichever the cursor is nearer to. |
| `'pick-existing'` | Only accepts a click on an existing point — rejects clicks on empty space. |
| `'place-free'` | Always drops a brand-new point at the cursor (grid-snapped), never reuses an existing one. |
| `'derive'` | No click needed for the point's *position* — it's computed from already-filled slots, but a click still advances the construction (see step 6). |
| `'scalar'` | A numeric input rather than a canvas click (e.g. a length or ratio). |

```typescript
slots: [
  { name: 'a', kind: 'pick', label: 'Pick the first endpoint (1 of 2)' },
  { name: 'b', kind: 'pick', label: 'Pick the second endpoint (2 of 2)' },
],
```

`name` is how this slot's bound value is looked up everywhere else on the
entry — in `edges`, `sketch`, `validate`, and `onSlotFilled`, always through
a `Bindings` object (`Record<string, ObjectId | number>`), not by array
index.

## 4. Define `edges` and `circles`

Both are **required** fields (an empty array if you don't need them).
`edges: EdgeSpec[]` draws a line between two slots' bound points while the
construction is in progress:

```typescript
edges: [{ pointIds: ['a', 'b'] }],
circles: [],
```

`pointIds` are **slot names**, not indices. `circles: CircleSpec[]` works
the same way for a center/radius pair, if your construction has one.

## 5. Implement `sketch`

Called once every slot is filled. It receives the full `Bindings` (not a
destructurable array) and must return either a new object to add to the
scene, or `null` if the slots already created everything needed:

```typescript
sketch: (b, scene) => {
  const aId = b.a as ObjectId;
  const bId = b.b as ObjectId;
  const a = scene.objects.get(aId) as PointObject;
  const bb = scene.objects.get(bId) as PointObject;
  const mId = scene.addPoint((a.x + bb.x) / 2, (a.y + bb.y) / 2); // (1)!
  return {
    kind: 'construction', // (2)!
    name: 'my-construction',
    bindings: { a: aId, b: bId, m: mId },
    edges: [[aId, bId]],
    circles: [],
  };
},
```

1. `sketch` can create new points directly on the scene (e.g. the midpoint
   itself) before returning — it isn't limited to just connecting existing
   ones.
2. There's no `'edge'` object kind. Every multi-point construction returns
   `{ kind: 'construction', ... }`; `ConstructionTool.onClick` is what
   actually calls `scene.addObject()` on this return value, not the entry
   itself.

## 6. Add `jgex` — without this, the construction never reaches the solver

`jgex?: JgexBlock[]` is optional on the type, but every real construction
defines it, and skipping it has a specific, silent consequence: when the
scene is serialized to JGEX for submission
(see [JGEX emission](../modules/jgex-emission.md)), any construction with no
`jgex` block is skipped without error. It'll draw fine on the canvas and
simply never appear in the problem sent to the solver.

```typescript
jgex: [
  { def: 'midpoint', signature: ['m', 'a', 'b'], produces: ['m'] },
],
```

`def` is a JGEX construction name the solver understands, `signature` is the
argument order (as slot names), and `produces` lists which of those names
is a *new* point defined by this clause rather than an input.

!!! warning "Picking a `def` is the hard part"
    The vocabulary of valid `def` names comes from the solver, not from
    anything in this frontend codebase — there's no catalogue of them here
    to browse. Before writing a new one, check whether an existing
    construction's `jgex` block already expresses what you need (grep
    `src/construction/entries/` for `def:`), and if your new construction
    genuinely needs a def the solver doesn't have, that's an engine change,
    not a frontend one.

## 7. Add optional hooks

- `validate(b, scene)` — return an error string to block completion (shown
  to the user), or `null` to allow it:
  ```typescript
  validate: (b) =>
    b.a !== undefined && b.b !== undefined && b.a === b.b
      ? 'Two distinct points required'
      : null,
  ```
- `preview(b, scene, cursor)` — extra rubber-band geometry while the cursor
  moves.
- `onSlotFilled(slotName, b, scene)` — react right after one slot is bound,
  before the construction finishes (e.g. emit a reference line as soon as
  its two points exist). Note the first argument is the **slot's name**
  (a string), not its index.

A `'derive'` slot needs two functions instead of `sketch` handling its
position — `project(b, scene, cursor)` computes where the point actually
lands, and `preview(b, scene)` draws the locus it's constrained to (e.g. a
circle). See `src/construction/entries/eqdistance.ts` for a worked example
with both.

## 8. Register in the catalogue

```typescript
// src/construction/catalog.ts
import { myConstruction } from './entries/my_construction';

export const CONSTRUCTION_CATALOG: Record<string, CatalogEntry> = {
  // ...existing entries...
  [myConstruction.name]: myConstruction,
};
```

`CONSTRUCTION_CATALOG` is a `Record`, keyed by each entry's `name` — not an
array.

## 9. Add to a toolbar group (optional)

Open `src/tools/groups.ts` and add the construction's `name` to the
appropriate group array so it appears in the right toolbar section.

## 10. Verify

Run `npm run dev`, find the tool in the toolbar (or press its shortcut), and
click through each slot. Confirm intermediate edges appear and the final
object is emitted correctly, and Ctrl/Cmd+Z undoes one slot at a time. Then
submit a proof and check the request payload (DevTools → Network →
`POST /api/jobs`) actually contains your construction's JGEX clause — this
is the step that catches a missing or wrong `jgex` block, which nothing else
will surface as an error.
