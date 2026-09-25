import asyncio
from agent_tools_code.mcp import mcp

def test_mcp_projection_is_explicit():
    names = {tool.name for tool in asyncio.run(mcp.list_tools())}
    assert names == {"run_python"}
