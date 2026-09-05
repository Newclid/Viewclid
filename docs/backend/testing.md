# Backend testing

Backend tests are split into unit and integration tests, further split by
`pytest` marker. Use the smallest test level that proves the behavior you
changed.

```text
tests/
├── unit/          isolated tests, no Redis or engine required
└── integration/   Redis/RQ and real Newclid runner tests
```

## Unit tests

Unit tests run without a real Redis server or worker.

| Test area | What it verifies |
|---|---|
| Health endpoint | The FastAPI app responds to `/api/health`. |
| Job routes | Route behavior, public statuses, messages, unknown-job handling — with a mocked queue. |
| Schemas | Request validation, custom theorem validation, duplicate names, predicate-line cleanup. |
| Queue wrapper | Enqueue/fetch behavior with mocked queue state. |
| Runner helpers | Output truncation, custom rule conversion, proof dependency indexing. |
| Runner models | Pydantic model validation, especially sketch points. |
| Tasks | The RQ task adapter returns a serializable dictionary. |

```bash
uv run pytest tests/unit
```

## Integration tests

Integration tests need real Redis/RQ, and some need the real Newclid/Yuclid
engine — marked `redis` and `slow` respectively (registered in
`backend/pyproject.toml`).

| Test area | What it verifies | Marker |
|---|---|---|
| API job lifecycle | A submitted job moves through the expected lifecycle. | `redis` |
| Redis/RQ behavior | Jobs can be enqueued and processed through the real queue. | `redis` |
| Unknown jobs | Missing job ids return the expected API error behavior. | `redis` |
| Newclid runner integration | The runner parses a real JGEX problem and produces a result. | `slow` |

```bash
REDIS_URL=redis://127.0.0.1:6379/15 uv run pytest tests -m redis
uv run pytest tests -m slow
```

!!! tip "Everything, or everything fast"
    ```bash
    uv run pytest tests                              # everything
    uv run pytest tests -m "not redis and not slow"  # fast subset only
    ```

## Choosing what to add

| Change type | Test expectation |
|---|---|
| Pydantic schema change | Unit test in `tests/unit/test_schemas.py` or a focused validation file. |
| Route behavior change | Unit route test, plus an integration test if Redis/RQ behavior changes. |
| Queue configuration change | Unit test for wrapper behavior, integration test with real Redis/RQ. |
| Runner output change | Runner helper/model tests, plus at least one runner integration test. |
| Full job lifecycle change | Integration test that submits a job and reads the final result. |

## Coverage

```bash
uv run --with pytest-cov pytest tests --cov=newclid_backend --cov-report=html
```
