#!/usr/bin/env python3
"""
Test FastMCP tool registration with alternative syntax
"""

import asyncio
from fastmcp import FastMCP

# Create test server
test_mcp = FastMCP("test-server")

# Test tool registration by direct function call
def manual_tool() -> str:
    """Manual tool registration test"""
    return "Manual registration works"

# Register manually
test_mcp.tool(manual_tool)

async def main():
    # Get tools directly
    tools = await test_mcp.get_tools()
    print(f"Registered tools: {list(tools.keys())}")

if __name__ == "__main__":
    asyncio.run(main())
