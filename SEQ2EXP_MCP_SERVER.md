# seq2exp MCP Server Documentation

## Overview

The seq2exp MCP Server provides a clean API interface to the real seq2exp bioinformatics application for gene expression prediction. It accepts configuration file content directly as text and executes the actual seq2exp C++ application to generate predictions and PDF plots.

## Key Features

- **Direct Config File Interface**: Accepts seq2exp configuration as plain text (no complex JSON transformation)
- **Real Application Execution**: Runs the actual seq2exp C++ bioinformatics application
- **Fast Execution**: ~1.5 seconds with minimal test parameters
- **PDF Generation**: Automatically processes LaTeX output to generate plot.pdf
- **Comprehensive Error Handling**: Proper validation, timeouts, and error reporting
- **RESTful API**: Standard HTTP endpoints with OpenAPI documentation

## Quick Start

### 1. Start the Server

```bash
cd /home/runner/work/MPA/MPA
python3 seq2exp_mcp_server.py
```

Server will be available at `http://localhost:8083`

### 2. Get Configuration Template

```bash
curl -X GET "http://localhost:8083/tools/seq2exp_config_template"
```

### 3. Run Prediction

```bash
curl -X POST "http://localhost:8083/tools/seq2exp_predict" \
  -H "Content-Type: application/json" \
  -d '{
    "config_content": "# Fast test config\nseqFile = iData/rhoseq.txt\nexprFile = iData/rhoexp.tab\nmotifFile = iData/factordts.wtmx\nfactorExprFile = iData/factorexpdts2s.tab\nfactorInfoFile = iData/factorinfodts.txt\nbindingSitesFile = iData/fas.txt\nbindingIntensityFile = iData/topbot2Int.txt\nparamFile = iData/synmyout6\nmodelOption = BINS\nobjOption = corr\ncoopFile = iData/coopdt.txt\nnAlternations = 1\nnRandomStarts = 1\nenergyThreshold = 5\noutputFile = out.txt\ndcFile = iData/coreOPT0dc1.txt\nduFile = iData/coreOPT0du1.txt"
  }'
```

## MCP Tools

### 1. seq2exp_config_template

Returns the default seq2exp configuration file as a template.

**MCP Tool Call:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call", 
  "params": {
    "name": "seq2exp_config_template",
    "arguments": {}
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "template: # Complete seq2exp configuration file\n...\ndescription: Default seq2exp configuration template...\nusage: Copy this template and modify..."
      }
    ]
  }
}
```

### 2. seq2exp_validate_config

Validates configuration file content without running seq2exp.

**MCP Tool Call:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "seq2exp_validate_config",
    "arguments": {
      "config_content": "seqFile = iData/rhoseq.txt\nexprFile = iData/rhoexp.tab\n..."
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0", 
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "valid: true\nissues: []\nparameter_count: 16\nparsed_config: {...}"
      }
    ]
  }
}
```

### 3. seq2exp_predict

Executes the complete seq2exp gene expression prediction pipeline.

Main prediction endpoint that executes seq2exp and returns results.

**Request Body:**
```json
{
  "config_content": "# seq2exp configuration\nseqFile = iData/rhoseq.txt\n..."
}
```

**Response:**
```json
{
  "success": true,
  "execution_time": 1.544,
  "results": {
    "main_output": " maxBindingWts : \n0.891\t1.000\t0.990\t\n...",
    "binding_weights": [0.891, 1.0, 0.99],
    "objective_function": 14.962
  },
  "pdf_path": null,
  "stdout": "m \n0.000000 1.000000 62.000000...",
  "config_content": "# Fast test config\nseqFile = iData/rhoseq.txt\n...",
  "returncode": 0
}
```

### 4. Get Latest Results

**GET** `/tools/seq2exp_get_results`

Retrieves results from the latest seq2exp run without re-executing.

**Response:**
```json
{
  "results": {
    "main_output": " maxBindingWts : \n0.891\t1.000\t0.990\t\n...",
    "binding_weights": [0.891, 1.0, 0.99],
    "objective_function": 14.962
  },
  "pdf_available": true,
  "pdf_url": "/results/pdf/plot.pdf",
  "timestamp": 1692123456.789
}
```

### 5. PDF Download

**GET** `/results/pdf/{filename}`

Downloads generated PDF files (e.g., plot.pdf).

## Configuration Parameters

The server accepts the same configuration parameters as the original seq2exp application. Key parameters:

### Required Parameters
- `seqFile`: Input sequence data (FASTA format)
- `exprFile`: Expression data (tab-delimited)
- `motifFile`: Transcription factor motifs
- `factorExprFile`: Factor expression data
- `outputFile`: Output file for predictions

### Performance Parameters
- `nRandomStarts`: Number of random starts (1 for fast testing, 5+ for accuracy)
- `energyThreshold`: Energy threshold (5 for fast testing, 7+ for accuracy)
- `nAlternations`: Number of alternations (1 for training)

### Model Options
- `modelOption`: BINS, Logistic, Direct, Quenching, ChrMod_Unlimited, ChrMod_Limited
- `objOption`: corr, SSE, Cross_Corr

## Usage Examples

### Example 1: Fast Testing Configuration

```bash
curl -X POST "http://localhost:8083/tools/seq2exp_predict" \
  -H "Content-Type: application/json" \
  -d '{
    "config_content": "# Fast test configuration\nseqFile = iData/rhoseq.txt\nexprFile = iData/rhoexp.tab\nmotifFile = iData/factordts.wtmx\nfactorExprFile = iData/factorexpdts2s.tab\nfactorInfoFile = iData/factorinfodts.txt\nbindingSitesFile = iData/fas.txt\nbindingIntensityFile = iData/topbot2Int.txt\nparamFile = iData/synmyout6\nmodelOption = BINS\nobjOption = corr\ncoopFile = iData/coopdt.txt\nnAlternations = 1\nnRandomStarts = 1\nenergyThreshold = 5\noutputFile = out.txt\ndcFile = iData/coreOPT0dc1.txt\nduFile = iData/coreOPT0du1.txt"
  }'
```

**Expected Response Time:** ~1.5 seconds

### Example 2: Production Configuration

```bash
### Example 2: Production Run (via MCP)

```python
# Example MCP tool call for production prediction
import asyncio
from fastmcp import FastMCP

async def run_production_prediction():
    # Connect to seq2exp MCP server
    mcp = FastMCP("seq2exp-client")
    
    config_content = """# Production configuration
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
nRandomStarts = 5
energyThreshold = 7
outputFile = out.txt
dcFile = iData/coreOPT0dc1.txt
duFile = iData/coreOPT0du1.txt"""
    
    result = await mcp.call_tool("seq2exp_predict", {"config_content": config_content})
    return result
```

**Expected Response Time:** ~3-5 seconds

### Example 3: Configuration Validation (via MCP)

```python
# Example MCP validation call
async def validate_config():
    mcp = FastMCP("seq2exp-client")
    
    test_config = """seqFile = iData/rhoseq.txt
exprFile = iData/rhoexp.tab
invalidParameter = badValue"""
    
    result = await mcp.call_tool("seq2exp_validate_config", {"config_content": test_config})
    return result
```

## MCP Integration Example

```python
#!/usr/bin/env python3
"""
Example MCP integration with seq2exp server
"""
import asyncio
import json
import subprocess
import sys

async def test_mcp_server():
    # Start seq2exp MCP server
    process = await asyncio.create_subprocess_exec(
        sys.executable, "seq2exp_mcp_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # MCP initialization
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
    
    # Read initialization response
    response = await process.stdout.readline()
    print(f"Init response: {response.decode()}")
    
    # Call seq2exp prediction tool
    config = """# Fast test config
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

    prediction_request = {
        "jsonrpc": "2.0", 
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "seq2exp_predict",
            "arguments": {"config_content": config}
        }
    }
    
    process.stdin.write((json.dumps(prediction_request) + "\n").encode())
    await process.stdin.drain()
    
    # Read prediction response
    response = await process.stdout.readline()
    result = json.loads(response.decode())
    print(f"Prediction result: {result}")
    
    process.terminate()
    return result

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
```
            result = await response.json()
            
            if result['success']:
                print(f"Prediction completed in {result['execution_time']:.2f}s")
                print(f"Binding weights: {result['results']['binding_weights']}")
                print(f"Objective function: {result['results']['objective_function']}")
            else:
                print(f"Prediction failed: {result['error']}")

# Run the example
asyncio.run(run_seq2exp_prediction())
```

## Error Handling

The server provides comprehensive error handling:

### Common Error Scenarios

1. **Missing Input Files**
   ```json
   {
     "valid": false,
     "issues": ["File not found: /path/to/missing/file.txt"]
   }
   ```

2. **seq2exp Execution Failure**
   ```json
   {
     "success": false,
     "error": "seq2exp failed: Error message from application",
     "returncode": 1
   }
   ```

3. **Timeout**
   ```json
   {
     "success": false,
     "error": "seq2exp execution timed out after 120 seconds"
   }
   ```

4. **Invalid Configuration Format**
   ```json
   {
     "valid": false,
     "issues": ["Line 5: Missing '=' - invalid line format"]
   }
   ```

## Performance Notes

- **Testing Parameters**: Use `nRandomStarts=1, energyThreshold=5` for ~1-2 second execution
- **Production Parameters**: Use `nRandomStarts=5+, energyThreshold=7+` for accurate results (3-30 minutes)
- **Timeout**: Default 120-second timeout for seq2exp execution

## MCP Protocol

This server implements the MCP (Model Context Protocol) for direct integration with Claude Desktop:

1. **stdio Transport**: Uses JSON-RPC over stdin/stdout
2. **Tool Registration**: 4 MCP tools automatically registered
3. **Error Handling**: Structured MCP error responses
4. **Process Isolation**: No network exposure, direct process communication

## Dependencies

### System Requirements
- Ubuntu/Debian Linux
- GSL (GNU Scientific Library): `sudo apt-get install libgsl-dev`
- LaTeX (for PDF generation): `sudo apt-get install texlive`

### Python Requirements
- fastmcp (MCP framework)
- aiofiles (async file operations)
- pydantic (data validation)

Install with:
```bash
pip install fastmcp>=2.11.0 aiofiles>=23.2.0 pydantic>=2.0.0
```

## Architecture

```
Config Content (Text) → Temp Config File → ./seq2exp → Results + format.tex → scriptse.sh → plot.pdf
```

The server follows the problem statement requirement of accepting config file content directly as text, creating temporary config files, and executing the real seq2exp application without reimplementing its functionality.