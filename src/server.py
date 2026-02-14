"""ECM MCP Server Implementation"""

import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from client.ecm_client import ECMClient
from tools import (
    register_document_tools,
    register_search_tools,
    register_folder_tools,
    register_metadata_tools,
    register_version_tools,
    register_workflow_tools,
)
from resources import register_ecm_resources
from utils.config import Config

logger = logging.getLogger(__name__)


def create_ecm_server(config: Config) -> FastMCP:
    """
    Create and configure the ECM MCP server.
    
    Args:
        config: Server configuration
        
    Returns:
        Configured FastMCP server instance
    """
    # Initialize FastMCP server
    mcp = FastMCP(
        name=config.server.name,
        version=config.server.version,
    )
    
    # Initialize ECM client
    ecm_client = ECMClient(config)
    
    # Store client in server context for tools to access
    mcp.dependencies = {"ecm_client": ecm_client, "config": config}
    
    # Register all tool categories
    logger.info("Registering document tools...")
    register_document_tools(mcp, ecm_client)
    
    logger.info("Registering search tools...")
    register_search_tools(mcp, ecm_client)
    
    logger.info("Registering folder tools...")
    register_folder_tools(mcp, ecm_client)
    
    logger.info("Registering metadata tools...")
    register_metadata_tools(mcp, ecm_client)
    
    logger.info("Registering version tools...")
    register_version_tools(mcp, ecm_client)
    
    logger.info("Registering workflow tools...")
    register_workflow_tools(mcp, ecm_client)
    
    # Register resources
    logger.info("Registering ECM resources...")
    register_ecm_resources(mcp, ecm_client)
    
    logger.info(f"Server initialized with {len(mcp._tools)} tools")
    
    return mcp
