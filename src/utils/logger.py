"""Logging configuration for ECM MCP Server"""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

import yaml


def setup_logging(config_path: Optional[str] = None, log_level: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        config_path: Optional path to logging config YAML file
        log_level: Optional log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Root logger instance
    """
    # Determine config file path
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "logging.yaml"
    else:
        config_path = Path(config_path)
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Load logging configuration if file exists
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config_dict = yaml.safe_load(f)
            logging.config.dictConfig(config_dict)
        except Exception as e:
            # Fallback to basic config if loading fails
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            logging.warning(f"Failed to load logging config from {config_path}: {e}")
    else:
        # Basic configuration if no config file
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    
    # Override log level if specified
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
        logging.getLogger().setLevel(level)
    
    # Get logger
    logger = logging.getLogger("ecm-mcp-server")
    
    return logger


def get_audit_logger() -> logging.Logger:
    """
    Get the audit logger for tracking operations.
    
    Returns:
        Audit logger instance
    """
    return logging.getLogger("audit")
