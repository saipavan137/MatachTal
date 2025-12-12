"""
Resume metadata routes
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi import Request
from bson import ObjectId
from typing import Optional
from src.config.database import get_database
from src.models.resume import ResumeMetadata, ResumeMetadataCreate, ResumeMetadataUpdate, ResumeMetadataResponse
from src.middleware.auth import get_current_user, require_roles
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_resume_metadata(
    resume_data: ResumeMetadataCreate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Create resume metadata (file upload stubbed - S3 integration to be added)"""
    db = get_database()
    
    # Verify profile exists and belongs to user
    if not ObjectId.is_valid(resume_data.profileId):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid profile ID format"
        )
    
    profile = await db.candidate_profiles.find_one({"_id": ObjectId(resume_data.profileId)})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Authorization check
    user_role = current_user.get("role")
    user_id = str(current_user["_id"])
    profile_user_id = str(profile.get("userId"))
    
    # Candidates can only add resumes to their own profile
    if user_role == "candidate":
        if user_id != profile_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only add resumes to your own profile"
            )
    
    # If this is set as primary, unset other primary resumes
    if resume_data.isPrimary:
        await db.resume_metadata.update_many(
            {"profileId": ObjectId(resume_data.profileId), "isActive": True},
            {"$set": {"isPrimary": False}}
        )
    
    # Prepare resume document
    resume_doc = resume_data.model_dump()
    resume_doc["profileId"] = ObjectId(resume_data.profileId)
    resume_doc["uploadedAt"] = datetime.utcnow()
    resume_doc["updatedAt"] = datetime.utcnow()
    
    # Insert resume metadata
    result = await db.resume_metadata.insert_one(resume_doc)
    resume_doc["_id"] = result.inserted_id
    
    logger.info(f"Resume metadata created: {resume_doc['_id']} for profile {resume_data.profileId}")
    
    return {
        "success": True,
        "message": "Resume metadata created successfully",
        "data": {
            "resume": ResumeMetadata.resume_to_dict(resume_doc)
        }
    }


@router.get("/{resume_id}", response_model=dict)
async def get_resume_metadata(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get resume metadata by ID"""
    db = get_database()
    
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format"
        )
    
    resume = await db.resume_metadata.find_one({"_id": ObjectId(resume_id)})
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get associated profile for authorization check
    profile = await db.candidate_profiles.find_one({"_id": resume.get("profileId")})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated profile not found"
        )
    
    # Authorization check
    user_role = current_user.get("role")
    user_id = str(current_user["_id"])
    profile_user_id = str(profile.get("userId"))
    
    # Candidates can only see their own resumes
    if user_role == "candidate":
        if user_id != profile_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own resumes"
            )
    
    return {
        "success": True,
        "data": {
            "resume": ResumeMetadata.resume_to_dict(resume)
        }
    }


@router.get("", response_model=dict)
async def list_resume_metadata(
    profileId: Optional[str] = Query(None, description="Filter by profile ID"),
    isActive: Optional[bool] = Query(None, description="Filter by active status"),
    isPrimary: Optional[bool] = Query(None, description="Filter by primary status"),
    current_user: dict = Depends(get_current_user)
):
    """List resume metadata with filters"""
    db = get_database()
    
    # Build query
    query = {}
    
    if profileId:
        if not ObjectId.is_valid(profileId):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid profile ID format"
            )
        query["profileId"] = ObjectId(profileId)
        
        # Verify profile exists and check authorization
        profile = await db.candidate_profiles.find_one({"_id": ObjectId(profileId)})
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Authorization check
        user_role = current_user.get("role")
        user_id = str(current_user["_id"])
        profile_user_id = str(profile.get("userId"))
        
        # Candidates can only see their own resumes
        if user_role == "candidate":
            if user_id != profile_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own resumes"
                )
    
    if isActive is not None:
        query["isActive"] = isActive
    
    if isPrimary is not None:
        query["isPrimary"] = isPrimary
    
    # Get resumes
    cursor = db.resume_metadata.find(query).sort("uploadedAt", -1)
    resumes = await cursor.to_list(length=None)
    
    return {
        "success": True,
        "data": {
            "resumes": [ResumeMetadata.resume_to_dict(resume) for resume in resumes]
        }
    }


@router.put("/{resume_id}", response_model=dict)
async def update_resume_metadata(
    resume_id: str,
    resume_update: ResumeMetadataUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Update resume metadata"""
    db = get_database()
    
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format"
        )
    
    resume = await db.resume_metadata.find_one({"_id": ObjectId(resume_id)})
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get associated profile for authorization check
    profile = await db.candidate_profiles.find_one({"_id": resume.get("profileId")})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated profile not found"
        )
    
    # Authorization check
    user_role = current_user.get("role")
    user_id = str(current_user["_id"])
    profile_user_id = str(profile.get("userId"))
    
    # Candidates can only update their own resumes
    if user_role == "candidate":
        if user_id != profile_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own resumes"
            )
    
    # If setting as primary, unset other primary resumes
    update_data = resume_update.model_dump(exclude_unset=True)
    if update_data.get("isPrimary") is True:
        await db.resume_metadata.update_many(
            {
                "profileId": resume.get("profileId"),
                "_id": {"$ne": ObjectId(resume_id)},
                "isActive": True
            },
            {"$set": {"isPrimary": False}}
        )
    
    # Prepare update
    if update_data:
        update_data["updatedAt"] = datetime.utcnow()
        await db.resume_metadata.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Resume metadata updated: {resume_id} by {current_user['_id']}")
    
    # Get updated resume
    updated_resume = await db.resume_metadata.find_one({"_id": ObjectId(resume_id)})
    
    return {
        "success": True,
        "message": "Resume metadata updated successfully",
        "data": {
            "resume": ResumeMetadata.resume_to_dict(updated_resume)
        }
    }


@router.delete("/{resume_id}", response_model=dict)
async def delete_resume_metadata(
    resume_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Soft delete resume metadata (set isActive to False)"""
    db = get_database()
    
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format"
        )
    
    resume = await db.resume_metadata.find_one({"_id": ObjectId(resume_id)})
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get associated profile for authorization check
    profile = await db.candidate_profiles.find_one({"_id": resume.get("profileId")})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated profile not found"
        )
    
    # Authorization check
    user_role = current_user.get("role")
    user_id = str(current_user["_id"])
    profile_user_id = str(profile.get("userId"))
    
    # Candidates can only delete their own resumes
    if user_role == "candidate":
        if user_id != profile_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own resumes"
            )
    
    # Soft delete
    await db.resume_metadata.update_one(
        {"_id": ObjectId(resume_id)},
        {"$set": {"isActive": False, "updatedAt": datetime.utcnow()}}
    )
    
    logger.info(f"Resume metadata deleted: {resume_id} by {current_user['_id']}")
    
    return {
        "success": True,
        "message": "Resume metadata deleted successfully"
    }

