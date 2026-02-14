"""Metadata management tools for ECM"""

import logging
from typing import Dict, Any, List

from mcp.server.fastmcp import FastMCP

from client.ecm_client import ECMClient

logger = logging.getLogger(__name__)


def register_metadata_tools(mcp: FastMCP, client: ECMClient) -> None:
    """
    Register metadata management tools.
    
    Args:
        mcp: FastMCP server instance
        client: ECM API client
    """
    
    @mcp.tool()
    async def ecm_get_metadata(document_id: str) -> Dict[str, Any]:
        """
        Get metadata for a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            Document metadata
        """
        logger.info(f"Getting metadata for document: {document_id}")
        result = await client.get(f"/documents/{document_id}/metadata")
        return result
    
    @mcp.tool()
    async def ecm_update_metadata(
        document_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update metadata for a document.
        
        Args:
            document_id: Document ID
            metadata: Metadata key-value pairs to update
        
        Returns:
            Updated metadata
        """
        logger.info(f"Updating metadata for document: {document_id}")
        
        result = await client.patch(
            f"/documents/{document_id}/metadata",
            json=metadata
        )
        
        logger.info(f"Metadata updated for document: {document_id}")
        return result
    
    @mcp.tool()
    async def ecm_get_metadata_schema(
        document_type: str = "default"
    ) -> Dict[str, Any]:
        """
        Get available metadata schema/fields for a document type.
        
        Args:
            document_type: Document type (default: "default")
        
        Returns:
            Metadata schema definition
        """
        logger.info(f"Getting metadata schema for type: {document_type}")
        
        result = await client.get(
            f"/metadata/schemas/{document_type}"
        )
        
        return result
    
    logger.info("Metadata tools registered")
