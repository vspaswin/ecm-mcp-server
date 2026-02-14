"""Caching utilities for ECM MCP Server"""

import functools
import time
from typing import Any, Callable, Dict, Optional, Tuple

from cachetools import TTLCache


class Cache:
    """
    Simple TTL-based cache with size limits.
    """
    
    def __init__(self, maxsize: int = 1000, ttl: int = 300):
        """
        Initialize cache.
        
        Args:
            maxsize: Maximum number of items in cache
            ttl: Time to live in seconds
        """
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
    
    def delete(self, key: str) -> None:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        """
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """
        Clear all cached values.
        """
        self._cache.clear()
    
    def size(self) -> int:
        """
        Get current cache size.
        
        Returns:
            Number of items in cache
        """
        return len(self._cache)


def cached(
    cache: Cache,
    key_func: Optional[Callable[..., str]] = None,
    ttl: Optional[int] = None
):
    """
    Decorator for caching function results.
    
    Args:
        cache: Cache instance to use
        key_func: Optional function to generate cache key from args/kwargs
        ttl: Optional TTL override for this specific function
    
    Returns:
        Decorated function
    
    Example:
        @cached(my_cache, key_func=lambda doc_id: f"doc:{doc_id}")
        async def get_document(doc_id: str):
            # Expensive operation
            return await fetch_document(doc_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name + str representation of args
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    
    return decorator
