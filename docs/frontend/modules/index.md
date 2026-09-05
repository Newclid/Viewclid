# Frontend modules

Reference material for what each frontend layer is and how it fits together
— see [architecture](../architecture.md) for how they connect, and
[guides](../guides/index.md) for step-by-step recipes.

| Module | Covers |
|---|---|
| [Scene and geometry](scene-and-geometry.md) | The in-memory canvas state and pure coordinate math. |
| [Tools and input](tools-and-input.md) | Translating DOM events into tool actions and viewport changes. |
| [Constructions](constructions.md) | The catalogue of built-in constructions and the slot-filling framework. |
| [Rendering](rendering.md) | Drawing the scene (SVG) and the proof overlay (Canvas). |
| [State stores](state-stores.md) | Global state outside the canvas: jobs, proof mode, custom theorems. |
| [JGEX emission](jgex-emission.md) | Converting between the canvas scene and JGEX strings. |
| [Backend integration](backend-integration.md) | Submitting jobs and polling for results. |
| [Proof UI](proof-ui.md) | Displaying proofs and letting the user step through them. |
| [Custom theorems](custom-theorems.md) | User-defined lemmas: data model, validation, and the theorem manager UI. |
