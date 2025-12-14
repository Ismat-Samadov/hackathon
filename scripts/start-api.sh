#!/bin/bash
# Start SOCAR API on port 9000 with nginx reverse proxy

PORT=${1:-9000}
HOST=${2:-0.0.0.0}

echo "🚀 Starting SOCAR API..."
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Public: http://beatbyteai-vm-ip.polandcentral.cloudapp.azure.com"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")/.."
uv run python main.py --host "$HOST" --port "$PORT"
