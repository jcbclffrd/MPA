from mcp import client

# Initialize the MCP client with the server URL
server_url = "http://localhost:3000"
client_instance = client.Client(server_url)

# List available tools on the MCP server
def list_tools():
    try:
        tools = client_instance.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"- {tool}")
    except Exception as e:
        print(f"Error listing tools: {e}")

# Example usage
if __name__ == "__main__":
    print("Testing MCP Client...")
    list_tools()
