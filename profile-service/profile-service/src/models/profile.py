"""
Candidate profile model and schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class Experience(BaseModel):
    """Work experience entry"""
    company: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=200)
    startDate: str = Field(..., description="Start date in YYYY-MM format")
    endDate: Optional[str] = Field(None, description="End date in YYYY-MM format, null for current")
    isCurrent: bool = False
    description: Optional[str] = Field(None, max_length=5000)
    location: Optional[str] = Field(None, max_length=200)
    
    @field_validator('endDate')
    @classmethod
    def validate_end_date(cls, v, info):
        if v is None:
            return v
        start_date = info.data.get('startDate')
        if start_date and v < start_date:
            raise ValueError('End date must be after start date')
        return v


class Education(BaseModel):
    """Education entry"""
    institution: str = Field(..., min_length=1, max_length=200)
    degree: str = Field(..., min_length=1, max_length=200)
    fieldOfStudy: Optional[str] = Field(None, max_length=200)
    startDate: str = Field(..., description="Start date in YYYY-MM format")
    endDate: Optional[str] = Field(None, description="End date in YYYY-MM format")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    description: Optional[str] = Field(None, max_length=2000)


class ProfileBase(BaseModel):
    """Base profile schema"""
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = Field(None, max_length=2000)
    skills: List[str] = Field(default_factory=list, max_length=100)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    linkedInUrl: Optional[str] = Field(None, max_length=500)
    portfolioUrl: Optional[str] = Field(None, max_length=500)
    githubUrl: Optional[str] = Field(None, max_length=500)
    websiteUrl: Optional[str] = Field(None, max_length=500)


class ProfileCreate(ProfileBase):
    """Profile creation schema"""
    userId: str = Field(..., description="User ID from auth-service")
    organizationId: Optional[str] = Field(None, description="Organization ID if applicable")


class ProfileUpdate(BaseModel):
    """Profile update schema"""
    firstName: Optional[str] = Field(None, min_length=1, max_length=100)
    lastName: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = Field(None, max_length=2000)
    skills: Optional[List[str]] = Field(None, max_length=100)
    experience: Optional[List[Experience]] = None
    education: Optional[List[Education]] = None
    linkedInUrl: Optional[str] = Field(None, max_length=500)
    portfolioUrl: Optional[str] = Field(None, max_length=500)
    githubUrl: Optional[str] = Field(None, max_length=500)
    websiteUrl: Optional[str] = Field(None, max_length=500)


class ProfileResponse(ProfileBase):
    """Profile response schema"""
    id: str = Field(..., alias="_id")
    userId: str
    organizationId: Optional[str] = None
    isActive: bool = True
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True


class Profile:
    """Profile model for database operations"""
    
    @staticmethod
    def profile_to_dict(profile: dict) -> dict:
        """Convert profile document to dict"""
        profile_dict = profile.copy()
        profile_dict['_id'] = str(profile_dict['_id'])
        
        # Convert userId ObjectId to string if present
        if profile_dict.get('userId') and isinstance(profile_dict['userId'], ObjectId):
            profile_dict['userId'] = str(profile_dict['userId'])
        
        # Convert organizationId ObjectId to string if present
        if profile_dict.get('organizationId') and isinstance(profile_dict['organizationId'], ObjectId):
            profile_dict['organizationId'] = str(profile_dict['organizationId'])
        
        return profile_dict





