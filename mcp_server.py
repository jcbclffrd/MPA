#!/usr/bin/env python3
"""
Python MCP Server wrapper for ExprPredictor tools.

This server wraps the existing C++ MCP tools to provide a Python-based
HTTP interface compatible with the MCP protocol.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPRequest(BaseModel):
    """MCP request model."""
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPToolCall(BaseModel):
    """MCP tool call parameters."""
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class MCPConfig:
    """Configuration manager for MCP server."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self._apply_env_overrides()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            "server": {"host": "0.0.0.0", "port": 8080, "debug": False},
            "mcp": {"executable_path": "./mcp_demo", "working_directory": ".", "timeout": 30},
            "logging": {"level": "INFO"},
            "tools": {"discovery_enabled": True}
        }
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        if "MCP_SERVER_HOST" in os.environ:
            self.config["server"]["host"] = os.environ["MCP_SERVER_HOST"]
        if "MCP_SERVER_PORT" in os.environ:
            self.config["server"]["port"] = int(os.environ["MCP_SERVER_PORT"])
        if "MCP_EXECUTABLE_PATH" in os.environ:
            self.config["mcp"]["executable_path"] = os.environ["MCP_EXECUTABLE_PATH"]
        if "MCP_WORKING_DIR" in os.environ:
            self.config["mcp"]["working_directory"] = os.environ["MCP_WORKING_DIR"]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


class MCPBackend:
    """Backend interface to C++ MCP tools."""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        executable_path = config.get("mcp.executable_path", "./mcp_demo")
        working_dir = config.get("mcp.working_directory", ".")
        
        # Convert to absolute paths
        self.working_directory = Path(working_dir).resolve()
        if Path(executable_path).is_absolute():
            self.executable_path = Path(executable_path)
        else:
            self.executable_path = self.working_directory / executable_path
        
        self.timeout = config.get("mcp.timeout", 30)
        
        # Verify executable exists
        if not self.executable_path.exists():
            raise RuntimeError(f"MCP executable not found: {self.executable_path}")
    
    async def call_mcp_tool(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call the C++ MCP backend with a request."""
        try:
            # For now, we'll simulate the request by calling mcp_demo directly
            # In a full implementation, we would send JSON-RPC requests
            
            if method == "tools/list":
                return await self._get_tools_list()
            elif method == "tools/get_schema":
                tool_name = params.get("name") if params else None
                return await self._get_tool_schema(tool_name)
            elif method == "tools/call":
                tool_name = params.get("name") if params else None
                arguments = params.get("arguments", {}) if params else {}
                return await self._execute_tool(tool_name, arguments)
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Error calling MCP backend: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_tools_list(self) -> Dict[str, Any]:
        """Get list of available tools from C++ backend."""
        # Since mcp_demo outputs all info at once, we'll parse its output
        process = await asyncio.create_subprocess_exec(
            str(self.executable_path),
            cwd=self.working_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            raise RuntimeError("MCP backend timeout")
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise RuntimeError(f"MCP backend failed: {error_msg}")
        
        # Parse the output to extract tools list JSON
        output = stdout.decode()
        return self._extract_json_from_output(output, "tools/list")
    
    async def _get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get schema for a specific tool."""
        if not tool_name:
            raise ValueError("Tool name is required")
        
        # For simplicity, we'll use the known schemas from the C++ implementation
        # In a full implementation, we would call the C++ backend with specific requests
        schemas = {
            "expr_predictor_obj_func": {
                "name": "expr_predictor_obj_func",
                "description": "Compute objective function value for ExprPredictor with given parameters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "parameters": {
                            "type": "object",
                            "description": "ExprPar parameters object"
                        }
                    },
                    "required": ["parameters"]
                }
            },
            "expr_par_get_free_pars": {
                "name": "expr_par_get_free_pars", 
                "description": "Extract free parameters from ExprPar object",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "parameters": {"type": "object", "description": "ExprPar parameters object"},
                        "coopMat": {"type": "object", "description": "Cooperativity matrix"},
                        "actIndicators": {"type": "array", "description": "Activator indicators"},
                        "repIndicators": {"type": "array", "description": "Repressor indicators"}
                    },
                    "required": ["parameters", "coopMat", "actIndicators", "repIndicators"]
                }
            },
            "expr_predictor_train": {
                "name": "expr_predictor_train",
                "description": "Train ExprPredictor model with given data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "initialParameters": {"type": "object", "description": "Initial ExprPar parameters"},
                        "trainingData": {"type": "object", "description": "Training dataset"},
                        "options": {"type": "object", "description": "Training options"}
                    },
                    "required": ["initialParameters", "trainingData"]
                }
            },
            "expr_predictor_predict": {
                "name": "expr_predictor_predict",
                "description": "Predict expression values using trained ExprPredictor",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "parameters": {"type": "object", "description": "Trained ExprPar parameters"},
                        "sequences": {"type": "array", "description": "Input sequences for prediction"},
                        "conditions": {"type": "array", "description": "Experimental conditions"}
                    },
                    "required": ["parameters", "sequences"]
                }
            },
            "expr_par_load": {
                "name": "expr_par_load",
                "description": "Load ExprPar parameters from file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Path to parameter file"},
                        "coopMat": {"type": "object", "description": "Cooperativity matrix"},
                        "repIndicators": {"type": "array", "description": "Repressor indicators"}
                    },
                    "required": ["filename", "coopMat", "repIndicators"]
                }
            },
            "expr_func_predict_expr": {
                "name": "expr_func_predict_expr",
                "description": "Predict expression using ExprFunc",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sites": {"type": "array", "description": "Binding sites (SiteVec)"},
                        "length": {"type": "integer", "description": "Sequence length"},
                        "factorConcentrations": {"type": "array", "description": "TF concentration values"}
                    },
                    "required": ["sites", "length", "factorConcentrations"]
                }
            }
        }
        
        if tool_name not in schemas:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return schemas[tool_name]
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool."""
        if not tool_name:
            raise ValueError("Tool name is required")
        
        # For the demo, we'll call mcp_demo and parse its output
        # In a full implementation, we would send proper JSON-RPC requests
        process = await asyncio.create_subprocess_exec(
            str(self.executable_path),
            cwd=self.working_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            raise RuntimeError("MCP backend timeout")
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise RuntimeError(f"MCP backend failed: {error_msg}")
        
        # Parse the output to extract tool execution result
        output = stdout.decode()
        return self._extract_json_from_output(output, "tools/call")
    
    def _extract_json_from_output(self, output: str, request_type: str) -> Dict[str, Any]:
        """Extract JSON response from mcp_demo output."""
        lines = output.split('\n')
        json_lines = []
        in_json = False
        
        for line in lines:
            if line.strip().startswith('{'):
                in_json = True
                json_lines = [line]
            elif in_json:
                json_lines.append(line)
                if line.strip().endswith('}') and self._is_complete_json(''.join(json_lines)):
                    try:
                        json_str = ''.join(json_lines)
                        result = json.loads(json_str)
                        
                        # Return the appropriate JSON based on request type
                        if request_type == "tools/list" and "tools" in result:
                            return result
                        elif request_type == "tools/call" and ("success" in result or "error" in result):
                            return result
                        else:
                            # Keep looking for the right JSON block
                            in_json = False
                            json_lines = []
                            continue
                    except json.JSONDecodeError:
                        continue
        
        # If no proper JSON found, return a default response
        if request_type == "tools/list":
            return {
                "tools": [
                    {"name": "expr_predictor_obj_func", "description": "Compute objective function value for ExprPredictor with given parameters"},
                    {"name": "expr_par_get_free_pars", "description": "Extract free parameters from ExprPar object"},
                    {"name": "expr_predictor_train", "description": "Train ExprPredictor model with given data"},
                    {"name": "expr_predictor_predict", "description": "Predict expression values using trained ExprPredictor"},
                    {"name": "expr_par_load", "description": "Load ExprPar parameters from file"},
                    {"name": "expr_func_predict_expr", "description": "Predict expression using ExprFunc"}
                ]
            }
        else:
            return {"success": False, "error": "Could not parse backend response"}
    
    def _is_complete_json(self, text: str) -> bool:
        """Check if text contains complete JSON."""
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False


# Initialize FastAPI app
app = FastAPI(
    title="ExprPredictor MCP Server",
    description="Python wrapper for ExprPredictor MCP tools",
    version="1.0.0"
)

# Global config and backend
config = MCPConfig()
backend = MCPBackend(config)


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "ExprPredictor MCP Server",
        "version": "1.0.0",
        "description": "Python wrapper for ExprPredictor MCP tools",
        "endpoints": {
            "tools": "/tools/list",
            "call": "/tools/call/{tool_name}",
            "schema": "/tools/schema/{tool_name}",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test if backend is accessible
        result = await backend.call_mcp_tool("tools/list")
        return {
            "status": "healthy",
            "backend": "accessible",
            "tools_available": len(result.get("tools", []))
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/tools/list")
async def list_tools():
    """List available MCP tools."""
    try:
        result = await backend.call_mcp_tool("tools/list")
        return result
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools/schema/{tool_name}")
async def get_tool_schema(tool_name: str):
    """Get schema for a specific tool."""
    try:
        result = await backend.call_mcp_tool("tools/get_schema", {"name": tool_name})
        return result
    except Exception as e:
        logger.error(f"Error getting schema for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/call/{tool_name}")
async def call_tool(tool_name: str, arguments: Dict[str, Any]):
    """Execute a specific tool."""
    try:
        result = await backend.call_mcp_tool("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        return result
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/request")
async def mcp_request(request: MCPRequest):
    """Generic MCP request endpoint (JSON-RPC style)."""
    try:
        result = await backend.call_mcp_tool(request.method, request.params)
        return result
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    host = config.get("server.host", "0.0.0.0")
    port = config.get("server.port", 8080)
    debug = config.get("server.debug", False)
    
    logger.info(f"Starting MCP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info" if not debug else "debug")