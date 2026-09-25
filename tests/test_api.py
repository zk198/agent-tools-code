import asyncio
from fastapi.testclient import TestClient
from agent_tools_code.api import app
from agent_tools_code.mcp import mcp

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_python_execution():
    response = client.post("/v1/python/execute", json={"code": "print(2 + 2)"})
    assert response.status_code == 200
    assert response.json()["stdout"].strip() == "4"

def test_mcp_allowlist():
    names = {tool.name for tool in asyncio.run(mcp.list_tools())}
    assert "run_python" in names
    assert "health" not in names


def test_python_does_not_use_shell():
    response = client.post("/v1/python/execute", json={"code": "import subprocess; print('ok')"})
    assert response.status_code == 200
    assert response.json()["stdout"].strip() == "ok"


def test_python_timeout():
    response = client.post("/v1/python/execute", json={"code": "while True: pass", "timeout_seconds": 1})
    assert response.status_code == 200
    assert response.json()["status"] == "timeout"
