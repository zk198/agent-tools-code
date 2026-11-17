# Agent Tools Code

Dedicated code-execution capability for the AI Platform, exposed through a REST API and MCP tool surface. The API delegates execution to a separate worker container so untrusted code does not run in the API process.

## Architecture
```text
agent-core / MCP client → code-api → code-worker
```
The Compose deployment separates API and worker onto an internal execution network. Containers use read-only filesystems, dropped Linux capabilities, `no-new-privileges`, PID limits, CPU/memory limits and a restricted temporary filesystem.

## REST API
- `GET /health` — API liveness.
- `POST /v1/python/execute` — execute a Python request through the isolated worker.

Typed request/response schemas are defined in the service models and exposed through OpenAPI.

## Configuration
- `CODE_WORKER_URL` — internal code-worker URL; required by the API service.

Use the supplied Compose topology or an equivalent isolated deployment. Do not expose the worker network to application clients.

## Development
Python 3.12+; use uv.
```bash
uv sync --dev
uv run ruff check .
uv run mypy src
uv run pytest
```

## Security boundary
This service executes untrusted code. The worker must remain isolated from host files, platform credentials, databases and internal service networks. Retain resource limits and hardening controls. Containerization alone is not a complete hostile-code sandbox; evaluate gVisor, Kata Containers or a dedicated sandbox runtime before enabling arbitrary multi-tenant execution.
