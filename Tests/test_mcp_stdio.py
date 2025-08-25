#!/usr/bin/env python3
"""
Test FastMCP stdio functionality directly
This simulates how Claude Desktop would interact with the MCP server
"""

import asyncio
import json
import subprocess
import sys
import time

async def test_mcp_server():
    """Test the MCP server via stdio communication"""
    print("Testing seq2exp MCP server via stdio...")
    
    # Start the MCP server process
    process = await asyncio.create_subprocess_exec(
        sys.executable, "../seq2exp_mcp_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=".."  # Run from parent directory where iData is located
    )
    
    try:
        # MCP initialization request
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
        
        # Send initialization
        init_message = json.dumps(init_request) + "\n"
        process.stdin.write(init_message.encode())
        await process.stdin.drain()
        
        # Read response with timeout and better error handling
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
            if response_line:
                response = json.loads(response_line.decode().strip())
                print(f"✓ Server initialized: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            else:
                print("✗ No initialization response received")
                return False
        except asyncio.TimeoutError:
            print("✗ Initialization timeout")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ JSON decode error: {e}")
            return False
        
        # Send initialized notification (required by MCP protocol)
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        initialized_message = json.dumps(initialized_notification) + "\n"
        process.stdin.write(initialized_message.encode())
        await process.stdin.drain()
        
        # Test tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        tools_message = json.dumps(tools_request) + "\n"
        process.stdin.write(tools_message.encode())
        await process.stdin.drain()
        
        # Read tools response with timeout
        try:
            tools_response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
            if tools_response_line:
                raw_response = tools_response_line.decode().strip()
                print(f"Raw tools response: {raw_response}")
                tools_response = json.loads(raw_response)
                print(f"Parsed tools response: {tools_response}")
                tools = tools_response.get('result', {}).get('tools', [])
                print(f"✓ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
            else:
                print("✗ No tools response received")
                return False
        except asyncio.TimeoutError:
            print("✗ Tools list timeout")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Tools JSON decode error: {e}")
            return False
        
        print("✓ MCP server test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ MCP server test failed: {e}")
        return False
    finally:
        # Clean shutdown
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
