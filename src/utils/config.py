"""Configuration management for ECM MCP Server"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class OAuthConfig(BaseModel):
    """OAuth 2.0 authentication configuration"""
    client_id: str
    client_secret: str
    token_url: str
    scopes: List[str] = Field(default_factory=list)
    refresh_token: Optional[str] = None


class APIKeyConfig(BaseModel):
    """API Key authentication configuration"""
    header_name: str = "X-API-Key"
    key: str


class BasicAuthConfig(BaseModel):
    """Basic authentication configuration"""
    username: str
    password: str


class ECMConfig(BaseModel):
    """ECM system configuration"""
    base_url: str
    auth_type: str = "oauth2"  # oauth2, api_key, basic
    oauth: Optional[OAuthConfig] = None
    api_key: Optional[APIKeyConfig] = None
    basic: Optional[BasicAuthConfig] = None
    timeout: int = 30
    retry_attempts: int = 3
    retry_backoff: int = 2
    rate_limit: int = 100
    headers: Dict[str, str] = Field(default_factory=dict)


class ServerConfig(BaseModel):
    """Server configuration"""
    name: str = "ecm-mcp-server"
    version: str = "1.0.0"
    log_level: str = "INFO"


class FeaturesConfig(BaseModel):
    """Feature flags configuration"""
    enable_caching: bool = True
    cache_ttl: int = 300
    cache_max_size: int = 1000
    enable_audit_log: bool = True
    audit_log_path: str = "logs/audit.log"
    enable_metrics: bool = False


class ToolsConfig(BaseModel):
    """Tool-specific configuration"""
    search: Dict[str, Any] = Field(default_factory=lambda: {"max_results": 100, "default_page_size": 20})
    documents: Dict[str, Any] = Field(default_factory=dict)
    folders: Dict[str, Any] = Field(default_factory=lambda: {"max_depth": 10})


class Config(BaseModel):
    """Main configuration model"""
    ecm: ECMConfig
    server: ServerConfig = Field(default_factory=ServerConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Optional path to config file. If not provided,
                    looks for config.yaml in config/ directory or
                    path specified in ECM_CONFIG_PATH env var.
    
    Returns:
        Parsed configuration object
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    # Determine config file path
    if config_path is None:
        config_path = os.getenv("ECM_CONFIG_PATH")
    
    if config_path is None:
        # Default to config/config.yaml
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Please create config/config.yaml from config/config.example.yaml"
        )
    
    # Load YAML
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    
    # Parse and validate
    try:
        config = Config(**config_data)
        return config
    except Exception as e:
        raise ValueError(f"Invalid configuration: {e}")
