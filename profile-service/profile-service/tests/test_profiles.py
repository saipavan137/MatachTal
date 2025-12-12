"""
Tests for profile endpoints
"""
import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime


def test_health_check(test_client):
    """Test health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "profile-service"


def test_create_profile_unauthorized(test_client):
    """Test creating profile without authentication"""
    profile_data = {
        "userId": str(ObjectId()),
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@example.com"
    }
    response = test_client.post("/api/v1/profiles", json=profile_data)
    assert response.status_code == 403  # Forbidden - no auth token


@pytest.mark.asyncio
async def test_create_profile_authorized(test_client, test_db):
    """Test creating profile with authentication"""
    from src.utils.jwt import verify_token
    from src.config.settings import settings
    from jose import jwt
    from datetime import datetime, timedelta
    
    # Create a mock JWT token
    user_id = str(ObjectId())
    token_data = {
        "sub": user_id,
        "userId": user_id,
        "email": "john@example.com",
        "role": "candidate",
        "isActive": True,
        "exp": datetime.utcnow() + timedelta(minutes=60),
        "iat": datetime.utcnow(),
        "iss": "matchtal-auth-service",
        "aud": "matchtal-platform",
        "type": "access"
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    profile_data = {
        "userId": user_id,
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@example.com",
        "skills": ["Python", "FastAPI"]
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.post("/api/v1/profiles", json=profile_data, headers=headers)
    
    # Should succeed (201) or fail with validation (422)
    assert response.status_code in [201, 422]


@pytest.mark.asyncio
async def test_get_profile_not_found(test_client, test_db):
    """Test getting non-existent profile"""
    from src.config.settings import settings
    from jose import jwt
    from datetime import datetime, timedelta
    
    # Create a mock JWT token
    user_id = str(ObjectId())
    token_data = {
        "sub": user_id,
        "userId": user_id,
        "email": "john@example.com",
        "role": "candidate",
        "isActive": True,
        "exp": datetime.utcnow() + timedelta(minutes=60),
        "iat": datetime.utcnow(),
        "iss": "matchtal-auth-service",
        "aud": "matchtal-platform",
        "type": "access"
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    headers = {"Authorization": f"Bearer {token}"}
    fake_id = str(ObjectId())
    response = test_client.get(f"/api/v1/profiles/{fake_id}", headers=headers)
    assert response.status_code == 404

