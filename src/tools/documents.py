"""Document management tools for ECM"""

import logging
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP

from client.ecm_client import ECMClient

logger = logging.getLogger(__name__)


def register_document_tools(mcp: FastMCP, client: ECMClient) -> None:
    """
    Register document management tools.
    
    Args:
        mcp: FastMCP server instance
        client: ECM API client
    """
    
    @mcp.tool()
    async def ecm_create_document(
        title: str,
        content: str,
        folder_id: Optional[str] = None,
        mime_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new document in the ECM system.
        
        Args:
            title: Document title
            content: Document content (text or base64 encoded binary)
            folder_id: Optional folder ID to create document in
            mime_type: MIME type of the document (default: text/plain)
            metadata: Optional metadata key-value pairs
        
        Returns:
            Created document information including document ID
        """
        logger.info(f"Creating document: {title}")
        
        payload = {
            "title": title,
            "content": content,
            "mimeType": mime_type,
        }
        
        if folder_id:
            payload["folderId"] = folder_id
        
        if metadata:
            payload["metadata"] = metadata
        
        result = await client.post("/documents", json=payload)
        
        logger.info(f"Document created: {result.get('id')}")
        return result
    
    @mcp.tool()
    async def ecm_get_document(document_id: str) -> Dict[str, Any]:
        """
        Retrieve a document by ID.
        
        Args:
            document_id: Document ID
        
        Returns:
            Document information and metadata
        """
        logger.info(f"Getting document: {document_id}")
        result = await client.get(f"/documents/{document_id}")
        return result
    
    @mcp.tool()
    async def ecm_update_document(
        document_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing document.
        
        Args:
            document_id: Document ID
            title: New title (optional)
            content: New content (optional)
            metadata: Metadata updates (optional)
        
        Returns:
            Updated document information
        """
        logger.info(f"Updating document: {document_id}")
        
        payload = {}
        if title:
            payload["title"] = title
        if content:
            payload["content"] = content
        if metadata:
            payload["metadata"] = metadata
        
        result = await client.patch(f"/documents/{document_id}", json=payload)
        
        logger.info(f"Document updated: {document_id}")
        return result
    
    @mcp.tool()
    async def ecm_delete_document(document_id: str) -> Dict[str, str]:
        """
        Delete a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            Deletion confirmation
        """
        logger.info(f"Deleting document: {document_id}")
        result = await client.delete(f"/documents/{document_id}")
        logger.info(f"Document deleted: {document_id}")
        return result
    
    @mcp.tool()
    async def ecm_download_document(document_id: str) -> Dict[str, Any]:
        """
        Download document content.
        
        Args:
            document_id: Document ID
        
        Returns:
            Document content and metadata
        """
        logger.info(f"Downloading document: {document_id}")
        result = await client.get(f"/documents/{document_id}/content")
        return result
    
    @mcp.tool()
    async def ecm_upload_document(
        document_id: str,
        content: str,
        create_version: bool = True
    ) -> Dict[str, Any]:
        """
        Upload new content to an existing document.
        
        Args:
            document_id: Document ID
            content: New document content (base64 encoded for binary)
            create_version: Whether to create a new version (default: True)
        
        Returns:
            Upload result
        """
        logger.info(f"Uploading content to document: {document_id}")
        
        payload = {
            "content": content,
            "createVersion": create_version
        }
        
        result = await client.post(
            f"/documents/{document_id}/content",
            json=payload
        )
        
        logger.info(f"Content uploaded to document: {document_id}")
        return result
    
    logger.info("Document tools registered")
