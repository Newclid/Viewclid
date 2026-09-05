# Proof UI

Displays the proofs returned by the backend and lets the user step through
them. Entirely read-only from the scene's perspective — it only consumes
data from `AppStore` and never mutates the canvas.

Source: `src/ui/proofPanel.ts`, `src/ui/proofsList.ts`,
`src/ui/proofChoice.ts`, `src/ui/proofByPointsPanel.ts`

## Proof panel

`proofPanel.ts` is the main proof display, shown in the left sidebar once a
job has results.

- Parses each proof step from the text format
  `"N. | premises = (rule) > conclusion"`. Premise references like `[C0]`
  and `[N1]` are resolved to their step labels.
- **Sub-step navigation** — the user steps through each premise and
  conclusion individually; the active sub-step drives the proof sketch on
  the [Canvas](rendering.md).
- Shows a status banner for the active job: queued, running, proved, failed,
  timed out.

## Proofs list

`proofsList.ts` shows a history table for every job submitted this session
— job name, problem snippet, status, duration. Clicking a row makes that job
active, updating the proof panel and canvas overlay.

## Proof choice

`proofChoice.ts` appears when the backend returns more than one proof for
the same problem, letting the user pick which one to display.

## Proof-by-points panel

`proofByPointsPanel.ts` implements a goal-picking mode: the user clicks
points on the canvas to specify proof goals instead of typing JGEX
predicates manually. While active, `AppStore` holds a goal-pick callback and
the canvas click handler invokes it instead of the active construction tool.
See [Adding a goal](../guides/add-a-goal.md).
