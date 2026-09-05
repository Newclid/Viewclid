# Backend setup

The backend needs two long-running processes — the FastAPI server and an RQ
worker — plus a Redis-compatible server for queue storage.

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) for dependency management
- A Redis-compatible server (Redis or Valkey)

!!! warning "Boost/CMake toolchain, for now"
    `newclid`/`py-yuclid` are pinned to a git revision in `backend/pyproject.toml`
    (no PyPI release yet), and `py-yuclid` is a compiled C++ extension. The first `uv sync` builds it
    from source, so you'll also need CMake, a C++ compiler, and Boost
    installed. This requirement disappears once the dependency moves to a
    published release.

## Install

From `backend/`:

```bash
uv sync --extra test
```

This installs the runtime dependencies (FastAPI, redis-py, RQ, Uvicorn,
`newclid[yuclid]`, `py-yuclid`) and the test extras (pytest, HTTPX).

## Redis

```bash
docker run --rm -p 6379:6379 redis:7
```

```bash
redis-cli ping
# PONG
```

The default URL is `redis://localhost:6379/0` — see
[configuration](modules/configuration.md) to change it.

## API server

```bash
uv run uvicorn newclid_backend.main:app --reload
```

```bash
curl http://127.0.0.1:8000/api/health
# {"status":"ok"}
```

Interactive OpenAPI docs are served at `http://127.0.0.1:8000/docs` — see the
[API reference](api-reference.md).

## RQ worker

In a second terminal:

```bash
uv run rq worker newclid --url redis://localhost:6379/0
```

The worker must use the same queue name and Redis URL as the API server. If
the API is running but no worker is, submitted jobs stay `queued` forever —
see [debugging job failures](guides/debug-job-failures.md).

## Smoke test

```bash
curl -X POST http://127.0.0.1:8000/api/jobs \
  -H 'Content-Type: application/json' \
  -d '{
    "input_type": "jgex",
    "problem_input": "a b c = triangle a b c ? cong a b a b"
  }'
# {"job_id":"...","status":"queued"}

curl http://127.0.0.1:8000/api/jobs/<job_id>
curl http://127.0.0.1:8000/api/jobs/<job_id>/result
```

See the [solver job lifecycle contract](../contracts/solver-job-lifecycle.md)
for the full status model and response shapes.
