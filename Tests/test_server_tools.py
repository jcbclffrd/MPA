#!/usr/bin/env python3
"""
Test tool registration in seq2exp server directly
"""

import asyncio
import sys
import os

# Add parent directory to path to import seq2exp_mcp_server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the MCP server module
import seq2exp_mcp_server

async def test_tools():
    """Test tool registration"""
    mcp = seq2exp_mcp_server.mcp
    tools = await mcp.get_tools()
    print(f"Tools found: {list(tools.keys())}")
    for name, tool in tools.items():
        print(f"  - {name}: {tool.description}")

if __name__ == "__main__":
    asyncio.run(test_tools())
