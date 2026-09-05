# Scene and geometry

The foundation of the canvas: the in-memory representation of every object
the user has drawn, and all coordinate math. Completely free of DOM or
rendering concerns, so it's testable in isolation.

Source: `src/scene/`, `src/geometry/`

## Scene

`src/scene/scene.ts` is the single source of truth for canvas state.

- Stores a flat list of `GeoObject` instances (points, circles,
  constructions).
- Exposes a listener pub-sub — `scene.subscribe(fn)` reacts to any mutation.
- Maintains an undo stack capped at 100 snapshots; each is a full deep copy
  captured before a user action.
- Key methods: `addObject()`, `removeObject()`, `setTool()`, `undo()`,
  `snapshot()`, `serialize()`.

Object types live in `src/geometry/types-object.ts`:

| Type | Shape |
|---|---|
| `PointObject` | A named point with a `WorldPoint` position. |
| `CircleObject` | A center point and radius. |
| `ConstructionObject` | A named construction (edge, line, circumcircle, …) referencing point ids. |

## Viewport

`src/geometry/viewport.ts` models the camera as
`{ center: WorldPoint, scale: number, width: number, height: number }`.

| Method | Does |
|---|---|
| `worldToScreen(p)` / `screenToWorld(p)` | Convert between coordinate spaces, including the Y-axis flip (world Y increases upward, screen Y increases downward). |
| `pan(dx, dy)` | Shift the camera by screen-pixel deltas. |
| `zoom(factor, screenAnchor)` | Scale while keeping `screenAnchor` pinned to the same world point. |
| `fitPoints(points)` | Auto-zoom and center so all given points are visible. |

## Coordinate types

`src/geometry/coords.ts` defines two branded TypeScript types, `WorldPoint`
and `ScreenPoint`. The factories `world(x, y)` and `screen(x, y)` create
values of the correct type:

```typescript
const p = world(10, 20);   // WorldPoint
renderer.drawAtScreen(p);  // compile error: WorldPoint is not a ScreenPoint
```

Branding catches an entire class of bugs — passing a world coordinate where
a screen pixel is expected, or vice versa — at compile time instead of as a
runtime rendering glitch.

## Geometry utilities

- `src/geometry/primitives.ts` — `distance()`, `midpoint()`, and other pure
  math helpers.
- `src/geometry/hitTest.ts` — picking logic: given a `ScreenPoint` and a
  scene, returns the nearest `GeoObject` within a tolerance (used for point
  snapping and context menus).
