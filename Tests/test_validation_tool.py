#!/usr/bin/env python3
"""
Test validation tool call
"""

import asyncio
import json
import sys

async def test_validation_tool():
    print("Testing validation tool...")
    
    # Start the MCP server
    process = await asyncio.create_subprocess_exec(
        sys.executable, "../seq2exp_mcp_server.py",
        cwd="/home/runner/work/MPA/MPA",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Wait for server to start
        await asyncio.sleep(2)
        
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
        await process.stdout.readline()  # Read init response
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        process.stdin.write((json.dumps(initialized_notification) + "\n").encode())
        await process.stdin.drain()
        await asyncio.sleep(0.5)
        
        # Test validation tool with config
        test_config = """seqFile = iData/rhoseq.txt
exprFile = iData/rhoexp.tab
motifFile = iData/factordts.wtmx
factorExprFile = iData/factorexpdts2s.tab
outputFile = out.txt
modelOption = BINS"""

        validation_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "seq2exp_validate_config",
                "arguments": {
                    "config_content": test_config
                }
            }
        }
        
        print("Calling validation tool...")
        process.stdin.write((json.dumps(validation_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read validation response
        response_data = await asyncio.wait_for(process.stdout.readline(), timeout=10)
        if response_data:
            response = json.loads(response_data.decode().strip())
            print(f"Validation response received")
            
            if "result" in response and "structuredContent" in response["result"]:
                result = response["result"]["structuredContent"]
                print(f"✓ Validation successful!")
                print(f"  Valid: {result.get('valid', 'unknown')}")
                print(f"  Parameters parsed: {result.get('parameter_count', 0)}")
                if result.get('issues'):
                    print(f"  Issues: {result['issues']}")
                return True
            else:
                print("✗ Unexpected validation response format")
                print(response)
                return False
        else:
            print("✗ No response received")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        process.terminate()
        await process.wait()

if __name__ == "__main__":
    result = asyncio.run(test_validation_tool())
    print(f"Test {'PASSED' if result else 'FAILED'}")