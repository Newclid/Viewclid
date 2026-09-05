# State stores

Global state that doesn't belong to the canvas — job tracking, proof mode,
and custom theorem persistence. Both stores use the same minimal pub-sub
pattern as [`Scene`](scene-and-geometry.md): `store.subscribe(fn)` gets a
callback on every change.

Source: `src/store/appStore.ts`, `src/store/theoremStore.ts`

## `AppStore`

The central hub for application-level state:

| State | What it holds |
|---|---|
| Problem | The current JGEX problem string, set on submission. |
| Job history | `Map<jobId, JobRecord>` — every proof job in the session, each with status, optional message, and the full result once it arrives. |
| Proof mode | Flag telling the renderer to show the proof overlay and disable canvas editing. |
| Active proof step | The step index and sub-step index highlighted in the proof panel and canvas. |
| Panel tab | Whether the left sidebar shows the toolbar or the proof history. |
| Active tool group | Drives nested tool sub-menus in the toolbar. |
| Goal-pick callback | One-shot callback set by the proof-by-points panel when the user needs to pick a goal point on the canvas. |

Key methods: `setProblem()`, `addJob()`, `updateJob()`, `enterProofMode()`,
`exitProofMode()`.

## `TheoremStore`

Manages user-defined [custom theorems](custom-theorems.md):

- Persisted to browser `localStorage`, surviving page reloads.
- An in-memory cache avoids repeated `localStorage` reads.
- Key methods: `getAll()`, `getById(id)`, `save(theorem)`, `remove(id)`.

Custom theorems are read from this store and included in every
`submitJob()` call — see the
[custom theorem contract](../../contracts/custom-theorem-contract.md).
