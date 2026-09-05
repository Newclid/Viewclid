# Backend integration

Submits proof jobs to the backend and streams status updates back into the
UI. All communication goes over HTTP to `/api`; the Vite dev server proxies
these requests to `http://localhost:8000`. The wire contract is the
[solver job lifecycle](../../contracts/solver-job-lifecycle.md).

Source: `src/api/backendClient.ts`, `src/api/jobPoller.ts`, `src/api/types.ts`

## `BackendClient`

`src/api/backendClient.ts` is a thin wrapper around `fetch`:

| Method | Calls | Returns |
|---|---|---|
| `submitJob(jgex, customTheorems)` | `POST /api/jobs` | `SubmitJobResponse` with the new `jobId`. |
| `getJobStatus(jobId)` | `GET /api/jobs/{id}` | The current `JobStatus` and an optional progress message. |
| `getJobResult(jobId)` | `GET /api/jobs/{id}/result` | The full `JobResultPayload` once the job is terminal. |
| `healthCheck()` | `GET /api/health` | Used to verify the backend is reachable. |

`ApiError` (in `types.ts`) is thrown on non-2xx responses and carries a
`retryable` flag, so the poller can tell transient network errors from
permanent failures.

## `JobPoller`

`src/api/jobPoller.ts` drives the polling loop after a job is submitted:

1. Polls `getJobStatus()` every 2 seconds.
2. Calls `AppStore.updateJob()` with each new status and message.
3. On a terminal status (`succeeded`, `failed`, `timed_out`, `cancelled`),
   fetches the full result with `getJobResult()` and stores it.
4. Retries automatically on transient network errors; stops permanently on
   `4xx` responses.

## API types

`src/api/types.ts` defines the frontend/backend contract in TypeScript:

| Type | Shape |
|---|---|
| `JobStatus` | `queued \| running \| succeeded \| failed \| timed_out \| cancelled` |
| `SubmitJobResponse` | `{ job_id, status }` |
| `JobStatusResponse` | `{ status, message? }` |
| `JobResultPayload` | The full result — proof sections, sketch geometry, stdout/stderr, run metadata. See the [proof result model contract](../../contracts/proof-result-model.md). |
| `NewclidProofSections` | Structured proof data: points, assumptions, steps, goals, theorem references. |
| `SketchPoint` | A named point with `x, y` in the canvas coordinate space. |
