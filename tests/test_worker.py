from unittest.mock import patch

import pytest

from agent_tools_code.worker import (
    MAX_FILE_BYTES,
    MAX_MEMORY_BYTES,
    MAX_OPEN_FILES,
    MAX_PROCESSES,
    _apply_limits,
)


def test_sandbox_limits_are_defined():
    assert MAX_MEMORY_BYTES == 256 * 1024 * 1024
    assert MAX_FILE_BYTES == 1 * 1024 * 1024
    assert MAX_PROCESSES == 32
    assert MAX_OPEN_FILES == 64


@pytest.mark.skipif(__import__("sys").platform == "win32", reason="resource limits are Unix-only")
def test_apply_limits_sets_expected_unix_limits():
    import resource

    with patch.object(resource, "setrlimit") as setrlimit:
        _apply_limits(5)

    calls = {call.args[0]: call.args[1] for call in setrlimit.call_args_list}
    assert calls[resource.RLIMIT_CPU] == (5, 5)
    assert calls[resource.RLIMIT_AS] == (MAX_MEMORY_BYTES, MAX_MEMORY_BYTES)
    assert calls[resource.RLIMIT_FSIZE] == (MAX_FILE_BYTES, MAX_FILE_BYTES)
    assert calls[resource.RLIMIT_NPROC] == (MAX_PROCESSES, MAX_PROCESSES)
    assert calls[resource.RLIMIT_NOFILE] == (MAX_OPEN_FILES, MAX_OPEN_FILES)
    assert calls[resource.RLIMIT_CORE] == (0, 0)
