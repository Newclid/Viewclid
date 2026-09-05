# JGEX emission

JGEX is the textual language the Newclid solver reads (see the
[JGEX problem input contract](../../contracts/jgex-problem-input.md)). This
layer converts between the canvas scene and JGEX strings in both directions:
serializing the user's sketch into a problem, and parsing the JGEX-encoded
geometry in the backend's result to drive the proof sketch overlay.

Source: `src/emit/jgex.ts`, `src/emit/jgexParser.ts`, `src/emit/names.ts`

## Emitting JGEX

`src/emit/jgex.ts` builds a JGEX problem string from the current scene and
any custom theorems. It iterates over the scene's construction objects,
looks up each point's label, and assembles the JGEX clauses for the solver
from each object's catalogue entry's `jgex` field (see
[Adding a construction](../guides/add-a-construction.md#6-add-jgex-without-this-the-construction-never-reaches-the-solver))
— a construction with no `jgex` block contributes nothing and is silently
skipped.

Point labels come from `buildNameTable()` in `src/emit/names.ts`, which maps
each `ObjectId` to a letter ("A", "B", …). The same table is used for display
in the proof panel and for round-tripping through the parser.

## Parsing JGEX output

`src/emit/jgexParser.ts` handles the JGEX that comes back from the backend:

| Function | Does |
|---|---|
| `parseConstructionSignature(marker)` | Parses a single construction marker string, e.g. `"eqangle A B C D E F G H"`, into a typed `ConstructionMarker`. |
| `expandJgexPredicates(jgex)` | Expands shorthand predicates into their full forms. |
| `parseJgexGeometry(jgex)` | Extracts `SketchGeom[]` values (segments, lines, circles, circumcircles) from the backend's output. Marker extraction (`perp`, `eqangle`, `midp`, `cong`, `para`, …) is `parseConstructionSignature`'s job, above. |

The parsed geometry goes to the [renderer](rendering.md) to draw the proof
sketch overlay on the Canvas element.
