# Viewclid developer documentation

This is the developer documentation for Viewclid — architecture, module
reference, extension guides, and the data contracts shared between the
frontend, backend, and the Newclid/Yuclid engine.

**Looking to use the app instead of change its code?** See the
[user guide](user-guide/index.md). For how to run Viewclid at all (Docker
Compose, requirements), see the
[project README](https://github.com/Newclid/Viewclid).

## Key concepts

Three terms come up on nearly every page here:

- **Newclid** — the geometry solver Viewclid wraps. Backend and frontend
  code call into it and pass its results around, but neither owns or
  documents its internals — those live in the Newclid project itself.
- **JGEX** — the text format Newclid problems are written in (e.g.
  `a b c = triangle a b c ? cong a b a b`). The frontend usually generates it
  from the canvas rather than asking users to write it by hand. Full syntax:
  [JGEX problem input](contracts/jgex-problem-input.md).
- **Solver job** — one request to solve a problem, tracked through a
  `queued → running → succeeded/failed/cancelled` lifecycle. Full details:
  [Solver job lifecycle](contracts/solver-job-lifecycle.md).

## Sections

<div class="grid cards" markdown>

- :material-account:{ .lg .middle } **User Guide**

    ---

    Using the app itself — no code involved.

    [:octicons-arrow-right-24: User guide](user-guide/index.md)

- :material-server:{ .lg .middle } **Backend**

    ---

    The FastAPI + Redis/RQ service that runs solver jobs.

    [:octicons-arrow-right-24: Backend guide](backend/index.md)

- :material-monitor:{ .lg .middle } **Frontend**

    ---

    The TypeScript/Vite canvas application.

    [:octicons-arrow-right-24: Frontend guide](frontend/index.md)

- :material-file-document-multiple:{ .lg .middle } **Contracts**

    ---

    Shared data shapes between frontend, backend, and the engine.

    [:octicons-arrow-right-24: Contracts](contracts/index.md)

</div>

## Where to start

- **New to the codebase?** Read the Architecture page for whichever side
  you're touching first: [backend](backend/architecture.md) or
  [frontend](frontend/architecture.md).
- **Making a specific change?** Check the guides:
  [backend guides](backend/guides/index.md),
  [frontend guides](frontend/guides/index.md).
- **Changing something both sides depend on?** Start at the
  [relevant contract](contracts/index.md) — update it in the same change as
  the code.
