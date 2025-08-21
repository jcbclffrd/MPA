# Python MCP Server for ExprPredictor Tools

This directory contains a Python-based MCP (Model Context Protocol) server that wraps the existing C++ ExprPredictor tools for easier deployment and integration.

## Overview

The Python MCP server provides:
- HTTP/REST API endpoints for tool discovery and execution
- JSON-RPC style MCP protocol compatibility
- Subprocess integration with existing C++ MCP tools
- Configuration via YAML files and environment variables
- Docker containerization support
- Comprehensive error handling and logging

## Architecture

```
┌─────────────────┐    HTTP/JSON     ┌──────────────────┐    subprocess    ┌─────────────────┐
│   HTTP Client   │ ─────────────► │  Python MCP      │ ─────────────► │   C++ MCP       │
│  (GitHub MCP,   │                │  Server          │                │   Tools         │
│   curl, etc.)   │ ◄───────────── │  (FastAPI)       │ ◄───────────── │   (mcp_demo)    │
└─────────────────┘                └──────────────────┘                └─────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- C++ build environment (g++, make)
- GSL (GNU Scientific Library)
- jsoncpp library

### Install Dependencies

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y libgsl-dev libjsoncpp-dev build-essential

# Install Python dependencies
pip install -r requirements.txt

# Build C++ components
make clean && make
```

### Docker Installation

```bash
# Build Docker image
docker build -t expr-predictor-mcp .

# Run container
docker run -p 8080:8080 expr-predictor-mcp
```

## Configuration

### YAML Configuration (config.yaml)

```yaml
server:
  host: "0.0.0.0"
  port: 8080
  debug: false

mcp:
  executable_path: "./mcp_demo"
  working_directory: "."
  timeout: 30

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Environment Variables

- `MCP_SERVER_HOST` - Override server host (default: 0.0.0.0)
- `MCP_SERVER_PORT` - Override server port (default: 8080)
- `MCP_EXECUTABLE_PATH` - Override path to C++ executable (default: ./mcp_demo)
- `MCP_WORKING_DIR` - Override working directory (default: .)

## Usage

### Starting the Server

```bash
# Using default configuration
python3 mcp_server.py

# Using custom configuration
python3 mcp_server.py --config custom_config.yaml

# Using environment variables
MCP_SERVER_PORT=9000 python3 mcp_server.py
```

### API Endpoints

#### Root Information
```bash
curl http://localhost:8080/
```

#### Health Check
```bash
curl http://localhost:8080/health
```

#### List Available Tools
```bash
curl http://localhost:8080/tools/list
```

#### Get Tool Schema
```bash
curl http://localhost:8080/tools/schema/expr_predictor_obj_func
```

#### Execute Tool
```bash
curl -X POST http://localhost:8080/tools/call/expr_predictor_obj_func \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "maxBindingWts": [1.0, 1.5, 2.0],
      "txpEffects": [1.2, 1.5, 0.8],
      "repEffects": [0.0, 0.0, 0.2],
      "basalTxp": 1.0
    }
  }'
```

#### MCP Request (JSON-RPC style)
```bash
curl -X POST http://localhost:8080/mcp/request \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "params": {}
  }'
```

### Interactive API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## Available Tools

The Python server exposes all 6 C++ MCP tools:

1. **`expr_predictor_obj_func`** - Compute objective function value
2. **`expr_par_get_free_pars`** - Extract free parameters from ExprPar object
3. **`expr_predictor_train`** - Train ExprPredictor model
4. **`expr_predictor_predict`** - Predict expression values
5. **`expr_par_load`** - Load ExprPar parameters from file
6. **`expr_func_predict_expr`** - Predict expression using ExprFunc

See [MCP_TOOLS.md](MCP_TOOLS.md) for detailed tool documentation and schemas.

## Testing

### Run Test Suite
```bash
# Start the server first
python3 mcp_server.py &

# Run tests
python3 test_mcp_server.py

# Run with pytest (if available)
pytest test_mcp_server.py -v
```

### Manual Testing Examples

```bash
# Test basic functionality
./test_examples.sh

# Load testing (requires siege or ab)
siege -c 10 -t 30s http://localhost:8080/tools/list
```

## Deployment

### Local Development
```bash
python3 mcp_server.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker mcp_server:app
```

### Docker Deployment
```bash
docker run -d \
  --name expr-predictor-mcp \
  -p 8080:8080 \
  -e MCP_SERVER_HOST=0.0.0.0 \
  expr-predictor-mcp
```

### Cloud Deployment

#### AWS Lambda
The server can be adapted for AWS Lambda using Mangum:
```python
from mangum import Mangum
handler = Mangum(app)
```

#### Google Cloud Run
```bash
gcloud run deploy expr-predictor-mcp \
  --source . \
  --port 8080 \
  --platform managed
```

## Integration with GitHub MCP Server

The Python server is designed to be compatible with GitHub's MCP server ecosystem:

1. **Tool Discovery**: Implements standard `/tools/list` endpoint
2. **Schema Validation**: Provides tool schemas via `/tools/schema/{name}`
3. **Execution**: Supports tool execution via `/tools/call/{name}`
4. **Error Handling**: Returns standardized error responses
5. **JSON-RPC**: Compatible with MCP protocol requirements

### Example Integration

```python
import httpx

# Discover tools
async with httpx.AsyncClient() as client:
    tools = await client.get("http://localhost:8080/tools/list")
    
    # Execute tool
    result = await client.post(
        "http://localhost:8080/tools/call/expr_predictor_obj_func",
        json={"parameters": {...}}
    )
```

## Monitoring and Logging

### Health Monitoring
```bash
# Check server health
curl http://localhost:8080/health

# Expected response:
{
  "status": "healthy",
  "backend": "accessible", 
  "tools_available": 6
}
```

### Logging Configuration
Modify `config.yaml` to adjust logging:
```yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Troubleshooting

### Common Issues

1. **Server won't start**
   ```bash
   # Check if port is already in use
   lsof -i :8080
   
   # Use different port
   MCP_SERVER_PORT=9000 python3 mcp_server.py
   ```

2. **Backend executable not found**
   ```bash
   # Verify C++ tools are built
   make clean && make
   
   # Check executable exists
   ls -la ./mcp_demo
   ```

3. **Tool execution fails**
   ```bash
   # Check C++ tools work directly
   ./mcp_demo
   
   # Check working directory
   pwd
   ls -la iData/
   ```

4. **Docker build fails**
   ```bash
   # Check dependencies
   docker build --no-cache -t expr-predictor-mcp .
   ```

### Debug Mode

Enable debug mode for verbose logging:
```yaml
server:
  debug: true
logging:
  level: "DEBUG"
```

## Performance Considerations

- **Subprocess Overhead**: Each tool call spawns a subprocess
- **Concurrent Requests**: Limited by system resources and C++ tool performance
- **Memory Usage**: Minimal Python overhead, C++ tools handle heavy computation
- **Caching**: Consider implementing response caching for repeated requests

## Security Considerations

- **Input Validation**: Server validates JSON payloads
- **Subprocess Safety**: Controlled execution of C++ tools
- **Network Security**: Use HTTPS in production
- **Authentication**: Add API keys or OAuth if needed
- **Container Security**: Run as non-root user in Docker

## Contributing

1. **Code Style**: Follow PEP 8 for Python code
2. **Testing**: Add tests for new features
3. **Documentation**: Update this README for changes
4. **Error Handling**: Maintain consistent error response format

## License

Same license as the parent MPA project.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the C++ MCP tools documentation in [MCP_TOOLS.md](MCP_TOOLS.md)
3. Test with the provided test scripts
4. Check server logs for detailed error information