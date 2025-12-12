"""
Tests for resume endpoints
"""
import pytest
from fastapi.testclient import TestClient
from bson import ObjectId


def test_list_resumes_unauthorized(test_client):
    """Test listing resumes without authentication"""
    response = test_client.get("/api/v1/resumes")
    assert response.status_code == 403  # Forbidden - no auth token


@pytest.mark.asyncio
async def test_create_resume_metadata_unauthorized(test_client):
    """Test creating resume metadata without authentication"""
    resume_data = {
        "profileId": str(ObjectId()),
        "fileName": "resume.pdf",
        "fileSize": 102400,
        "mimeType": "application/pdf"
    }
    response = test_client.post("/api/v1/resumes", json=resume_data)
    assert response.status_code == 403  # Forbidden - no auth token

