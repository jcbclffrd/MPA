#!/usr/bin/env python3
"""
Test script for the Python MCP Server wrapper.

This script tests all the endpoints and tool functionality.
"""

import asyncio
import json
import time
import httpx
import sys


async def test_mcp_server():
    """Test the MCP server endpoints."""
    base_url = "http://localhost:8080"
    
    async with httpx.AsyncClient() as client:
        print("Testing Python MCP Server wrapper for ExprPredictor tools")
        print("=" * 60)
        
        # Test root endpoint
        print("\n1. Testing root endpoint...")
        response = await client.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
        # Test health endpoint
        print("\n2. Testing health endpoint...")
        response = await client.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
        # Test tools list
        print("\n3. Testing tools list...")
        response = await client.get(f"{base_url}/tools/list")
        print(f"Status: {response.status_code}")
        tools_response = response.json()
        print(json.dumps(tools_response, indent=2))
        
        if "tools" in tools_response:
            tools = tools_response["tools"]
            print(f"\nFound {len(tools)} tools")
            
            # Test schema for first tool
            if tools:
                tool_name = tools[0]["name"]
                print(f"\n4. Testing schema for tool '{tool_name}'...")
                response = await client.get(f"{base_url}/tools/schema/{tool_name}")
                print(f"Status: {response.status_code}")
                print(json.dumps(response.json(), indent=2))
                
                # Test tool execution
                print(f"\n5. Testing execution of tool '{tool_name}'...")
                
                # Use a simple test payload
                test_payload = {
                    "parameters": {
                        "maxBindingWts": [1.0],
                        "txpEffects": [1.0], 
                        "repEffects": [0.0],
                        "basalTxp": 1.0
                    }
                }
                
                response = await client.post(
                    f"{base_url}/tools/call/{tool_name}",
                    json=test_payload
                )
                print(f"Status: {response.status_code}")
                print(json.dumps(response.json(), indent=2))
        
        # Test MCP request endpoint
        print("\n6. Testing MCP request endpoint...")
        mcp_request = {
            "method": "tools/list",
            "params": {}
        }
        response = await client.post(f"{base_url}/mcp/request", json=mcp_request)
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
        print("\n" + "=" * 60)
        print("Test completed!")


def main():
    """Main function."""
    try:
        asyncio.run(test_mcp_server())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()