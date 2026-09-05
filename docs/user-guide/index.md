# User guide

Viewclid lets you construct a plane geometry problem visually, define what
you want to prove, and watch the [Newclid](https://github.com/Newclid/Newclid)
solver produce a step-by-step proof — without writing any JGEX by hand
(though you can, if you prefer).

This guide covers using the app. If you're looking for architecture,
extension guides, or the frontend/backend code itself, that's the
[developer documentation](../index.md) instead.

## What we'll build

Rather than describe each screen in the abstract, this guide walks through
one real example from an empty canvas to a finished proof — the classic
**midsegment theorem**. We'll:

1. Draw a triangle `ABC`, then mark `D` as the midpoint of `AB` and `E` as
   the midpoint of `AC` — [Constructing a problem](constructing-a-problem.md).
2. Ask the solver to prove that segment `DE` is **parallel** to `BC` —
   [Defining a goal](defining-a-goal.md).
3. Along the way, teach the solver a reusable fact — "a midpoint is
   equidistant from both endpoints" — as a [custom theorem](custom-theorems.md).
4. Submit, and [step through the resulting proof](reviewing-a-proof.md) with
   the canvas highlighting exactly which points each step is about.

By the end you'll have seen every major screen in the app, driven by one
coherent problem instead of four unrelated screenshots.

## Two ways to work, throughout

Every step above has a visual path (click points and shapes on the canvas)
and a text path (type [JGEX](../contracts/jgex-problem-input.md) directly).
The visual path is the intended default — it's there so you never have to
know JGEX syntax. The text path exists for anyone who already knows it and
wants to move faster, or who needs a predicate the visual tools don't
expose yet. We'll show both as we go.

Ready? Start with [constructing the problem](constructing-a-problem.md).
