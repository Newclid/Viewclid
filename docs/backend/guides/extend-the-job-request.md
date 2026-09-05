# Extending the job request

Use this guide when adding a new field to `POST /api/jobs` — the endpoint
that creates a solver job (see the
[solver job lifecycle contract](../../contracts/solver-job-lifecycle.md) for
what it already accepts).

A request goes through four hops before Newclid ever runs: **API** (validates
the request) → **queue** (hands it to RQ) → **worker** (a separate process
that picks the job up) → **runner** (calls Newclid). See the
[backend architecture](../architecture.md) if those four names are new to
you. The important question for a new field is: how far along that chain
does it need to travel?

## Two shapes a new field can take

Every field on `CreateJobRequest` today is one of these two shapes. Work out
which one yours is before writing any code — the wrong choice means adding a
parameter that's defined but never actually reached.

**Queue-level** — only the queueing step needs it; the runner never sees it.
`timeout_seconds` is the existing example: it's read once, by `queue.py`,
and turned into RQ's own `job_timeout` argument. It is not one of
`run_newclid_job`'s parameters, and it never reaches `newclid_runner.py`:

```python
# queue.py
def enqueue_job(
    func: Any,
    *args: Any,
    job_id: str | None = None,
    timeout_seconds: int = DEFAULT_JOB_TIMEOUT_SECONDS,
    **kwargs: Any,
) -> Job:
    return newclid_queue.enqueue(
        func, *args, **kwargs,
        job_id=job_id,
        job_timeout=timeout_seconds,   # (1)!
        result_ttl=RESULT_TTL_SECONDS,
        failure_ttl=FAILURE_TTL_SECONDS,
    )
```

1. `timeout_seconds` stops here. `run_newclid_job` and
   `run_newclid_from_jgex` have no `timeout_seconds` parameter at all — RQ
   kills the job from the outside if it overruns.

**Solver-level** — the runner needs the value to actually change what it
does. `custom_theorems` is the existing example: it's forwarded as a real
function argument, hop by hop, all the way to `run_newclid_from_jgex`:

```python
# routers/jobs.py — create_job()
custom_theorems = [theorem.model_dump() for theorem in request.custom_theorems]  # (1)!
enqueue_job(
    run_newclid_job,
    jgex_problem,
    custom_theorems,          # positional args, in order
    job_id=job_id,
    timeout_seconds=request.timeout_seconds,
)
```

```python
# tasks.py
def run_newclid_job(
    jgex_problem: str, custom_theorems: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    from newclid_backend.newclid_runner import run_newclid_from_jgex
    result = run_newclid_from_jgex(jgex_problem, custom_theorems=custom_theorems)
    return result.model_dump()
```

1. Convert Pydantic models to plain dicts **before** they cross the queue
   boundary. RQ pickles whatever you enqueue and stores it in Redis until a
   worker picks it up — a plain `dict` doesn't care which process or which
   version of `newclid_backend` reads it back; a pickled `CustomTheoremRequest`
   instance would tie the worker to the exact same class definition the API
   process used. Keep this pattern for any new object-shaped field.

If your new field is solver-level, it needs a parameter on **both**
`run_newclid_job` and `run_newclid_from_jgex` — not just on the request
schema and the router. RQ calls `run_newclid_job` directly as a plain
function in the worker process; it never goes through `create_job()` again,
so nothing forwards the field automatically.

## Steps

Once you know which shape you need:

1. **Add the field to `CreateJobRequest` in `schemas.py`.** Give it a
   default so existing clients keep working (see the compatibility rule
   below).
2. **Decide queue-level vs. solver-level** using the two examples above.
3. **Queue-level:** read `request.<field>` in `routers/jobs.py` and pass it
   into `enqueue_job(...)` as a keyword argument consumed inside `queue.py`
   — do not add it to `run_newclid_job`'s signature.
4. **Solver-level:** pass it as a new positional/keyword argument through
   `enqueue_job(...)`, add a matching parameter to `run_newclid_job` in
   `tasks.py`, and forward it into `run_newclid_from_jgex` in
   `newclid_runner.py`.
5. **Update the contract** — if the frontend must send the field, update the
   [solver job lifecycle contract](../../contracts/solver-job-lifecycle.md).
6. **Add tests** — a schema validation test, a route test asserting the
   value reaches `enqueue_job`/`run_newclid_job` with the right arguments,
   and a runner test if the field changes solver behavior.

## Compatibility rule

!!! warning "Don't break old clients"
    Give new fields a default. Existing frontend deployments may still send
    the old request shape, and `CreateJobRequest` must keep accepting it.
