import asyncio
import sys
from .models import ExecuteRequest, ExecuteResponse

class CodeExecutionService:
    async def run_python(self, request: ExecuteRequest) -> ExecuteResponse:
        # Phase 1 safety boundary: subprocess only, no shell, bounded timeout.
        # Production deployment must additionally isolate the worker in a
        # container/VM with CPU, memory, filesystem and network restrictions.
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-I", "-c", request.code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=request.timeout_seconds
            )
        except TimeoutError:
            proc.kill()
            await proc.wait()
            return ExecuteResponse(status="timeout", stdout="", stderr="execution timed out", exit_code=None)
        return ExecuteResponse(
            status="ok" if proc.returncode == 0 else "error",
            stdout=stdout.decode(errors="replace")[:100_000],
            stderr=stderr.decode(errors="replace")[:100_000],
            exit_code=proc.returncode,
        )
