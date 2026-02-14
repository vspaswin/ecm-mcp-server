"""Main MCP server entry point for ECM integration"""

import asyncio
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from client.ecm_client import ECMClient
from config.settings import get_settings
from tools.documents import register_document_tools
from tools.search import register_search_tools
from tools.folders import register_folder_tools
from tools.metadata import register_metadata_tools
from tools.versions import register_version_tools
from tools.workflows import register_workflow_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("ecm-server")

# Global client instance
ecm_client: ECMClient = None


@mcp.tool()
async def ecm_health_check() -> dict:
    """
    Check health status of the ECM API connection.
    
    Returns:
        Health status including API connectivity and configuration
    """
    logger.info("Performing health check")
    
    try:
        settings = get_settings()
        
        # Test API connectivity
        response = await ecm_client.get("/health")
        
        return {
            "status": "healthy",
            "api_url": settings.ecm_api_url,
            "api_response": response,
            "authenticated": ecm_client.is_authenticated()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@mcp.tool()
async def ecm_get_api_info() -> dict:
    """
    Get information about available ECM API endpoints and capabilities.
    
    Returns:
        API information including version and available endpoints
    """
    logger.info("Getting API information")
    
    try:
        response = await ecm_client.get("/api/info")
        return response
    except Exception as e:
        logger.error(f"Failed to get API info: {e}")
        return {
            "error": str(e),
            "message": "Could not retrieve API information"
        }


async def initialize_server():
    """
    Initialize the MCP server and register all tools.
    """
    global ecm_client
    
    logger.info("Initializing ECM MCP Server")
    
    # Load settings
    settings = get_settings()
    logger.info(f"Loaded configuration for API: {settings.ecm_api_url}")
    
    # Initialize ECM client
    ecm_client = ECMClient(
        base_url=settings.ecm_api_url,
        username=settings.ecm_username,
        password=settings.ecm_password,
        timeout=settings.request_timeout
    )
    
    # Authenticate
    try:
        await ecm_client.authenticate()
        logger.info("Successfully authenticated with ECM API")
    except Exception as e:
        logger.error(f"Failed to authenticate: {e}")
        raise
    
    # Register all tool groups
    logger.info("Registering tool groups...")
    register_document_tools(mcp, ecm_client)
    register_search_tools(mcp, ecm_client)
    register_folder_tools(mcp, ecm_client)
    register_metadata_tools(mcp, ecm_client)
    register_version_tools(mcp, ecm_client)
    register_workflow_tools(mcp, ecm_client)
    
    logger.info("ECM MCP Server initialization complete")


async def cleanup():
    """
    Cleanup resources on server shutdown.
    """
    global ecm_client
    
    logger.info("Shutting down ECM MCP Server")
    
    if ecm_client:
        await ecm_client.close()
        logger.info("ECM client closed")


def main():
    """
    Main entry point for the MCP server.
    """
    import sys
    
    try:
        # Initialize and run server
        asyncio.run(initialize_server())
        
        # Run the MCP server
        mcp.run(transport='stdio')
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        asyncio.run(cleanup())


if __name__ == "__main__":
    main()
