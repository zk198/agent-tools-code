import pytest
from fastapi.testclient import TestClient
from agent_tools_code.worker import app

def test_worker_executes_python():
    response = TestClient(app).post("/execute", json={"code": "print(2 + 3)"})
    assert response.status_code == 200
    assert response.json()["stdout"].strip() == "5"

def test_worker_timeout():
    response = TestClient(app).post("/execute", json={"code": "while True: pass", "timeout_seconds": 1})
    assert response.status_code == 200
    assert response.json()["status"] == "timeout"
