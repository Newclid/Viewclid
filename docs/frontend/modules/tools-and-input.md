# Tools and input

Translates raw DOM events into tool invocations and viewport changes. Sits
between the browser and the [scene](scene-and-geometry.md) — it never reads
from the DOM after setup, and never renders anything.

Source: `src/input/`, `src/tools/`

## Tool interface

Every construction implements the `Tool` interface (`src/tools/tool.ts`):

| Method | Called |
|---|---|
| `onClick(ctx: ToolContext)` | On each canvas left-click. |
| `onMove(ctx: ToolContext)` | On mouse move, for live previews. |
| `onDeactivate(ctx)` | When the tool is switched away from — clears transient state. |
| `captureState()` / `restoreState(state)` | Optional. Snapshot/replay in-progress state so undo can rewind mid-construction (see [Keyboard shortcuts](#keyboard-shortcuts) below — there's no separate `cancel()` method). |
| `currentSlotLabel()` | Optional. Label for the slot the user needs to fill next; `null` when idle. |

`ToolContext` bundles the scene, world position, screen position, current
viewport scale, and whether Shift is held.

`getTool(id)` in `src/tools/registry.ts` returns the `Tool` instance for a
given tool id string — tools are singletons, lazily created on first access.

## Click dispatch

`src/input/toolDispatcher.ts` handles `mousedown` on the canvas:

1. Converts the screen pixel to a `WorldPoint` via `Viewport`.
2. Applies grid snapping (disabled while Shift is held).
3. Builds a `ToolContext` and calls `getTool(scene.tool).onClick(ctx)`.
4. Captures an undo snapshot in the scene before the tool mutates anything.

Right-click on a point opens the point context menu
(`src/ui/pointContextMenu.ts`) instead of invoking the active tool.

## Pan and zoom

`src/input/panZoom.ts` handles viewport navigation:

- **Pan** — right-click or middle-click drag, using pointer capture so
  panning continues past the canvas edge.
- **Zoom** — Ctrl+wheel or two-finger pinch, centered on the cursor so the
  point under it stays fixed.
- **Trackpad scroll** — plain wheel events (no Ctrl) pan instead of zooming.

Redraws from pan/zoom are coalesced with `requestAnimationFrame` to avoid
redundant work.

## Keyboard shortcuts

`src/input/shortcuts.ts` listens for `keydown` on the document:

| Shortcut | Action |
|---|---|
| Ctrl/Cmd + Z | Undo — rewinds the scene's undo stack. |
| Escape | Cancels the in-progress construction, step by step, by repeatedly invoking undo — not a dedicated tool method. |
| Letter keys | Switch tool, per each construction's `shortcut` field in the [catalogue](constructions.md). |

Shortcuts are suppressed when the focused element is an `INPUT` or
`TEXTAREA`, so typing in the JGEX input or theorem editor isn't intercepted.
