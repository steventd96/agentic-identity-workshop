#!/bin/bash

# Start Langflow with Custom Tools
# This script sets up the environment and starts Langflow with the custom tools loaded

# Get the absolute path to the tools directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOLS_DIR="$SCRIPT_DIR/tools"

# Check if tools directory exists
if [ ! -d "$TOOLS_DIR" ]; then
    echo "Error: Tools directory not found at $TOOLS_DIR"
    exit 1
fi

# Display banner
echo "================================================"
echo "  Starting Langflow with AskHR Custom Tools"
echo "================================================"
echo ""
echo "Tools directory: $TOOLS_DIR"
echo ""
echo "Custom tools that will be loaded:"
echo "  - Token Exchange Tool"
echo "  - Vault Tool"
echo "  - Database Tool"
echo ""

# Set environment variable for Langflow to find custom components
export LANGFLOW_COMPONENTS_PATH="$TOOLS_DIR"

# Optional: Set other Langflow environment variables
export LANGFLOW_HOST="${LANGFLOW_HOST:-0.0.0.0}"
export LANGFLOW_PORT="${LANGFLOW_PORT:-7860}"
export LANGFLOW_LOG_LEVEL="${LANGFLOW_LOG_LEVEL:-INFO}"

echo "Environment variables set:"
echo "  LANGFLOW_COMPONENTS_PATH=$LANGFLOW_COMPONENTS_PATH"
echo "  LANGFLOW_HOST=$LANGFLOW_HOST"
echo "  LANGFLOW_PORT=$LANGFLOW_PORT"
echo "  LANGFLOW_LOG_LEVEL=$LANGFLOW_LOG_LEVEL"
echo ""

# Check if langflow is installed
if ! command -v langflow &> /dev/null; then
    echo "Error: Langflow is not installed"
    echo "Please install it with: pip install langflow"
    exit 1
fi

# Check Langflow version
LANGFLOW_VERSION=$(langflow --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1)
echo "Langflow version: $LANGFLOW_VERSION"
echo ""

# Start Langflow
echo "Starting Langflow..."
echo "Access the UI at: http://localhost:$LANGFLOW_PORT"
echo ""
echo "Press Ctrl+C to stop"
echo "================================================"
echo ""

# Start Langflow with the custom components path
langflow run --host "$LANGFLOW_HOST" --port "$LANGFLOW_PORT" --log-level "$LANGFLOW_LOG_LEVEL"

# Made with Bob