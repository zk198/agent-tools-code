import httpx
from .models import ExecuteRequest, ExecuteResponse

class CodeExecutionService:
    def __init__(self, worker_url: str = "http://code-worker:9000") -> None:
        self.worker_url = worker_url

    async def run_python(self, request: ExecuteRequest) -> ExecuteResponse:
        async with httpx.AsyncClient(timeout=request.timeout_seconds + 2) as client:
            response = await client.post(f"{self.worker_url}/execute", json=request.model_dump())
            response.raise_for_status()
            return ExecuteResponse.model_validate(response.json())
