"""Version control tools for ECM"""

import logging
from typing import Dict, Any, List

from mcp.server.fastmcp import FastMCP

from client.ecm_client import ECMClient

logger = logging.getLogger(__name__)


def register_version_tools(mcp: FastMCP, client: ECMClient) -> None:
    """
    Register version control tools.
    
    Args:
        mcp: FastMCP server instance
        client: ECM API client
    """
    
    @mcp.tool()
    async def ecm_get_versions(document_id: str) -> Dict[str, Any]:
        """
        Get version history for a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            List of document versions
        """
        logger.info(f"Getting version history for document: {document_id}")
        result = await client.get(f"/documents/{document_id}/versions")
        return result
    
    @mcp.tool()
    async def ecm_create_version(
        document_id: str,
        comment: str = "",
        major: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new version of a document.
        
        Args:
            document_id: Document ID
            comment: Version comment/description
            major: Create major version (default: False for minor version)
        
        Returns:
            New version information
        """
        logger.info(f"Creating new version for document: {document_id}")
        
        payload = {
            "comment": comment,
            "major": major
        }
        
        result = await client.post(
            f"/documents/{document_id}/versions",
            json=payload
        )
        
        logger.info(f"New version created: {result.get('version')}")
        return result
    
    @mcp.tool()
    async def ecm_restore_version(
        document_id: str,
        version_id: str
    ) -> Dict[str, Any]:
        """
        Restore a document to a previous version.
        
        Args:
            document_id: Document ID
            version_id: Version ID to restore
        
        Returns:
            Restoration result
        """
        logger.info(f"Restoring document {document_id} to version {version_id}")
        
        payload = {"versionId": version_id}
        result = await client.post(
            f"/documents/{document_id}/restore",
            json=payload
        )
        
        logger.info(f"Document restored to version {version_id}")
        return result
    
    logger.info("Version tools registered")
