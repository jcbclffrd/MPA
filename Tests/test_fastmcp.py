#!/usr/bin/env python3
"""
Test FastMCP basic functionality
"""

from fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("test_server")

@mcp.tool
def hello(name: str) -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"

@mcp.tool  
def add_numbers(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    import asyncio
    
    async def test():
        # List tools to verify they're registered
        tools = await mcp.get_tools()
        print(f"Tools type: {type(tools)}")
        print(f"Tools content: {tools}")
        
        # For testing, we'll just print this info
        # In actual usage, you'd call mcp.run_stdio_async()
        print("FastMCP server ready")
    
    asyncio.run(test())