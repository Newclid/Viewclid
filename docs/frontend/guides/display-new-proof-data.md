# Displaying new proof data

The backend returns a `JobResultPayload` (see the
[proof result model contract](../../contracts/proof-result-model.md)) that
the frontend stores per-job in `AppStore` and renders in the proof panel or
on the canvas. This guide covers surfacing a new field from that payload —
first as text, since that's the common case, then on the canvas if the field
is geometry.

## Steps

**1. Extend the type definition**

If the backend sends a field that isn't modeled yet, add it to the matching
type in `src/api/types.ts`:

- `JobResultPayload` — for top-level result fields.
- `NewclidProofSections` — for fields inside the structured proof (steps,
  goals, assumptions, etc).

Mark new fields optional (`field?: Type`) if they may be absent on older
backend versions.

**2. No extra plumbing needed to store it**

`JobPoller.fetchResult()` already passes the whole `result` object straight
into `AppStore.updateJob()` — it doesn't pick out individual fields. So the
moment your field exists in the type, it's already available at
`appStore.jobs.get(jobId).result` with zero changes to the polling code. The
only reason to touch `JobPoller` is if the raw value needs preprocessing
(e.g. parsing a string into a structured value) before the rest of the app
sees it.

**3. Show it in the proof panel**

Proof panel rendering lives in `src/ui/proofPanel.ts`, built with the `el()`
helper from `src/ui/dom.ts` — a small wrapper over
`document.createElement()` that takes attributes and children in one call.
This is the real pattern already used there for a plain text field
(`job.result.message`):

```typescript
import { el } from './dom';

if (job.result.message) {
  content.appendChild(el('p', { class: 'proof-error-msg' }, [job.result.message]));
}
```

Follow the same shape for a new field: guard for `undefined`/`null` (older
backend responses may not send it), then append an element built with `el()`
into the relevant part of the panel (job status, proof steps, or metadata —
find the nearest existing block in `proofPanel.ts` and follow its pattern).

!!! info "Two fields already on the model have no display code to copy from"
    `run_info` and `proof_text` exist on `JobResultPayload` today, but
    nothing in `proofPanel.ts` renders either of them yet. If your new field
    is a plain scalar or stat (closer to `run_info` than to structured proof
    steps), you're writing the first example of that pattern, not copying
    one — budget time accordingly.

**4. Show it on the canvas (if the field is geometry)**

This path is more involved, because canvas geometry isn't assembled inside
the renderer itself. The actual pipeline:

1. `main.ts` holds an `appStore.subscribe(...)` callback that reads
   `job.result` whenever it changes, builds a geometry object from the
   problem's JGEX (`parseJgexGeometry()`, `src/emit/jgexParser.ts`) plus
   the proof's own signatures and points, and assigns it to
   `renderer.proofSketch` (a setter — see
   [Rendering](../modules/rendering.md)).
2. `Renderer.draw()` reads `this.proofSketch` and draws it on the Canvas 2D
   layer on every redraw.

A new geometry field needs code in **both** places: something in `main.ts`'s
subscription callback to fold your field into the object passed to
`proofSketch`, and a new drawing branch inside `Renderer.draw()`'s Canvas 2D
section to actually paint it — the coordinate transforms and 2D context are
already set up there, but not the drawing details for a new marker or shape.

**5. Verify**

Run `npm run dev`, submit a proof job, and confirm the new data appears
correctly. Run `npm run typecheck` to catch any type mismatches.
