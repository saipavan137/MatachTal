"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from src.main import app
from src.config.database import get_database, connect_db, close_db
from src.config.settings import settings
import os


@pytest.fixture(scope="session")
def test_client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture(scope="function")
async def test_db():
    """Create test database connection"""
    # Use test database
    test_db_name = settings.MONGODB_TEST_DATABASE
    test_client = AsyncIOMotorClient(settings.MONGODB_URI)
    test_db = test_client[test_db_name]
    
    # Set the database module's database for this test
    import src.config.database as db_module
    db_module.database = test_db
    
    yield test_db
    
    # Cleanup: drop test database
    await test_client.drop_database(test_db_name)
    test_client.close()
    db_module.database = None


@pytest.fixture(scope="function")
async def sample_profile(test_db):
    """Create a sample profile for testing"""
    from bson import ObjectId
    from datetime import datetime
    
    profile_doc = {
        "userId": ObjectId(),
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "location": "New York, NY",
        "summary": "Experienced software engineer",
        "skills": ["Python", "FastAPI", "MongoDB"],
        "experience": [],
        "education": [],
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await test_db.candidate_profiles.insert_one(profile_doc)
    profile_doc["_id"] = result.inserted_id
    
    return profile_doc


@pytest.fixture(scope="function")
async def sample_resume(test_db, sample_profile):
    """Create a sample resume metadata for testing"""
    from bson import ObjectId
    from datetime import datetime
    
    resume_doc = {
        "profileId": sample_profile["_id"],
        "fileName": "resume.pdf",
        "fileSize": 102400,
        "mimeType": "application/pdf",
        "s3Key": "resumes/resume-123.pdf",
        "s3Bucket": "matchtal-resumes",
        "isActive": True,
        "isPrimary": True,
        "uploadedAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await test_db.resume_metadata.insert_one(resume_doc)
    resume_doc["_id"] = result.inserted_id
    
    return resume_doc

