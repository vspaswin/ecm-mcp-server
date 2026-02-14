"""Custom exceptions for ECM client"""


class ECMClientError(Exception):
    """Base exception for ECM client errors"""
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)


class ECMAuthenticationError(ECMClientError):
    """Authentication failed"""
    pass


class ECMNotFoundError(ECMClientError):
    """Resource not found"""
    pass


class ECMPermissionError(ECMClientError):
    """Permission denied"""
    pass


class ECMRateLimitError(ECMClientError):
    """Rate limit exceeded"""
    pass


class ECMValidationError(ECMClientError):
    """Request validation failed"""
    pass


class ECMTimeoutError(ECMClientError):
    """Request timeout"""
    pass
