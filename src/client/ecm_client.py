"""ECM REST API Client Implementation"""

import logging
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx

from utils.config import Config
from .auth import create_auth_handler, AuthHandler
from .exceptions import (
    ECMClientError,
    ECMAuthenticationError,
    ECMNotFoundError,
    ECMPermissionError,
    ECMRateLimitError,
    ECMTimeoutError,
)

logger = logging.getLogger(__name__)


class ECMClient:
    """
    REST API client for ECM systems.
    
    Provides methods for interacting with ECM REST APIs including:
    - Document operations (CRUD)
    - Search and discovery
    - Folder management
    - Metadata operations
    - Version control
    - Workflow management
    """
    
    def __init__(self, config: Config):
        """
        Initialize ECM client.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.base_url = config.ecm.base_url
        self.timeout = config.ecm.timeout
        self.retry_attempts = config.ecm.retry_attempts
        self.retry_backoff = config.ecm.retry_backoff
        
        # Initialize authentication
        self.auth_handler = create_auth_handler(config)
        
        # Rate limiting
        self.rate_limit = config.ecm.rate_limit
        self._request_times: List[float] = []
        
        # HTTP client
        self._client: Optional[httpx.AsyncClient] = None
        
        logger.info(f"ECM client initialized for {self.base_url}")
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client"""
        if self._client is None:
            # Prepare headers
            headers = {
                **self.config.ecm.headers,
            }
            
            # Create client
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout,
                follow_redirects=True,
            )
        
        return self._client
    
    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting"""
        current_time = time.time()
        
        # Remove timestamps older than 1 minute
        self._request_times = [
            t for t in self._request_times 
            if current_time - t < 60
        ]
        
        # Check if we've hit the rate limit
        if len(self._request_times) >= self.rate_limit:
            oldest_time = min(self._request_times)
            sleep_time = 60 - (current_time - oldest_time)
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Waiting {sleep_time:.2f}s")
                raise ECMRateLimitError(
                    f"Rate limit of {self.rate_limit} requests/minute exceeded"
                )
        
        # Record this request
        self._request_times.append(current_time)
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request to ECM API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx.request
        
        Returns:
            HTTP response
        
        Raises:
            ECMClientError: On API errors
        """
        # Check rate limit
        await self._check_rate_limit()
        
        # Refresh auth if needed
        await self.auth_handler.refresh_if_needed()
        
        # Get auth headers
        auth_headers = self.auth_handler.get_headers()
        
        # Merge headers
        headers = kwargs.pop("headers", {})
        headers.update(auth_headers)
        
        # Get client
        client = await self._get_client()
        
        # Retry loop
        last_exception = None
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f"{method} {endpoint} (attempt {attempt + 1}/{self.retry_attempts})")
                
                response = await client.request(
                    method=method,
                    url=endpoint,
                    headers=headers,
                    **kwargs
                )
                
                # Handle error responses
                if response.status_code >= 400:
                    self._handle_error_response(response)
                
                return response
                
            except httpx.TimeoutException as e:
                last_exception = ECMTimeoutError(f"Request timeout: {e}")
                if attempt < self.retry_attempts - 1:
                    wait_time = self.retry_backoff ** attempt
                    logger.warning(f"Request timeout. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
            
            except httpx.HTTPError as e:
                last_exception = ECMClientError(f"HTTP error: {e}")
                if attempt < self.retry_attempts - 1:
                    wait_time = self.retry_backoff ** attempt
                    logger.warning(f"HTTP error. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
        
        # All retries failed
        if last_exception:
            raise last_exception
        raise ECMClientError("Request failed after all retries")
    
    def _handle_error_response(self, response: httpx.Response) -> None:
        """
        Handle error HTTP responses.
        
        Args:
            response: HTTP response with error status
        
        Raises:
            Appropriate ECMClientError subclass
        """
        status_code = response.status_code
        try:
            error_body = response.json()
            error_message = error_body.get("error", error_body.get("message", response.text))
        except Exception:
            error_message = response.text
        
        # Map status codes to exceptions
        if status_code == 401:
            raise ECMAuthenticationError(
                f"Authentication failed: {error_message}",
                status_code=status_code,
                response_body=response.text
            )
        elif status_code == 403:
            raise ECMPermissionError(
                f"Permission denied: {error_message}",
                status_code=status_code,
                response_body=response.text
            )
        elif status_code == 404:
            raise ECMNotFoundError(
                f"Resource not found: {error_message}",
                status_code=status_code,
                response_body=response.text
            )
        elif status_code == 429:
            raise ECMRateLimitError(
                f"Rate limit exceeded: {error_message}",
                status_code=status_code,
                response_body=response.text
            )
        else:
            raise ECMClientError(
                f"API error ({status_code}): {error_message}",
                status_code=status_code,
                response_body=response.text
            )
    
    # Convenience methods for common HTTP operations
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        response = await self._request("GET", endpoint, **kwargs)
        return response.json()
    
    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST request"""
        response = await self._request("POST", endpoint, **kwargs)
        return response.json()
    
    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        response = await self._request("PUT", endpoint, **kwargs)
        return response.json()
    
    async def patch(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PATCH request"""
        response = await self._request("PATCH", endpoint, **kwargs)
        return response.json()
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        response = await self._request("DELETE", endpoint, **kwargs)
        if response.status_code == 204:
            return {"status": "deleted"}
        return response.json()
    
    async def close(self) -> None:
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


import asyncio  # Import here to avoid circular dependency
