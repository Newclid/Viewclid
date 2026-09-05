# Rendering

Reads the scene and viewport and produces everything the user sees. Has no
mutable state of its own — a full redraw from the current scene is cheap
enough to call on every animation frame.

Source: `src/render/renderer.ts`

## Two-layer approach

The canvas is built from two overlapping HTML elements:

- **SVG** — the static geometry layer: grid, axes, points, edges, circles,
  tool previews. Individual elements can be styled and picked by the
  browser with no extra work.
- **Canvas 2D** — the proof overlay, drawn on top of the SVG. Used because
  the proof sketch needs many small decorations (angle arcs, tick marks,
  parallel marks) that would be unwieldy as SVG elements.

## The `Renderer` class

Constructed once in `main.ts` as `new Renderer(container, viewport, scene)`
— the scene and viewport are held as constructor references, not passed
per-call.

| Method | Does |
|---|---|
| `draw()` | Redraws everything from the held scene/viewport — called whenever they change. Takes no arguments. |
| `resize()` | Reads the container's current size and updates both elements. Takes no arguments. |
| `proofSketch` (setter) | Assigns the active proof's geometry (points, highlighted/premise geometry, markers) to draw on the Canvas layer — set externally by whoever owns the active proof step, not read from `AppStore` inside `Renderer` itself. |

## SVG layer

Every `draw()` call fully replaces the SVG content:

- **Grid and axes** — line spacing adapts to zoom level so lines never get
  too dense or too sparse.
- **Points** — small circles; the snap-candidate point is highlighted.
- **Edges and circles** — straight lines and SVG `<circle>` elements.
- **Tool previews** — rubber-band lines and candidate snap targets while a
  construction is in progress.

## Canvas layer (proof sketch)

When a proof step is active, the renderer draws a geometry sketch on the
Canvas element. Each step contributes:

| Element | Style |
|---|---|
| Premises | Highlighted in amber. |
| Conclusions | Highlighted in green. |
| Equal-angle groups | Color-coded with a rainbow palette. |
| Parallel groups | Matched tick marks on the relevant segments. |

Markers drawn on the Canvas: perpendicular squares at right-angle vertices,
angle arcs with optional tick marks for equal angles, tick marks for equal
lengths, and parallel marks (arrow-like ticks) on parallel segments.

## Coordinate transforms

All drawing coordinates go through `Viewport.worldToScreen()`, so the sketch
follows the current pan and zoom. The renderer never stores `ScreenPoint`
values between frames — they're recomputed on every `draw()` call.
