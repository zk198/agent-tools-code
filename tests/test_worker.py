import asyncio

import pytest

from agent_tools_code.models import ExecuteRequest
from agent_tools_code.worker import MAX_FILE_BYTES, MAX_MEMORY_BYTES, MAX_OPEN_FILES, MAX_PROCESSES
from agent_tools_code.worker import _apply_limits


def test_sandbox_limits_are_defined():
    assert MAX_MEMORY_BYTES == 256 * 1024 * 1024
    assert MAX_FILE_BYTES == 1 * 1024 * 1024
    assert MAX_PROCESSES == 32
    assert MAX_OPEN_FILES == 64


@pytest.mark.skipif(__import__("sys").platform == "win32", reason="resource limits are Unix-only")
def test_apply_limits_reduces_process_limits():
    import resource

    _apply_limits(5)
    assert resource.getrlimit(resource.RLIMIT_CPU)[0] == 5
    assert resource.getrlimit(resource.RLIMIT_FSIZE)[0] == MAX_FILE_BYTES
    assert resource.getrlimit(resource.RLIMIT_NPROC)[0] == MAX_PROCESSES
    assert resource.getrlimit(resource.RLIMIT_NOFILE)[0] == MAX_OPEN_FILES
