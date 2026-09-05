# Debugging job failures

Use this guide when submitted jobs stay queued, fail unexpectedly, or return
no usable proof result. If you already know what's wrong, jump straight to
the matching symptom below; otherwise work through the triage order top to
bottom.

## Triage order

1. Is the API server running? `curl http://127.0.0.1:8000/api/health`
2. Is Redis reachable?
3. Is an RQ worker listening to the correct queue?
4. What's the public job status?
5. Fetch the job result.
6. Inspect the runner's `message` and `stderr` fields.
7. Reproduce the runner call directly, in a test or a Python shell.

## Symptoms

??? failure "Job stays `queued` forever"
    Most common causes:

    - no RQ worker is running
    - the worker listens to a different queue name
    - the worker uses a different Redis URL
    - the worker's environment doesn't have Newclid installed (see the next
      symptom — this looks identical to a healthy worker until a job runs)

    Check the worker command:

    ```bash
    uv run rq worker newclid --url redis://localhost:6379/0
    ```

    The queue name must match `NEWCLID_QUEUE_NAME` — see
    [configuration](../modules/configuration.md).

??? failure "Worker starts fine, but every job fails immediately"
    `tasks.run_newclid_job` imports `newclid_backend.newclid_runner` **inside
    the function body**, not at module load time:

    ```python
    def run_newclid_job(jgex_problem, custom_theorems=None):
        from newclid_backend.newclid_runner import run_newclid_from_jgex
        ...
    ```

    That means a broken Newclid installation, or any import-time error in
    the runner module, doesn't stop the worker from starting or from
    reporting itself as ready — it only surfaces the first time an actual
    job runs, as a `failed` status with the `ImportError`/`ModuleNotFoundError`
    traceback in `stderr`. If jobs fail instantly (no meaningful runtime),
    check `stderr` for an import error before assuming it's a solver problem.

??? failure "`POST /api/jobs` returns 503"
    The route couldn't enqueue the job. Check that Redis is running and that
    `REDIS_URL` is correct:

    ```bash
    redis-cli ping
    ```

??? failure "Job reaches `failed`"
    Fetch the result:

    ```bash
    curl http://127.0.0.1:8000/api/jobs/<job_id>/result
    ```

    Then inspect:

    - `result.message` — the high-level failure reason
    - `result.stderr` — a runner traceback, if there was an exception
    - `error` — the API-level error summary (duplicates `result.message`)

??? failure "Job fails right around its `timeout_seconds` value, message is generic"
    This is what a real timeout looks like today: `status: "failed"`,
    `message: "Newclid failed."`, and no traceback in `stderr`. `timed_out`
    is a reserved status that no code path currently produces — RQ kills the
    job and reports it as a plain failure before the backend ever gets a
    chance to distinguish it. See
    [solver job lifecycle](../../contracts/solver-job-lifecycle.md#status-state-machine)
    for the full explanation. Confirm this is what happened by comparing the
    job's actual runtime to its `timeout_seconds`.

??? info "Message is \"Newclid finished, but did not prove all goals.\""
    The backend and worker probably worked correctly — this is a solver
    outcome, not a bug. `solver.run()` returned `False`, so no exception was
    raised and `stderr` will be empty. The likely cause is the JGEX problem
    itself: the selected goal, missing assumptions, missing rules, or solver
    completeness for that case.

??? failure "`stderr` contains a traceback"
    Reproduce the runner directly, bypassing FastAPI, Redis, and RQ:

    ```python
    from newclid_backend.newclid_runner import run_newclid_from_jgex

    result = run_newclid_from_jgex("a b c = triangle a b c ? cong a b a b")
    print(result.status)
    print(result.message)
    print(result.stderr)
    ```

    If the direct call fails the same way, debug the runner or the JGEX
    input — this rules out queue/worker setup entirely, since nothing here
    touches Redis or RQ. If it succeeds, the problem is specific to the
    queue/worker environment (see the two symptoms above), not the runner
    itself. If a custom theorem is involved, the traceback is often
    `Rule(**fields)` rejecting a shape your API validation let through — see
    [extending custom theorems](extend-custom-theorems.md#the-pipeline).
