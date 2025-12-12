"""
JWT token utilities for validating tokens from auth-service
"""
from typing import Dict
from jose import JWTError, jwt
from src.config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def verify_token(token: str) -> Dict:
    """Verify and decode JWT token from auth-service"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer="matchtal-auth-service",
            audience="matchtal-platform"
        )
        
        # Verify it's an access token
        if payload.get("type") != "access":
            raise ValueError("Token is not an access token")
        
        return payload
    except JWTError as e:
        logger.error(f"JWT verification error: {e}")
        raise ValueError(f"Invalid token: {str(e)}")





