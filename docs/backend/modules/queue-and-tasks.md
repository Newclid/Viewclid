# Queue and tasks

The queue layer is the boundary between the HTTP server and worker execution.
It uses Redis as storage and RQ as the background-job framework.

Source: `queue.py`, `tasks.py`

## Queue wrapper

`queue.py` creates one Redis connection and one RQ queue:

```python
redis_connection = Redis.from_url(REDIS_URL)
newclid_queue = Queue(NEWCLID_QUEUE_NAME, connection=redis_connection)
```

It exposes two functions:

| Function | Responsibility |
|---|---|
| `enqueue_job` | Enqueue a callable with a job id, timeout, result TTL, and failure TTL. |
| `fetch_job` | Fetch an RQ job by id, returning `None` if it doesn't exist. |

The API route uses these helpers instead of importing RQ directly everywhere,
keeping queue configuration in one place.

## Task adapter

`tasks.py` contains the function RQ workers execute:

```python
run_newclid_job(jgex_problem, custom_theorems=None)
```

It imports `run_newclid_from_jgex` lazily, calls it, and returns
`result.model_dump()`. It's intentionally small — the task adapter shouldn't
contain solver logic; that belongs in the [runner](runner.md).

## Queue options

Three operational settings apply when enqueueing a job, all sourced from
[configuration](configuration.md):

| Setting | Use |
|---|---|
| `job_timeout` | Maximum execution time enforced by RQ. |
| `result_ttl` | How long successful results stay in Redis. |
| `failure_ttl` | How long failed job metadata stays in Redis. |

## Worker requirement

The API process only enqueues jobs — it never executes queued work. A
separate RQ worker must be running with the same Redis URL and queue name:

```bash
uv run rq worker newclid --url redis://localhost:6379/0
```

If the worker is missing, `POST /api/jobs` still returns `queued`, but the
job never advances — see
[debugging job failures](../guides/debug-job-failures.md).
