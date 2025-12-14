#!/bin/bash
# Docker deployment script for SOCAR API

set -e

COMPOSE_FILE="docker-compose.yml"
SERVICE_NAME="socar-api"

echo "🐳 SOCAR API Docker Deployment"
echo "================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please create a .env file with required environment variables."
    echo "   See .env.example for reference."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Parse command line arguments
case "${1:-up}" in
    build)
        echo "🔨 Building Docker image..."
        docker compose build
        ;;
    
    up)
        echo "🚀 Starting SOCAR API service..."
        docker compose up -d
        echo ""
        echo "✅ Service started successfully!"
        echo ""
        echo "📊 Service status:"
        docker compose ps
        echo ""
        echo "🌐 API available at: http://localhost:9000"
        echo "📖 API documentation: http://localhost:9000/docs"
        echo ""
        echo "📋 Useful commands:"
        echo "   View logs:       docker compose logs -f $SERVICE_NAME"
        echo "   Stop service:    docker compose down"
        echo "   Restart:         docker compose restart"
        echo "   Rebuild:         docker compose up -d --build"
        ;;
    
    down)
        echo "⏹️  Stopping SOCAR API service..."
        docker compose down
        echo "✅ Service stopped"
        ;;
    
    restart)
        echo "🔄 Restarting SOCAR API service..."
        docker compose restart
        echo "✅ Service restarted"
        ;;
    
    logs)
        echo "📋 Showing service logs (Ctrl+C to exit)..."
        docker compose logs -f $SERVICE_NAME
        ;;
    
    status)
        echo "📊 Service status:"
        docker compose ps
        ;;
    
    shell)
        echo "🐚 Opening shell in container..."
        docker compose exec $SERVICE_NAME /bin/bash
        ;;
    
    rebuild)
        echo "🔨 Rebuilding and restarting service..."
        docker compose down
        docker compose build
        docker compose up -d
        echo "✅ Service rebuilt and started"
        ;;
    
    clean)
        echo "🧹 Cleaning up Docker resources..."
        docker compose down -v
        docker system prune -f
        echo "✅ Cleanup complete"
        ;;
    
    *)
        echo "Usage: $0 {build|up|down|restart|logs|status|shell|rebuild|clean}"
        echo ""
        echo "Commands:"
        echo "  build    - Build Docker image"
        echo "  up       - Start service (default)"
        echo "  down     - Stop service"
        echo "  restart  - Restart service"
        echo "  logs     - Show service logs"
        echo "  status   - Show service status"
        echo "  shell    - Open shell in container"
        echo "  rebuild  - Rebuild and restart service"
        echo "  clean    - Clean up Docker resources"
        exit 1
        ;;
esac
