#!/usr/bin/env python3
"""
Python CLI client for testing the seq2exp MCP server
"""

import asyncio
import json
import sys
import argparse
import subprocess
from typing import Dict, Any, Optional

class MCPClient:
    def __init__(self):
        self.process = None
        self.request_id = 0
        
    def get_next_id(self) -> int:
        self.request_id += 1
        return self.request_id
    
    async def start_server(self):
        """Start the MCP server process"""
        self.process = subprocess.Popen(
            ["python3", "seq2exp_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/home/j/MPA"
        )
        
    async def send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a request to the MCP server and return response"""
        if not self.process:
            return None
            
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            if response_line.strip():
                return json.loads(response_line)
                
            return None
            
        except Exception as e:
            print(f"Error communicating with server: {e}", file=sys.stderr)
            return None
    
    async def send_notification(self, notification: Dict[str, Any]):
        """Send a notification (no response expected)"""
        if not self.process:
            return
            
        try:
            notification_json = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_json)
            self.process.stdin.flush()
        except Exception as e:
            print(f"Error sending notification: {e}", file=sys.stderr)
    
    async def initialize(self) -> bool:
        """Complete MCP initialization handshake"""
        print("🚀 Initializing MCP server...")
        
        # Start server
        await self.start_server()
        
        # Step 1: Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "seq2exp-cli-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self.send_request(init_request)
        if not response or response.get("error"):
            print(f"❌ Failed to initialize: {response}")
            return False
        
        # Step 2: Send initialized notification (CRITICAL!)
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        await self.send_notification(initialized_notification)
        
        print("✅ Server initialized successfully")
        return True
    
    async def list_tools(self) -> Optional[list]:
        """List available tools from the MCP server"""
        print("📋 Listing available tools...")
        
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/list",
            "params": {}
        }
        
        response = await self.send_request(request)
        if not response or response.get("error"):
            print(f"❌ Failed to list tools: {response}")
            return None
        
        tools = response.get("result", {}).get("tools", [])
        print(f"✅ Found {len(tools)} tools:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool.get('name', 'Unknown')} - {tool.get('description', 'No description')}")
        
        return tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a specific tool with arguments"""
        print(f"🔧 Calling tool: {tool_name}")
        
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self.send_request(request)
        if not response or response.get("error"):
            print(f"❌ Tool call failed: {response}")
            return None
        
        result = response.get("result", {})
        print(f"✅ Tool call successful")
        return result
    
    def cleanup(self):
        """Clean up the server process"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

async def test_seq2exp_predict(client: MCPClient):
    """Test the seq2exp prediction tool with sample config"""
    print("\n🧬 Testing seq2exp prediction...")
    
    # Use the correct config format based on seq2exp.conf
    config_content = """# Fast test config for seq2exp
seqFile = iData/rhoseq.txt
exprFile = iData/rhoexp.tab
motifFile = iData/factordts.wtmx
factorExprFile = iData/factorexpdts2s.tab
factorInfoFile = iData/factorinfodts.txt
bindingSitesFile = iData/fas.txt
bindingIntensityFile = iData/topbot2Int.txt
paramFile = iData/synmyout6
modelOption = BINS
objOption = corr
coopFile = iData/coopdt.txt
nAlternations = 1
nRandomStarts = 1
energyThreshold = 5
outputFile = out.txt
dcFile = iData/coreOPT0dc1.txt
duFile = iData/coreOPT0du1.txt"""

    arguments = {
        "config_content": config_content
    }
    
    result = await client.call_tool("seq2exp_predict_impl", arguments)
    if result:
        print(f"📊 Prediction result: {result.get('success', False)}")
        if result.get('output_file'):
            print(f"📄 Output file: {result['output_file']}")
        if result.get('execution_time'):
            print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
        if result.get('stdout'):
            print(f"📝 seq2exp output preview: {result['stdout'][:200]}...")

async def test_config_template(client: MCPClient):
    """Test getting the config template"""
    print("\n📝 Testing config template...")
    
    result = await client.call_tool("seq2exp_config_template_impl", {})
    if result:
        template = result.get('template', '')
        print(f"📋 Config template received ({len(template)} characters)")
        if template:
            print("First few lines:")
            print('\n'.join(template.split('\n')[:5]))

async def test_validate_config(client: MCPClient):
    """Test config validation"""
    print("\n✅ Testing config validation...")
    
    # Test with minimal config
    config_content = "seqFile = iData/rhoseq.txt\nexprFile = iData/rhoexp.tab\nmotifFile = iData/factordts.wtmx"
    
    arguments = {
        "config_content": config_content
    }
    
    result = await client.call_tool("seq2exp_validate_config_impl", arguments)
    if result:
        print(f"🔍 Validation result: {result.get('valid', False)}")
        if result.get('errors'):
            print(f"❌ Errors found: {result['errors']}")
        if result.get('warnings'):
            print(f"⚠️  Warnings: {result['warnings']}")

async def test_get_results(client: MCPClient):
    """Test getting results after a prediction run"""
    print("\n📊 Testing get results...")
    
    result = await client.call_tool("seq2exp_get_results_impl", {})
    if result:
        print(f"📄 Results available: {result.get('success', False)}")
        if result.get('output_files'):
            print(f"📁 Output files: {result['output_files']}")
        if result.get('pdf_available'):
            print(f"📈 PDF plot available: {result['pdf_available']}")

async def interactive_mode(client: MCPClient):
    """Interactive mode for testing tools"""
    print("\n🎮 Interactive Mode")
    print("Available commands:")
    print("  1. list - List all tools")
    print("  2. predict - Run seq2exp prediction")
    print("  3. template - Get config template")
    print("  4. validate - Validate config")
    print("  5. results - Get prediction results")
    print("  6. quit - Exit interactive mode")
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd in ['quit', 'exit', 'q']:
                break
            elif cmd in ['list', '1']:
                await client.list_tools()
            elif cmd in ['predict', '2']:
                await test_seq2exp_predict(client)
            elif cmd in ['template', '3']:
                await test_config_template(client)
            elif cmd in ['validate', '4']:
                await test_validate_config(client)
            elif cmd in ['results', '5']:
                await test_get_results(client)
            else:
                print("Unknown command. Try 'list', 'predict', 'template', 'validate', 'results', or 'quit'")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            break

async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="seq2exp MCP Client CLI")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive mode")
    parser.add_argument("--test-all", action="store_true",
                       help="Run all tests")
    parser.add_argument("--list-tools", action="store_true",
                       help="List available tools")
    parser.add_argument("--predict", action="store_true",
                       help="Test seq2exp prediction")
    parser.add_argument("--template", action="store_true",
                       help="Get config template")
    parser.add_argument("--validate", action="store_true",
                       help="Test config validation")
    parser.add_argument("--results", action="store_true",
                       help="Get prediction results")
    
    args = parser.parse_args()
    
    print("🧬 seq2exp MCP Client CLI")
    print("=" * 40)
    
    # Create client and initialize
    client = MCPClient()
    
    try:
        # Initialize server with proper MCP handshake
        if not await client.initialize():
            sys.exit(1)
        
        # Run requested operations
        if args.interactive:
            await interactive_mode(client)
        elif args.test_all:
            await client.list_tools()
            await test_config_template(client)
            await test_validate_config(client)
            await test_seq2exp_predict(client)
            await test_get_results(client)
        elif args.list_tools:
            await client.list_tools()
        elif args.predict:
            await test_seq2exp_predict(client)
        elif args.template:
            await test_config_template(client)
        elif args.validate:
            await test_validate_config(client)
        elif args.results:
            await test_get_results(client)
        else:
            # Default: list tools
            await client.list_tools()
        
        print("\n✨ Done!")
        
    finally:
        # Clean up
        client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())