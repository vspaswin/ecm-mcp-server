"""Search and discovery tools for ECM"""

import logging
from typing import Dict, Any, List, Optional

from mcp.server.fastmcp import FastMCP

from client.ecm_client import ECMClient

logger = logging.getLogger(__name__)


def register_search_tools(mcp: FastMCP, client: ECMClient) -> None:
    """
    Register search and discovery tools.
    
    Args:
        mcp: FastMCP server instance
        client: ECM API client
    """
    
    @mcp.tool()
    async def ecm_search_documents(
        query: str,
        max_results: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for documents using a text query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 20)
            offset: Offset for pagination (default: 0)
        
        Returns:
            Search results with document list and pagination info
        """
        logger.info(f"Searching documents: {query}")
        
        params = {
            "q": query,
            "limit": max_results,
            "offset": offset
        }
        
        result = await client.get("/search", params=params)
        
        logger.info(f"Search returned {len(result.get('documents', []))} results")
        return result
    
    @mcp.tool()
    async def ecm_advanced_search(
        query: Optional[str] = None,
        folder_id: Optional[str] = None,
        mime_types: Optional[List[str]] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        modified_after: Optional[str] = None,
        modified_before: Optional[str] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        max_results: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Advanced search with multiple filter criteria.
        
        Args:
            query: Optional text query
            folder_id: Filter by folder
            mime_types: Filter by MIME types (e.g., ['application/pdf'])
            created_after: Filter by creation date (ISO 8601 format)
            created_before: Filter by creation date (ISO 8601 format)
            modified_after: Filter by modification date (ISO 8601 format)
            modified_before: Filter by modification date (ISO 8601 format)
            metadata_filters: Filter by metadata key-value pairs
            max_results: Maximum number of results (default: 20)
            offset: Offset for pagination (default: 0)
        
        Returns:
            Search results with document list and pagination info
        """
        logger.info("Executing advanced search")
        
        payload = {
            "limit": max_results,
            "offset": offset
        }
        
        if query:
            payload["query"] = query
        if folder_id:
            payload["folderId"] = folder_id
        if mime_types:
            payload["mimeTypes"] = mime_types
        if created_after:
            payload["createdAfter"] = created_after
        if created_before:
            payload["createdBefore"] = created_before
        if modified_after:
            payload["modifiedAfter"] = modified_after
        if modified_before:
            payload["modifiedBefore"] = modified_before
        if metadata_filters:
            payload["metadata"] = metadata_filters
        
        result = await client.post("/search/advanced", json=payload)
        
        logger.info(f"Advanced search returned {len(result.get('documents', []))} results")
        return result
    
    @mcp.tool()
    async def ecm_get_recent_documents(
        limit: int = 10,
        folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get recently modified documents.
        
        Args:
            limit: Maximum number of documents to return (default: 10)
            folder_id: Optional folder to filter by
        
        Returns:
            List of recently modified documents
        """
        logger.info(f"Getting {limit} recent documents")
        
        params = {
            "limit": limit,
            "sortBy": "modifiedDate",
            "sortOrder": "desc"
        }
        
        if folder_id:
            params["folderId"] = folder_id
        
        result = await client.get("/documents/recent", params=params)
        
        logger.info(f"Retrieved {len(result.get('documents', []))} recent documents")
        return result
    
    logger.info("Search tools registered")
