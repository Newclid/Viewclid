# Backend modules

Reference material describing what each backend component is and how it fits
into the job lifecycle. These are reference pages, not step-by-step guides —
see [guides](../guides/index.md) for those.

| Module | Covers |
|---|---|
| [API](api.md) | FastAPI app, job routes, request schemas, status mapping, result endpoint behavior. |
| [Queue and tasks](queue-and-tasks.md) | The Redis/RQ queue wrapper and the worker task adapter. |
| [Runner](runner.md) | JGEX parsing, Newclid invocation, proof conversion, error handling. |
| [Result model](result-model.md) | Pydantic models returned by the runner and consumed by the frontend. |
| [Custom theorems](custom-theorems.md) | Request validation and conversion of custom theorem payloads into Newclid rules. |
| [Configuration](configuration.md) | Environment variables and operational settings. |
