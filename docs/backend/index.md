# Backend developer guide

The Viewclid backend is a FastAPI service that receives solver requests from
the frontend, stores them as Redis/RQ jobs, and exposes endpoints for status
polling and result retrieval.

The backend is intentionally thin. It owns transport, validation, queueing,
status mapping, configuration, and result normalization. It does **not** own
the mathematical solver logic — that lives in Newclid, the geometry solver
engine, and its compiled Yuclid rule-matching component.

## Reading order

| Order | Page | Use it for |
|---|---|---|
| 1 | [Architecture](architecture.md) | Understanding the whole backend flow in one pass. Read this first. |
| 2 | [Setup](setup.md) | Running the API server, Redis, and an RQ worker locally. |
| 3 | [Modules](modules/index.md) | Understanding what each backend module is responsible for. |
| 4 | [Guides](guides/index.md) | Making common backend changes safely. |
| 5 | [API reference](api-reference.md) | Where to find live and hand-written API documentation. |
| 6 | [Testing](testing.md) | Choosing and running the right backend tests. |

## Source map

```text
src/newclid_backend/
  main.py
  routers/jobs.py
  schemas.py
  queue.py
  tasks.py
  newclid_runner.py
  runner_helpers.py
  runner_models.py
  settings.py
```
