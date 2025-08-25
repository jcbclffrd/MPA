#!/usr/bin/env python3
"""
Test approach for MCP function definition
"""

import asyncio
from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("test_server")

# Define the function first
async def my_config_template() -> dict:
    """Get config template"""
    return {"template": "test config content"}

async def my_validate(config_content: str) -> dict:
    """Validate config"""
    return {"valid": True, "config": config_content}

# Register them as tools
mcp.tool(my_config_template, name="config_template")
mcp.tool(my_validate, name="validate_config")

async def test():
    # Test direct function calls
    print("Direct function call:")
    result1 = await my_config_template()
    print(f"Template result: {result1}")
    
    result2 = await my_validate("test config")
    print(f"Validate result: {result2}")
    
    # Test registry
    tools = await mcp.get_tools()
    print(f"Registered tools: {list(tools.keys())}")

if __name__ == "__main__":
    asyncio.run(test())