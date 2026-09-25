from pydantic import BaseModel, Field

class ExecuteRequest(BaseModel):
    code: str = Field(min_length=1, max_length=20_000)
    timeout_seconds: int = Field(default=5, ge=1, le=30)

class ExecuteResponse(BaseModel):
    status: str
    stdout: str
    stderr: str
    exit_code: int | None
