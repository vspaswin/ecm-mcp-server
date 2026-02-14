#!/usr/bin/env python3
"""
ECM MCP Server - Entry Point

This is the main entry point for the ECM MCP server.
It initializes the server and starts listening for MCP protocol messages.
"""

import asyncio
import sys
from pathlib import Path

from server import create_ecm_server
from utils.config import load_config
from utils.logger import setup_logging


def main():
    """
    Main entry point for the ECM MCP server.
    """
    # Setup logging
    logger = setup_logging()
    logger.info("Starting ECM MCP Server...")
    
    try:
        # Load configuration
        config = load_config()
        logger.info(f"Configuration loaded successfully")
        logger.info(f"ECM Base URL: {config.ecm.base_url}")
        logger.info(f"Auth Type: {config.ecm.auth_type}")
        
        # Create and run the server
        server = create_ecm_server(config)
        
        logger.info("ECM MCP Server started successfully")
        logger.info("Listening for MCP protocol messages on stdio...")
        
        # Run the server with stdio transport
        server.run(transport="stdio")
        
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        logger.error("Please create config/config.yaml from config.example.yaml")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
