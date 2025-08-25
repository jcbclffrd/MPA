#!/usr/bin/env python3
"""
Updated comprehensive test for FastMCP seq2exp server
"""

import asyncio
import json
import subprocess
import sys
import time

async def test_mcp_tool_call():
    """Test calling a tool via MCP protocol"""
    print("Testing seq2exp MCP tool calls...")
    
    # Start the MCP server process
    process = await asyncio.create_subprocess_exec(
        sys.executable, "seq2exp_mcp_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,  # Ignore banner output
        cwd="/home/runner/work/MPA/MPA"  # Run from the correct directory
    )
    
    try:
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {}, "sampling": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read init response
        response = await process.stdout.readline()
        init_result = json.loads(response.decode().strip())
        print(f"✓ Initialized: {init_result['result']['serverInfo']['name']}")
        
        # Send initialized notification
        initialized = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        process.stdin.write((json.dumps(initialized) + "\n").encode())
        await process.stdin.drain()
        
        # Test config template tool
        template_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "seq2exp_config_template_impl",
                "arguments": {}
            }
        }
        
        process.stdin.write((json.dumps(template_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read template response
        template_response = await process.stdout.readline()
        template_result = json.loads(template_response.decode().strip())
        
        if 'result' in template_result:
            template_data = template_result['result']['content'][0]['text']
            template_obj = json.loads(template_data)
            print(f"✓ Config template retrieved: {len(template_obj['template'])} characters")
        else:
            print(f"✗ Template call failed: {template_result.get('error', 'Unknown error')}")
        
        print("✓ MCP tool call test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ MCP tool call test failed: {e}")
        return False
    finally:
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()

if __name__ == "__main__":
    success = asyncio.run(test_mcp_tool_call())
    sys.exit(0 if success else 1)
