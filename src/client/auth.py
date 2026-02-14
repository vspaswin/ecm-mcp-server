"""Authentication handlers for ECM API"""

import logging
import time
from typing import Dict, Optional

import httpx
from authlib.integrations.httpx_client import OAuth2Client

from utils.config import Config, OAuthConfig, APIKeyConfig, BasicAuthConfig
from .exceptions import ECMAuthenticationError

logger = logging.getLogger(__name__)


class AuthHandler:
    """Base class for authentication handlers"""
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        raise NotImplementedError
    
    async def refresh_if_needed(self) -> None:
        """Refresh authentication if needed"""
        pass


class OAuth2Handler(AuthHandler):
    """OAuth 2.0 authentication handler"""
    
    def __init__(self, config: OAuthConfig, base_url: str):
        self.config = config
        self.base_url = base_url
        self._token = None
        self._token_expires_at = 0
        self._client = None
    
    async def _fetch_token(self) -> Dict:
        """Fetch new access token"""
        logger.info("Fetching OAuth access token...")
        
        try:
            # Create OAuth2 client
            client = OAuth2Client(
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
            )
            
            # Fetch token
            token = client.fetch_token(
                url=self.config.token_url,
                grant_type="client_credentials",
                scope=" ".join(self.config.scopes) if self.config.scopes else None,
            )
            
            self._token = token["access_token"]
            # Set expiration with 5 minute buffer
            expires_in = token.get("expires_in", 3600)
            self._token_expires_at = time.time() + expires_in - 300
            
            logger.info("OAuth token fetched successfully")
            return token
            
        except Exception as e:
            logger.error(f"Failed to fetch OAuth token: {e}")
            raise ECMAuthenticationError(f"OAuth authentication failed: {e}")
    
    def _is_token_expired(self) -> bool:
        """Check if token is expired or about to expire"""
        return time.time() >= self._token_expires_at
    
    async def refresh_if_needed(self) -> None:
        """Refresh token if expired"""
        if self._token is None or self._is_token_expired():
            await self._fetch_token()
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers with bearer token"""
        if self._token is None:
            raise ECMAuthenticationError("No OAuth token available. Call refresh_if_needed() first.")
        
        return {
            "Authorization": f"Bearer {self._token}"
        }


class APIKeyHandler(AuthHandler):
    """API Key authentication handler"""
    
    def __init__(self, config: APIKeyConfig):
        self.config = config
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers with API key"""
        return {
            self.config.header_name: self.config.key
        }


class BasicAuthHandler(AuthHandler):
    """Basic authentication handler"""
    
    def __init__(self, config: BasicAuthConfig):
        self.config = config
        self._auth = httpx.BasicAuth(config.username, config.password)
    
    def get_auth(self) -> httpx.BasicAuth:
        """Get BasicAuth object for httpx"""
        return self._auth
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        # Basic auth is handled by httpx auth parameter
        return {}


def create_auth_handler(config: Config) -> AuthHandler:
    """
    Create appropriate authentication handler based on configuration.
    
    Args:
        config: ECM configuration
    
    Returns:
        Authentication handler instance
    
    Raises:
        ValueError: If auth type is invalid or config is missing
    """
    auth_type = config.ecm.auth_type.lower()
    
    if auth_type == "oauth2":
        if not config.ecm.oauth:
            raise ValueError("OAuth configuration is required for oauth2 auth type")
        return OAuth2Handler(config.ecm.oauth, config.ecm.base_url)
    
    elif auth_type == "api_key":
        if not config.ecm.api_key:
            raise ValueError("API key configuration is required for api_key auth type")
        return APIKeyHandler(config.ecm.api_key)
    
    elif auth_type == "basic":
        if not config.ecm.basic:
            raise ValueError("Basic auth configuration is required for basic auth type")
        return BasicAuthHandler(config.ecm.basic)
    
    else:
        raise ValueError(
            f"Invalid auth type: {auth_type}. "
            "Supported types: oauth2, api_key, basic"
        )
