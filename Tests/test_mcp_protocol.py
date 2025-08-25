#!/usr/bin/env python3
"""
Test MCP communication with the seq2exp server
"""

import asyncio
import json
import subprocess
import sys

async def test_mcp_communication():
    print("Testing MCP protocol communication...")
    
    # Start the MCP server process
    process = await asyncio.create_subprocess_exec(
        sys.executable, "../seq2exp_mcp_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Wait for server to start (look for the banner)
        await asyncio.sleep(2)
        
        # Send initialize request
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
        
        print("Sending initialize request...")
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read response
        response_data = await asyncio.wait_for(process.stdout.readline(), timeout=5)
        if response_data:
            response = json.loads(response_data.decode().strip())
            print(f"Initialize response: {response}")
            
            if response.get("id") == 1 and "result" in response:
                print("✓ Server initialized successfully")
                
                # Send initialized notification
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                print("Sending initialized notification...")
                process.stdin.write((json.dumps(initialized_notification) + "\n").encode())
                await process.stdin.drain()
                
                # Wait a moment for the notification to be processed
                await asyncio.sleep(0.5)
                
                # Send tools/list request
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                print("Sending tools/list request...")
                process.stdin.write((json.dumps(tools_request) + "\n").encode())
                await process.stdin.drain()
                
                # Read tools response
                tools_response_data = await asyncio.wait_for(process.stdout.readline(), timeout=5)
                if tools_response_data:
                    tools_response = json.loads(tools_response_data.decode().strip())
                    print(f"Tools response: {tools_response}")
                    
                    if "result" in tools_response and "tools" in tools_response["result"]:
                        tools = tools_response["result"]["tools"]
                        print(f"✓ Found {len(tools)} tools:")
                        for tool in tools:
                            print(f"  - {tool['name']}: {tool.get('description', 'No description')[:100]}...")
                        
                        # Test calling the config template tool
                        call_request = {
                            "jsonrpc": "2.0",
                            "id": 3,
                            "method": "tools/call",
                            "params": {
                                "name": "seq2exp_config_template",
                                "arguments": {}
                            }
                        }
                        
                        print("Testing tool call (config template)...")
                        process.stdin.write((json.dumps(call_request) + "\n").encode())
                        await process.stdin.drain()
                        
                        # Read call response
                        call_response_data = await asyncio.wait_for(process.stdout.readline(), timeout=10)
                        if call_response_data:
                            call_response = json.loads(call_response_data.decode().strip())
                            print(f"Tool call response: {call_response}")
                            
                            if "result" in call_response and "content" in call_response["result"]:
                                print("✓ Tool call successful!")
                            else:
                                print("✗ Tool call failed")
                        else:
                            print("✗ No tool call response received")
                    else:
                        print("✗ Unexpected tools response format")
                else:
                    print("✗ No tools response received")
            else:
                print("✗ Initialize failed")
                print(response)
        else:
            print("✗ No response received")
            
    except asyncio.TimeoutError:
        print("✗ Timeout waiting for response")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Clean up
        process.terminate()
        await process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_communication())