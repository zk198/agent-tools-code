import os
from fastapi import APIRouter, FastAPI, HTTPException
from .models import ExecuteRequest, ExecuteResponse
from .service import CodeExecutionService

service = CodeExecutionService(os.getenv("CODE_WORKER_URL", "http://code-worker:9000"))
app = FastAPI(title="Agent Tools Code", version="0.1.0")
router = APIRouter(prefix="/v1")

@router.post("/python/execute", response_model=ExecuteResponse, operation_id="run_python", tags=["llm"])
async def run_python(request: ExecuteRequest) -> ExecuteResponse:
    try:
        return await service.run_python(request)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="execution worker unavailable") from exc

@app.get("/health", tags=["internal"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

app.include_router(router)
