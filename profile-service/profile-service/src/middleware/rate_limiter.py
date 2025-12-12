"""
Rate limiting middleware
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.config.settings import settings

# Create rate limiter
rate_limiter = Limiter(key_func=get_remote_address)





