#!/bin/bash

# Test examples for Python MCP Server
# This script demonstrates various ways to interact with the server

echo "Python MCP Server Test Examples"
echo "================================"

BASE_URL="http://localhost:8080"

# Check if server is running
echo "1. Checking if server is running..."
if curl -s "$BASE_URL/health" > /dev/null; then
    echo "✓ Server is running"
else
    echo "✗ Server is not running. Please start it with: python3 mcp_server.py"
    exit 1
fi

echo ""

# Test 1: Root endpoint
echo "2. Testing root endpoint..."
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""

# Test 2: Health check
echo "3. Testing health check..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

# Test 3: List tools
echo "4. Listing available tools..."
curl -s "$BASE_URL/tools/list" | python3 -m json.tool
echo ""

# Test 4: Get schema for each tool
echo "5. Getting schemas for all tools..."
TOOLS=(
    "expr_predictor_obj_func"
    "expr_par_get_free_pars"
    "expr_predictor_train"
    "expr_predictor_predict"
    "expr_par_load"
    "expr_func_predict_expr"
)

for tool in "${TOOLS[@]}"; do
    echo "Schema for $tool:"
    curl -s "$BASE_URL/tools/schema/$tool" | python3 -m json.tool
    echo ""
done

# Test 5: Execute expr_predictor_obj_func tool
echo "6. Testing expr_predictor_obj_func tool execution..."
curl -s -X POST "$BASE_URL/tools/call/expr_predictor_obj_func" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "maxBindingWts": [1.0, 1.5, 2.0],
      "txpEffects": [1.2, 1.5, 0.8],
      "repEffects": [0.0, 0.0, 0.2],
      "basalTxp": 1.0
    }
  }' | python3 -m json.tool
echo ""

# Test 6: Test MCP request endpoint (JSON-RPC style)
echo "7. Testing MCP request endpoint (JSON-RPC style)..."
curl -s -X POST "$BASE_URL/mcp/request" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "params": {}
  }' | python3 -m json.tool
echo ""

# Test 7: Test tool execution via MCP request endpoint
echo "8. Testing tool execution via MCP request endpoint..."
curl -s -X POST "$BASE_URL/mcp/request" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "expr_predictor_obj_func",
      "arguments": {
        "parameters": {
          "maxBindingWts": [1.0],
          "txpEffects": [1.0],
          "repEffects": [0.0],
          "basalTxp": 1.0
        }
      }
    }
  }' | python3 -m json.tool
echo ""

# Test 8: Error handling - invalid tool
echo "9. Testing error handling with invalid tool..."
curl -s "$BASE_URL/tools/schema/invalid_tool" | python3 -m json.tool
echo ""

# Test 9: Error handling - invalid JSON
echo "10. Testing error handling with invalid JSON..."
curl -s -X POST "$BASE_URL/tools/call/expr_predictor_obj_func" \
  -H "Content-Type: application/json" \
  -d '{"invalid": "json"' || echo '{"error": "Invalid JSON request"}'
echo ""

echo "================================"
echo "All tests completed!"
echo ""
echo "Additional endpoints to explore:"
echo "- OpenAPI docs: $BASE_URL/docs"
echo "- ReDoc docs: $BASE_URL/redoc"
echo "- Health check: $BASE_URL/health"