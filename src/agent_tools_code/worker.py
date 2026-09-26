import asyncio
import os
import signal
import sys
from pathlib import Path

from fastapi import FastAPI

from .models import ExecuteRequest, ExecuteResponse

app = FastAPI(title="Code Execution Worker")

MAX_MEMORY_BYTES = 256 * 1024 * 1024
MAX_OUTPUT_BYTES = 100_000
MAX_FILE_BYTES = 1 * 1024 * 1024
MAX_PROCESSES = 32
MAX_OPEN_FILES = 64


def _apply_limits(cpu_seconds: int) -> None:
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY_BYTES, MAX_MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_FILE_BYTES, MAX_FILE_BYTES))
    resource.setrlimit(resource.RLIMIT_NPROC, (MAX_PROCESSES, MAX_PROCESSES))
    resource.setrlimit(resource.RLIMIT_NOFILE, (MAX_OPEN_FILES, MAX_OPEN_FILES))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def _kill_process_group(proc: asyncio.subprocess.Process) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest) -> ExecuteResponse:
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-I",
        "-S",
        "-B",
        "-c",
        request.code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=Path("/tmp"),
        env={
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "PYTHONNOUSERSITE": "1",
        },
        start_new_session=True,
        preexec_fn=lambda: _apply_limits(request.timeout_seconds + 1),
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=request.timeout_seconds + 1,
        )
    except TimeoutError:
        _kill_process_group(proc)
        await proc.wait()
        return ExecuteResponse(
            status="timeout",
            stdout="",
            stderr="execution timed out",
            exit_code=None,
        )

    return ExecuteResponse(
        status="ok" if proc.returncode == 0 else "error",
        stdout=stdout.decode(errors="replace")[:MAX_OUTPUT_BYTES],
        stderr=stderr.decode(errors="replace")[:MAX_OUTPUT_BYTES],
        exit_code=proc.returncode,
    )
