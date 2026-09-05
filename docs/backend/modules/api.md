# API and routing

The API layer is implemented by `main.py`, `routers/jobs.py`, and
`schemas.py`. It owns the public HTTP contract between the frontend and the
backend.

Source: `main.py`, `routers/jobs.py`, `schemas.py`

## FastAPI application

`main.py` creates the FastAPI app, includes the jobs router, and exposes the
health endpoint:

```text
GET /api/health -> {"status": "ok"}
```

The health endpoint only checks that the ASGI app can respond, not that
Redis or Newclid are healthy.

## Job endpoints

The jobs router is mounted under `/api/jobs`. The full request/response
shapes are the [solver job lifecycle contract](../../contracts/solver-job-lifecycle.md);
this table is the routing summary:

| Method | Path | Responsibility |
|---|---|---|
| `POST` | `/api/jobs` | Create a job id, normalize the JGEX input, serialize custom theorems, enqueue the task, return `queued`. |
| `GET` | `/api/jobs/{job_id}` | Fetch the RQ job, map its internal status to a public status, return a message. |
| `GET` | `/api/jobs/{job_id}/result` | Return `null` while pending, or the stored runner result for terminal states. |

The main request model is `CreateJobRequest` — see the
[JGEX problem input contract](../../contracts/jgex-problem-input.md) for its
fields. The backend strips whitespace from `problem_input` but does not parse
it; parsing happens in the [runner](runner.md).

## Status mapping

`routers/jobs.py` maps RQ's internal status vocabulary to the
[public status](../../contracts/solver-job-lifecycle.md) the frontend sees:

| RQ status / condition | Public status | Notes |
|---|---|---|
| `queued`, `deferred`, `scheduled` | `queued` | Work hasn't started. |
| `started` | `running` | A worker is executing the job. |
| `stopped`, `canceled` | `cancelled` | Interrupted by queue control. |
| `failed` | `failed` | RQ marks the job as failed. |
| `finished`, result status `succeeded` | `succeeded` | Newclid proved all goals. |
| `finished`, result status `failed` | `failed` | Newclid didn't prove all goals, or the runner caught an exception. |
| `finished`, result status `timed_out` | `timed_out` | Not currently reachable — no code path constructs a result with this status. See [solver job lifecycle](../../contracts/solver-job-lifecycle.md#status-state-machine). |

!!! note "Unknown states fail closed"
    Any unrecognized or malformed state is reported as `failed`. Reporting
    success when the backend can't understand the stored result would be far
    worse than a false failure.

## Result endpoint behavior

See [solver job lifecycle: fetch the result](../../contracts/solver-job-lifecycle.md#fetch-the-result)
for the full table of responses by status, including the `error` field's
actual behavior for `failed`/`timed_out` and the fallback for a worker that
crashed before returning any result at all.
