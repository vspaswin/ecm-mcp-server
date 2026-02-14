"""MCP Tools for ECM operations"""

from .documents import register_document_tools
from .search import register_search_tools
from .folders import register_folder_tools
from .metadata import register_metadata_tools
from .versions import register_version_tools
from .workflows import register_workflow_tools

__all__ = [
    "register_document_tools",
    "register_search_tools",
    "register_folder_tools",
    "register_metadata_tools",
    "register_version_tools",
    "register_workflow_tools",
]
