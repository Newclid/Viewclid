# Reviewing a proof

After you submit — our midsegment problem, goal `para d e b c`, with
`midpoint_equal_dist` available if the solver wants it — Viewclid switches
to the proof panel and shows a status badge: **Queued…**, **Running…**,
**Proved**, **Failed**, **Timed out**, or **Cancelled**. Queued and running
jobs poll automatically — you don't need to refresh anything.

![The status badge once the solver finishes](../assets/screenshots/proof-status.png)

Once it reads **Proved**, here's stepping through the result — from the
first derived fact to the final one:

![Stepping through the proved midsegment proof, one step at a time](../assets/screenshots/proof.gif)

## Reading a successful proof

![The full panel at step 1: status, legend, assumptions, and the step navigator](../assets/screenshots/proof-step1.png)

Once the job is **Proved**, the panel shows, top to bottom:

- A **legend** explaining the highlight colors used on the canvas.

    ![The legend](../assets/screenshots/proof-legend.png)

- **Assumptions** — the premises the proof starts from.

    ![The Assumptions section](../assets/screenshots/proof-assumptions.png)

- **Numerical checks**, if any were needed — sanity checks the solver ran
  numerically rather than derived logically.
- A **step navigator** (**← Prev** / **Next →**) to move through the proof
  one derived fact at a time.

    ![The Proof Steps navigator, with its Prev/Next controls and step counter](../assets/screenshots/proof-step-navigator.png)

- **Derived Facts** for the current step — each step also has its own
  **← Prev** / **Next →** control for moving between the individual facts
  it derives.

    ![Derived Facts a few steps into the proof](../assets/screenshots/proof-derived-facts.png)

- **Proven Goals**, once you reach the last step.

    ![The Proven Goals section on the final step](../assets/screenshots/proof-proven-goals.png)

As you move through steps, the canvas highlights the geometry each step is
about: the premises it uses in one color, and what it concludes in another,
so you can follow the proof visually instead of just reading predicate
names. Step through to the end and you'll see `para d e b c` listed under
**Proven Goals** — the midsegment theorem, proved by Newclid.

![The final step, full panel: DE parallel to BC, listed under Proven Goals](../assets/screenshots/proof-final.png)

## Reading a failed or partial result

If the solver couldn't prove everything, the panel still shows what it
*did* manage — a **Proved So Far** section, along with any unproven goals —
plus a message explaining the outcome. If the failure was a crash rather
than the solver simply running out of ideas, a raw error trace is shown at
the bottom of the panel; that's mainly useful if you're reporting a bug
rather than adjusting your problem.

If nothing seems to be happening for an unusually long time, see
[Debug frontend-backend flow](../frontend/guides/debug-frontend-backend-flow.md)
in the developer docs — it's written for diagnosing this, not just fixing
code.

## Redrawing

If your problem was submitted as JGEX (typed directly, or via proof by
points — as ours was) rather than drawn by hand, a **Redraw** button lets
you ask the solver to re-lay-out the same problem with different
coordinates — useful if the first layout the solver picked is visually
cramped or confusing. Redraw isn't available for problems you drew yourself
on the canvas, since your own drawing is already the intended layout.

## Starting a new problem

**"← Back to edit"** returns you to the canvas to change the construction or
try a different goal.
