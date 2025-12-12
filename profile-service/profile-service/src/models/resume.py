"""
Resume metadata model and schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class ResumeMetadataBase(BaseModel):
    """Base resume metadata schema"""
    profileId: str = Field(..., description="Profile ID this resume belongs to")
    fileName: str = Field(..., min_length=1, max_length=500)
    fileSize: int = Field(..., ge=0, description="File size in bytes")
    mimeType: str = Field(..., description="MIME type (e.g., application/pdf)")
    s3Key: Optional[str] = Field(None, description="S3 object key if stored in S3")
    s3Bucket: Optional[str] = Field(None, description="S3 bucket name")
    isActive: bool = True
    isPrimary: bool = False
    notes: Optional[str] = Field(None, max_length=1000)


class ResumeMetadataCreate(ResumeMetadataBase):
    """Resume metadata creation schema"""
    pass


class ResumeMetadataUpdate(BaseModel):
    """Resume metadata update schema"""
    fileName: Optional[str] = Field(None, min_length=1, max_length=500)
    isActive: Optional[bool] = None
    isPrimary: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)


class ResumeMetadataResponse(ResumeMetadataBase):
    """Resume metadata response schema"""
    id: str = Field(..., alias="_id")
    uploadedAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True


class ResumeMetadata:
    """Resume metadata model for database operations"""
    
    @staticmethod
    def resume_to_dict(resume: dict) -> dict:
        """Convert resume document to dict"""
        resume_dict = resume.copy()
        resume_dict['_id'] = str(resume_dict['_id'])
        
        # Convert profileId ObjectId to string if present
        if resume_dict.get('profileId') and isinstance(resume_dict['profileId'], ObjectId):
            resume_dict['profileId'] = str(resume_dict['profileId'])
        
        return resume_dict





