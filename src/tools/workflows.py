"""Workflow management tools for ECM"""

import logging
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP

from client.ecm_client import ECMClient

logger = logging.getLogger(__name__)


def register_workflow_tools(mcp: FastMCP, client: ECMClient) -> None:
    """
    Register workflow management tools.
    
    Args:
        mcp: FastMCP server instance
        client: ECM API client
    """
    
    @mcp.tool()
    async def ecm_start_workflow(
        document_id: str,
        workflow_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a workflow on a document.
        
        Args:
            document_id: Document ID
            workflow_name: Workflow type/name to start
            parameters: Optional workflow parameters
        
        Returns:
            Workflow instance information
        """
        logger.info(f"Starting workflow '{workflow_name}' on document {document_id}")
        
        payload = {
            "workflowName": workflow_name,
            "documentId": document_id
        }
        
        if parameters:
            payload["parameters"] = parameters
        
        result = await client.post("/workflows", json=payload)
        
        logger.info(f"Workflow started: {result.get('workflowId')}")
        return result
    
    @mcp.tool()
    async def ecm_get_workflow_status(workflow_id: str) -> Dict[str, Any]:
        """
        Get status of a workflow instance.
        
        Args:
            workflow_id: Workflow instance ID
        
        Returns:
            Workflow status and details
        """
        logger.info(f"Getting workflow status: {workflow_id}")
        result = await client.get(f"/workflows/{workflow_id}")
        return result
    
    @mcp.tool()
    async def ecm_approve_workflow(
        workflow_id: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve a workflow step.
        
        Args:
            workflow_id: Workflow instance ID
            comment: Optional approval comment
        
        Returns:
            Workflow approval result
        """
        logger.info(f"Approving workflow: {workflow_id}")
        
        payload = {"action": "approve"}
        if comment:
            payload["comment"] = comment
        
        result = await client.post(
            f"/workflows/{workflow_id}/action",
            json=payload
        )
        
        logger.info(f"Workflow approved: {workflow_id}")
        return result
    
    @mcp.tool()
    async def ecm_reject_workflow(
        workflow_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Reject a workflow step.
        
        Args:
            workflow_id: Workflow instance ID
            reason: Rejection reason
        
        Returns:
            Workflow rejection result
        """
        logger.info(f"Rejecting workflow: {workflow_id}")
        
        payload = {
            "action": "reject",
            "reason": reason
        }
        
        result = await client.post(
            f"/workflows/{workflow_id}/action",
            json=payload
        )
        
        logger.info(f"Workflow rejected: {workflow_id}")
        return result
    
    logger.info("Workflow tools registered")
