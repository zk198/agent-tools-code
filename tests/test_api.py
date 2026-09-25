import asyncio
from fastapi.testclient import TestClient
from agent_tools_code.api import app
from agent_tools_code.mcp import mcp
from agent_tools_code.models import ExecuteResponse

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_python_execution(monkeypatch):
    async def fake_run(_request):
        return ExecuteResponse(status="ok", stdout="4\n", stderr="", exit_code=0)
    import agent_tools_code.api as api
    monkeypatch.setattr(api.service, "run_python", fake_run)
    response = client.post("/v1/python/execute", json={"code": "print(2 + 2)"})
    assert response.status_code == 200
    assert response.json()["stdout"].strip() == "4"

def test_mcp_allowlist():
    names = {tool.name for tool in asyncio.run(mcp.list_tools())}
    assert "run_python" in names
    assert "health" not in names

def test_worker_failure_is_502(monkeypatch):
    async def failing_run(_request):
        raise RuntimeError("worker unavailable")
    import agent_tools_code.api as api
    monkeypatch.setattr(api.service, "run_python", failing_run)
    response = client.post("/v1/python/execute", json={"code": "print(1)"})
    assert response.status_code == 502
