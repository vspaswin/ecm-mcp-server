"""Folder management tools for ECM"""

import logging
from typing import Dict, Any, Optional, List

from mcp.server.fastmcp import FastMCP

from client.ecm_client import ECMClient

logger = logging.getLogger(__name__)


def register_folder_tools(mcp: FastMCP, client: ECMClient) -> None:
    """
    Register folder management tools.
    
    Args:
        mcp: FastMCP server instance
        client: ECM API client
    """
    
    @mcp.tool()
    async def ecm_create_folder(
        name: str,
        parent_folder_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new folder in the ECM system.
        
        Args:
            name: Folder name
            parent_folder_id: Optional parent folder ID (None for root)
            description: Optional folder description
        
        Returns:
            Created folder information
        """
        logger.info(f"Creating folder: {name}")
        
        payload = {"name": name}
        if parent_folder_id:
            payload["parentId"] = parent_folder_id
        if description:
            payload["description"] = description
        
        result = await client.post("/folders", json=payload)
        
        logger.info(f"Folder created: {result.get('id')}")
        return result
    
    @mcp.tool()
    async def ecm_list_folder_contents(
        folder_id: str,
        include_documents: bool = True,
        include_subfolders: bool = True
    ) -> Dict[str, Any]:
        """
        List contents of a folder.
        
        Args:
            folder_id: Folder ID
            include_documents: Include documents in results (default: True)
            include_subfolders: Include subfolders in results (default: True)
        
        Returns:
            Folder contents (documents and subfolders)
        """
        logger.info(f"Listing folder contents: {folder_id}")
        
        params = {
            "includeDocuments": str(include_documents).lower(),
            "includeSubfolders": str(include_subfolders).lower()
        }
        
        result = await client.get(f"/folders/{folder_id}/contents", params=params)
        
        doc_count = len(result.get('documents', []))
        folder_count = len(result.get('folders', []))
        logger.info(f"Folder contains {doc_count} documents and {folder_count} subfolders")
        
        return result
    
    @mcp.tool()
    async def ecm_move_document(
        document_id: str,
        target_folder_id: str
    ) -> Dict[str, Any]:
        """
        Move a document to a different folder.
        
        Args:
            document_id: Document ID to move
            target_folder_id: Target folder ID
        
        Returns:
            Move operation result
        """
        logger.info(f"Moving document {document_id} to folder {target_folder_id}")
        
        payload = {"folderId": target_folder_id}
        result = await client.post(
            f"/documents/{document_id}/move",
            json=payload
        )
        
        logger.info(f"Document moved successfully")
        return result
    
    @mcp.tool()
    async def ecm_get_folder_tree(
        folder_id: Optional[str] = None,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Get hierarchical folder structure.
        
        Args:
            folder_id: Root folder ID (None for repository root)
            max_depth: Maximum depth to traverse (default: 3)
        
        Returns:
            Hierarchical folder tree
        """
        logger.info(f"Getting folder tree (max depth: {max_depth})")
        
        endpoint = "/folders/tree"
        params = {"maxDepth": max_depth}
        
        if folder_id:
            params["folderId"] = folder_id
        
        result = await client.get(endpoint, params=params)
        
        logger.info("Folder tree retrieved")
        return result
    
    @mcp.tool()
    async def ecm_delete_folder(
        folder_id: str,
        recursive: bool = False
    ) -> Dict[str, str]:
        """
        Delete a folder.
        
        Args:
            folder_id: Folder ID to delete
            recursive: Delete folder and all contents (default: False)
        
        Returns:
            Deletion confirmation
        """
        logger.info(f"Deleting folder: {folder_id} (recursive={recursive})")
        
        params = {"recursive": str(recursive).lower()}
        result = await client.delete(f"/folders/{folder_id}", params=params)
        
        logger.info(f"Folder deleted: {folder_id}")
        return result
    
    logger.info("Folder tools registered")
