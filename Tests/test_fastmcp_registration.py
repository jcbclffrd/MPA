#!/usr/bin/env python3
"""
Quick test to verify FastMCP tool registration works
"""

import asyncio
from fastmcp import FastMCP

# Create test server
test_mcp = FastMCP("test-server")

@test_mcp.tool
def simple_test() -> str:
    """Simple test tool"""
    return "Test successful"

async def main():
    # Get tools directly
    tools = await test_mcp.get_tools()
    print(f"Registered tools: {list(tools.keys())}")
    
    # Try calling the tool
    result = await test_mcp.call_tool("simple_test", {})
    print(f"Tool result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
