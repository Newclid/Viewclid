# Debugging frontend-backend flow

Covers the most common failure modes when a proof submission isn't working,
and how to diagnose them. If you already know what's wrong, jump to the
matching entry under [Common failures](#common-failures); otherwise the
sections below walk through the flow a submission takes, in order. See
[Backend integration](../modules/backend-integration.md) and
[JGEX emission](../modules/jgex-emission.md) for background on the two
pieces this guide moves between.

## Check the backend is running

```bash
curl http://localhost:8000/api/health
```

A healthy backend returns `200`. A `502 Bad Gateway` on `POST /api/jobs` in
the Network tab means the backend isn't reachable — start it first.

## Inspect network requests

Open **DevTools → Network** and filter by `/api`:

| Request | What to check |
|---|---|
| `POST /api/jobs` | The submission. Confirm the request body has the expected JGEX string and any custom theorems. A `4xx` body contains a backend error message. |
| `GET /api/jobs/{id}` | The polling requests. The body has the current `status` and an optional `message` with progress info. |
| `GET /api/jobs/{id}/result` | Fetched once, on terminal status. The full result, including `stdout`/`stderr` from the solver. |

## Read the JGEX string

The JGEX input panel shows the problem string before submission — copy it
out and check it manually if the backend reports a parse error.

JGEX syntax basics: construction lines are `<points> = <construction> <args>`
(e.g. `A B C = triangle A B C`); goal lines are `? <predicate> <points>`
(e.g. `? perp A B C D`); custom theorem clauses follow the same predicate
syntax. See the [JGEX problem input contract](../../contracts/jgex-problem-input.md)
for the full syntax.

## Common failures

??? failure "Backend not running"
    Symptom: `POST /api/jobs` returns `502`.
    Fix: start the backend — see the [backend setup guide](../../backend/setup.md).

??? failure "Malformed JGEX"
    Symptom: job status is `failed` immediately; `stderr` has a parse or
    resolution error.
    Fix: check the JGEX string from the input panel for typos in
    construction names or point labels.

??? failure "Proof takes too long, or never finishes"
    Symptom: job status is `failed` with a generic message, and the job's
    runtime is close to `timeout_seconds`. `timed_out` is a reserved status
    the backend can't currently produce — a real timeout looks identical to
    any other failure. See
    [solver job lifecycle](../../contracts/solver-job-lifecycle.md#status-state-machine).
    Fix: try a simpler problem to confirm the backend is healthy. If it is,
    the problem may be too complex for the current solver configuration —
    see [backend configuration](../../backend/modules/configuration.md#timeout-configuration).

??? failure "Custom theorem conflict"
    Symptom: job fails with a predicate resolution error naming a theorem.
    Fix: open the theorem manager, check that theorem's premises and
    conclusions for typos or wrong argument counts, and re-save.

??? failure "Polling stops early"
    Symptom: the UI shows "running" indefinitely, no result ever arrives.
    `JobPoller` doesn't log anything to the console — it stops silently on
    any non-retryable error (a `4xx` on a polling request) and records it
    on the job instead. Fix: check the Network tab for a `4xx` on
    `GET /api/jobs/{id}`, or inspect `AppStore` state (see below) for that
    job's `error` field.

## Inspecting state directly

`JobPoller` has no console logging, so the fastest way to see what's
actually happening is a breakpoint, not the console. Set one inside
`updateJob()` in `src/store/appStore.ts` and trigger a proof submission —
you'll see every status transition and the `error` field `JobPoller` sets
when it gives up.
