#!/usr/bin/env python3
"""
Test FastMCP with async functions
"""

import asyncio
from fastmcp import FastMCP

# Create test server
test_mcp = FastMCP("test-server")

@test_mcp.tool
async def async_tool() -> str:
    """Async tool test"""
    return "Async tool works"

@test_mcp.tool  
def sync_tool() -> str:
    """Sync tool test"""
    return "Sync tool works"

async def main():
    # Get tools directly
    tools = await test_mcp.get_tools()
    print(f"Registered tools: {list(tools.keys())}")

if __name__ == "__main__":
    asyncio.run(main())
