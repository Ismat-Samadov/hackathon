#!/usr/bin/env python3
"""
SOCAR Historical Document Processing System - Main Entry Point.

This script starts the FastAPI server for the document processing system.
It supports both local development and production deployment.

Usage:
    python main.py                    # Start with default settings
    python main.py --host 0.0.0.0     # Bind to all interfaces
    python main.py --port 8080        # Use custom port
    python main.py --reload           # Enable auto-reload for development
"""

import argparse
import sys
import logging

import uvicorn

from src.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="server.log",
    
)
logger = logging.getLogger(__name__)


def print_startup_banner(host: str, port: int) -> None:
    """
    Print ASCII banner with server startup information.

    Args:
        host: Server host address
        port: Server port number
    """
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║         SOCAR Historical Document Processing API             ║
╠══════════════════════════════════════════════════════════════╣
║  Version:    1.0.0                                           ║
║  OCR Model:    {settings.OCR_MODEL:<43} ║
║  Chat Model:   {settings.CHAT_MODEL:<43} ║
║  Embedding:    {settings.EMBEDDING_MODEL:<43} ║
╠══════════════════════════════════════════════════════════════╣
║  Server:       http://{host}:{port:<37} ║
║  Swagger UI:   http://{host}:{port}/docs{' ':<29} ║
║  ReDoc:        http://{host}:{port}/redoc{' ':<28} ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main() -> None:
    """
    Main entry point for the API server.

    Parses command-line arguments and starts the Uvicorn server.
    """
    parser = argparse.ArgumentParser(
        description="SOCAR Document Processing API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                         # Start with defaults
  python main.py --host 0.0.0.0          # Listen on all interfaces
  python main.py --port 8080             # Use custom port
  python main.py --reload                # Enable auto-reload
        """
    )

    parser.add_argument(
        "--host",
        default=settings.API_HOST,
        help=f"Host to bind (default: {settings.API_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.API_PORT,
        help=f"Port to bind (default: {settings.API_PORT})"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes (development only)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (production)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.port < 1 or args.port > 65535:
        logger.error("Port must be between 1 and 65535")
        sys.exit(1)

    if args.workers < 1:
        logger.error("Workers must be at least 1")
        sys.exit(1)

    # Print startup information
    print_startup_banner(args.host, args.port)

    try:
        # Start the server
        uvicorn.run(
            "src.api:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=1 if args.reload else args.workers,
            log_level="info",
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
