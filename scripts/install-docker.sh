#!/bin/bash
# Install Docker and Docker Compose on Ubuntu/Debian Linux

set -e

echo "🐳 Docker Installation Script"
echo "=============================="
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is designed for Linux systems only."
    echo "   For other OS, please visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Please run this script as your regular user (not root)."
    echo "   The script will use sudo when needed."
    exit 1
fi

# Check if Docker is already installed
if command -v docker &> /dev/null; then
    echo "✅ Docker is already installed!"
    docker --version
    echo ""
    read -p "Reinstall Docker? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping Docker installation."
        exit 0
    fi
fi

echo "📦 Installing Docker..."
echo ""

# Remove old versions if they exist
echo "🧹 Removing old Docker versions (if any)..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Update package index
echo "📥 Updating package index..."
sudo apt-get update

# Install prerequisites
echo "📦 Installing prerequisites..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
echo "🔑 Adding Docker GPG key..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo "📋 Setting up Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
echo "📥 Updating package index with Docker repository..."
sudo apt-get update

# Install Docker Engine
echo "🐳 Installing Docker Engine..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker service
echo "🚀 Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Add current user to docker group
echo "👤 Adding user to docker group..."
sudo usermod -aG docker $USER

# Verify installation
echo ""
echo "✅ Docker installation complete!"
echo ""
echo "📊 Installed versions:"
docker --version
docker compose version

echo ""
echo "⚠️  IMPORTANT: Log out and log back in for group changes to take effect!"
echo ""
echo "After logging back in, verify Docker works without sudo:"
echo "  docker run hello-world"
echo ""
echo "🎉 Installation successful!"
echo ""
echo "📚 Useful Docker commands:"
echo "  docker ps                    # List running containers"
echo "  docker images                # List images"
echo "  docker compose up -d         # Start services in background"
echo "  docker compose down          # Stop services"
echo "  docker compose logs -f       # View logs"
echo "  docker system prune          # Clean up unused resources"
echo ""
echo "📖 For more info: https://docs.docker.com/"
