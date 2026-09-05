# Configuration

Backend configuration lives in `settings.py` and is read from environment
variables. Defaults are safe for local development.

Source: `settings.py`

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis-compatible server used by RQ. |
| `NEWCLID_QUEUE_NAME` | `newclid` | Queue name used by the API and worker. |
| `DEFAULT_JOB_TIMEOUT_SECONDS` | `120` | `enqueue_job()`'s internal fallback timeout. See the note in [Timeout configuration](#timeout-configuration) — this is *not* currently what a client gets by omitting `timeout_seconds` on a request. |
| `RESULT_TTL_SECONDS` | `3600` | How long successful job results remain in Redis. |
| `FAILURE_TTL_SECONDS` | `3600` | How long failed job metadata remains in Redis. |
| `NEWCLID_COMMAND` | `newclid` | Reserved from an earlier subprocess-based runner design; the current runner calls Newclid in-process. |
| `MAX_OUTPUT_CHARS` | `200000` | Maximum stored output length for proof text and tracebacks. |

## API/worker consistency

The API server and RQ worker **must** agree on:

- `REDIS_URL`
- `NEWCLID_QUEUE_NAME`
- the Python environment and installed Newclid version

!!! warning
    If these differ, jobs may be enqueued into one queue while a worker
    listens to another, or a worker may fail outright because the expected
    package versions aren't installed. See
    [debugging job failures](../guides/debug-job-failures.md).

Overriding a variable is a normal environment variable, e.g.:

```bash
REDIS_URL=redis://prod-redis:6379/1 uv run uvicorn newclid_backend.main:app
```

## Timeout configuration

`timeout_seconds` can be set per job request and is passed to RQ as the job
timeout. Its default is `120`, set directly on the request schema
(`CreateJobRequest.timeout_seconds`) — **not** read from
`DEFAULT_JOB_TIMEOUT_SECONDS`. That env var only backs `enqueue_job()`'s own
fallback parameter, which the job-creation route never actually exercises,
since it always passes `timeout_seconds` explicitly. Today, changing
`DEFAULT_JOB_TIMEOUT_SECONDS` has no effect on requests that omit
`timeout_seconds` — if you need that to actually work, wire the schema's
default to the setting instead of leaving them as two independent `120`s.
Longer timeouts keep worker processes busy longer, delaying every job queued
behind them.

!!! tip
    Before raising a timeout, check whether the solver work itself can be
    optimized, or whether you need more worker processes instead.

## Output-size configuration

`MAX_OUTPUT_CHARS` prevents unbounded proof text or tracebacks from being
stored. Truncation keeps the *end* of the output, since that's usually where
the most useful error message lives.

## Result retention

`RESULT_TTL_SECONDS` and `FAILURE_TTL_SECONDS` control how long RQ keeps
results in Redis. Longer TTLs make it easier to fetch old results, but
increase Redis memory usage.

| Environment | Example TTL | Why |
|---|---|---|
| Interactive local development | `300` (5 minutes) | You're watching results arrive; nothing needs to persist. |
| Demos and debugging environments | `86400` (24 hours) | Lets you revisit a run without re-submitting it. |
| Production | Start at the default (`3600`), raise only if operators need to inspect older results, and watch Redis memory as you do. | |

## Worker scaling

RQ workers process jobs from the queue one at a time each. To increase
parallelism, start more worker processes — make sure the host has enough
CPU/memory for multiple simultaneous Newclid runs.

!!! tip "After changing execution settings, verify"
    1. `POST /api/jobs` returns a queued job.
    2. The worker receives and starts it.
    3. `GET /api/jobs/{job_id}` moves `queued` → `running` → a terminal status.
    4. `GET /api/jobs/{job_id}/result` returns the expected stored result.
    5. Old results expire according to the configured TTL.
