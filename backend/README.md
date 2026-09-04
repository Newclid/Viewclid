# Viewclid Backend

FastAPI service that turns geometry problems submitted by the frontend into asynchronous solver jobs, runs them against the real Newclid/Yuclid engine, and exposes their status and results.

Long-running solver work never runs inside an HTTP request handler. Jobs are queued with RQ and executed by a separate worker process, backed by Redis — so the API stays responsive no matter how long a proof search takes.

```text
frontend
  → POST /api/jobs               FastAPI enqueues the job
  → Redis / RQ                   job sits in the queue
  → worker                       runs Newclid/Yuclid on the job
  → Redis                        result is stored
  → GET /api/jobs/{id}/result    frontend polls and fetches it
```

## Tech stack

| | |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Queue | [Redis](https://redis.io/) + [RQ](https://python-rq.org/) |
| Engine | [Newclid](https://github.com/Newclid/Newclid) / Yuclid, installed as a normal dependency |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Testing | [pytest](https://docs.pytest.org/) |

## Requirements

* Python 3.11+
* [uv](https://docs.astral.sh/uv/getting-started/installation/)
* A Redis-compatible server

```bash
cd backend
uv sync
```

`uv sync` installs `newclid`/`py-yuclid` like any other dependency. Since the engine's Yuclid component is a compiled C++ extension currently pinned to a git revision (no PyPI release yet), the first sync builds it from source — you'll additionally need CMake, a C++ compiler, and Boost installed. This requirement goes away once the dependency moves to a published release.

## Configuration

Read from environment variables; a `.env` file is optional.

| Variable | Default | Meaning |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis-compatible server used by RQ |
| `NEWCLID_QUEUE_NAME` | `newclid` | Queue name shared by the API and worker |
| `DEFAULT_JOB_TIMEOUT_SECONDS` | `120` | Default maximum runtime for a solver job |
| `RESULT_TTL_SECONDS` | `3600` | How long successful results remain available |
| `FAILURE_TTL_SECONDS` | `3600` | How long failed job info remains available |
| `NEWCLID_COMMAND` | `newclid` | Command name for Newclid-related execution paths |
| `MAX_OUTPUT_CHARS` | `200000` | Maximum stored stdout/stderr/proof output length |

## Running locally

Three processes, three terminals:

```bash
docker run --rm -p 6379:6379 redis:7               # 1. Redis
uv run uvicorn newclid_backend.main:app --reload    # 2. API   → http://127.0.0.1:8000
uv run rq worker newclid                            # 3. worker
```

(On Windows, use `uv run rq worker --worker-class rq.worker.SimpleWorker newclid` for the worker.)

```bash
curl http://127.0.0.1:8000/api/health
```

Interactive API docs are served at `/docs`.

## Running with Docker

See the [root README](../README.md#getting-started) for the full Docker Compose stack. To run just the backend services:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build api worker redis
```

## API endpoints

| Endpoint | Description |
|---|---|
| `GET /api/health` | Health check — `{"status":"ok"}` |
| `POST /api/jobs` | Create a solver job (`input_type`, `problem_input`, optional `custom_theorems`, `timeout_seconds`) → `job_id` |
| `GET /api/jobs/{job_id}` | Job status: `queued`, `running`, `succeeded`, `failed`, `timed_out`, `cancelled` |
| `GET /api/jobs/{job_id}/result` | Proof text, structured proof sections, run info, sketch points, and stdout/stderr for a finished job |

## Testing

```text
tests/
├── unit/          isolated tests, no Redis or engine required
└── integration/   Redis/RQ and real Newclid runner tests
```

```bash
uv sync --extra test

uv run pytest tests/unit                                            # fast, no dependencies
REDIS_URL=redis://127.0.0.1:6379/15 uv run pytest tests -m redis    # needs a real Redis
uv run pytest tests -m slow                                         # runs the real Newclid/Yuclid engine
uv run pytest tests -m "not redis and not slow"                     # everything else
```

Coverage:

```bash
uv run --with pytest-cov pytest tests --cov=newclid_backend --cov-report=html
```

## Project layout

```text
backend/
├── src/newclid_backend/
│   ├── main.py             FastAPI app setup and health endpoint
│   ├── queue.py            Redis/RQ connection and job helpers
│   ├── tasks.py            RQ task adapter
│   ├── newclid_runner.py   Newclid/JGEX runner integration
│   ├── runner_helpers.py   runner helper functions
│   ├── runner_models.py    internal runner result models
│   ├── schemas.py          API request/response models
│   ├── settings.py         environment-based configuration
│   └── routers/jobs.py     job create/status/result endpoints
├── tests/{unit,integration}/
└── pyproject.toml
```

## Third-party licenses

Dependency license report: [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md), generated with `pip-licenses`. Regenerate after a dependency change:

```bash
uv run --extra test --with pip-licenses --with uv_build \
  pip-licenses --format=markdown --with-urls \
  --ignore-packages newclid-backend pip-licenses prettytable wcwidth \
  --output-file THIRD_PARTY_LICENSES.md
```

---

See the [root README](../README.md) for the full project overview and the frontend counterpart.
