from mcp import client

c = client("http://localhost:3000")

print(c.list_tools())