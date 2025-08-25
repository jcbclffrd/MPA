from mcp import client

# Initialize the MCP client with the server URL
server_url = "http://localhost:3000"

try:
    # Create a client instance
    mcp_client = client.create_client(server_url)

    # List available tools
    tools = mcp_client.list_tools()
    print("Available tools:")
    for tool in tools:
        print(f"- {tool}")

except Exception as e:
    print(f"An error occurred: {e}")
