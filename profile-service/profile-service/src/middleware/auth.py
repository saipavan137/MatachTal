"""
Authentication middleware - validates JWT tokens from auth-service
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.utils.jwt import verify_token
from src.utils.logger import setup_logger
import httpx

logger = setup_logger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user by validating JWT token"""
    token = credentials.credentials
    
    try:
        # Verify token locally (shared secret with auth-service)
        payload = verify_token(token)
        user_id = payload.get("sub") or payload.get("userId")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Extract user info from token payload
        user = {
            "_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role"),
            "organizationId": payload.get("organizationId"),
            "isActive": payload.get("isActive", True)
        }
        
        return user
        
    except ValueError as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def require_roles(*allowed_roles: str):
    """Dependency to check user roles"""
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role(s): {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


def check_organization_access(current_user: dict, requested_org_id: str = None) -> bool:
    """Check if user has access to organization data"""
    user_role = current_user.get("role")
    user_org_id = current_user.get("organizationId")
    
    # Candidates don't have organizationId, they can only access their own data
    if user_role == "candidate":
        return True  # Will be checked at endpoint level
    
    # Employer admins can access all data in their organization
    if user_role == "employer_admin":
        if requested_org_id and str(user_org_id) != str(requested_org_id):
            return False
        return True
    
    # Recruiters can access data in their organization
    if user_role == "recruiter":
        if requested_org_id and str(user_org_id) != str(requested_org_id):
            return False
        return True
    
    return False





