#!/bin/bash
# Setup systemd service for SOCAR API

set -e

SERVICE_NAME="socar-api"
SERVICE_FILE="socar-api.service"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SYSTEMD_DIR="/etc/systemd/system"

echo "🔧 Setting up SOCAR API systemd service..."
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Please run this script as your regular user (with sudo privileges)"
    echo "   Usage: ./scripts/setup-service.sh"
    exit 1
fi

# Check if service file exists
if [ ! -f "$PROJECT_DIR/$SERVICE_FILE" ]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

# Copy service file to systemd directory
echo "📝 Installing service file..."
sudo cp "$PROJECT_DIR/$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME.service"

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable service to start on boot
echo "✅ Enabling service to start on boot..."
sudo systemctl enable "$SERVICE_NAME"

# Start the service
echo "🚀 Starting service..."
sudo systemctl start "$SERVICE_NAME"

# Wait a moment for the service to start
sleep 2

# Check service status
echo ""
echo "📊 Service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "✨ Setup complete!"
echo ""
echo "📋 Useful commands:"
echo "   Check status:    sudo systemctl status $SERVICE_NAME"
echo "   Start service:   sudo systemctl start $SERVICE_NAME"
echo "   Stop service:    sudo systemctl stop $SERVICE_NAME"
echo "   Restart service: sudo systemctl restart $SERVICE_NAME"
echo "   View logs:       sudo journalctl -u $SERVICE_NAME -f"
echo "   Disable service: sudo systemctl disable $SERVICE_NAME"
echo ""
echo "📁 Log files:"
echo "   Output: $PROJECT_DIR/logs/api_service.log"
echo "   Errors: $PROJECT_DIR/logs/api_service_error.log"
