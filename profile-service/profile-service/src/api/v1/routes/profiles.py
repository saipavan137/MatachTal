"""
Candidate profile routes
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi import Request
from bson import ObjectId
from typing import Optional, List
from src.config.database import get_database
from src.models.profile import Profile, ProfileCreate, ProfileUpdate, ProfileResponse
from src.middleware.auth import get_current_user, require_roles, check_organization_access
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Create a new candidate profile"""
    db = get_database()
    
    # Only candidates can create their own profile
    if current_user.get("role") != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can create profiles"
        )
    
    # Verify userId matches current user
    if str(current_user["_id"]) != profile_data.userId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create a profile for yourself"
        )
    
    # Check if profile already exists for this user
    existing_profile = await db.candidate_profiles.find_one({
        "userId": ObjectId(profile_data.userId)
    })
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists for this user"
        )
    
    # Prepare profile document
    profile_doc = profile_data.model_dump(exclude={"userId", "organizationId"})
    profile_doc["userId"] = ObjectId(profile_data.userId)
    
    if profile_data.organizationId:
        profile_doc["organizationId"] = ObjectId(profile_data.organizationId)
    
    profile_doc["isActive"] = True
    profile_doc["createdAt"] = datetime.utcnow()
    profile_doc["updatedAt"] = datetime.utcnow()
    
    # Insert profile
    result = await db.candidate_profiles.insert_one(profile_doc)
    profile_doc["_id"] = result.inserted_id
    
    logger.info(f"Profile created: {profile_doc['_id']} for user {profile_data.userId}")
    
    return {
        "success": True,
        "message": "Profile created successfully",
        "data": {
            "profile": Profile.profile_to_dict(profile_doc)
        }
    }


@router.get("/{profile_id}", response_model=dict)
async def get_profile(
    profile_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get profile by ID"""
    db = get_database()
    
    if not ObjectId.is_valid(profile_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid profile ID format"
        )
    
    profile = await db.candidate_profiles.find_one({"_id": ObjectId(profile_id)})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Authorization check
    user_role = current_user.get("role")
    user_id = str(current_user["_id"])
    profile_user_id = str(profile.get("userId"))
    
    # Candidates can only see their own profile
    if user_role == "candidate":
        if user_id != profile_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own profile"
            )
    else:
        # Recruiters/admins can see profiles in their organization
        profile_org_id = profile.get("organizationId")
        if not check_organization_access(current_user, str(profile_org_id) if profile_org_id else None):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return {
        "success": True,
        "data": {
            "profile": Profile.profile_to_dict(profile)
        }
    }


@router.get("", response_model=dict)
async def list_profiles(
    userId: Optional[str] = Query(None, description="Filter by user ID"),
    organizationId: Optional[str] = Query(None, description="Filter by organization ID"),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    skills: Optional[str] = Query(None, description="Comma-separated list of skills to filter by"),
    isActive: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user)
):
    """List profiles with filters and pagination"""
    db = get_database()
    
    user_role = current_user.get("role")
    
    # Build query
    query = {}
    
    # Candidates can only see their own profile
    if user_role == "candidate":
        query["userId"] = ObjectId(current_user["_id"])
    else:
        # Recruiters/admins see profiles in their organization
        user_org_id = current_user.get("organizationId")
        if user_org_id:
            query["organizationId"] = ObjectId(user_org_id)
    
    # Apply filters
    if userId:
        if not ObjectId.is_valid(userId):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        query["userId"] = ObjectId(userId)
    
    if organizationId:
        if not ObjectId.is_valid(organizationId):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization ID format"
            )
        query["organizationId"] = ObjectId(organizationId)
    
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    
    if skills:
        skill_list = [s.strip().lower() for s in skills.split(",")]
        query["skills"] = {"$in": skill_list}
    
    if isActive is not None:
        query["isActive"] = isActive
    
    # Pagination
    skip = (page - 1) * limit
    
    # Get profiles
    cursor = db.candidate_profiles.find(query).skip(skip).limit(limit).sort("createdAt", -1)
    profiles = await cursor.to_list(length=limit)
    
    # Get total count
    total = await db.candidate_profiles.count_documents(query)
    
    return {
        "success": True,
        "data": {
            "profiles": [Profile.profile_to_dict(profile) for profile in profiles],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    }


@router.put("/{profile_id}", response_model=dict)
async def update_profile(
    profile_id: str,
    profile_update: ProfileUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Update profile"""
    db = get_database()
    
    if not ObjectId.is_valid(profile_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid profile ID format"
        )
    
    profile = await db.candidate_profiles.find_one({"_id": ObjectId(profile_id)})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Authorization check
    user_role = current_user.get("role")
    user_id = str(current_user["_id"])
    profile_user_id = str(profile.get("userId"))
    
    # Candidates can only update their own profile
    if user_role == "candidate":
        if user_id != profile_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile"
            )
    else:
        # Recruiters/admins can update profiles in their organization
        profile_org_id = profile.get("organizationId")
        if not check_organization_access(current_user, str(profile_org_id) if profile_org_id else None):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Prepare update
    update_data = profile_update.model_dump(exclude_unset=True)
    if update_data:
        update_data["updatedAt"] = datetime.utcnow()
        await db.candidate_profiles.update_one(
            {"_id": ObjectId(profile_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Profile updated: {profile_id} by {current_user['_id']}")
    
    # Get updated profile
    updated_profile = await db.candidate_profiles.find_one({"_id": ObjectId(profile_id)})
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": {
            "profile": Profile.profile_to_dict(updated_profile)
        }
    }


@router.get("/user/{user_id}", response_model=dict)
async def get_profile_by_user_id(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get profile by user ID"""
    db = get_database()
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    profile = await db.candidate_profiles.find_one({"userId": ObjectId(user_id)})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found for this user"
        )
    
    # Authorization check
    user_role = current_user.get("role")
    current_user_id = str(current_user["_id"])
    
    # Candidates can only see their own profile
    if user_role == "candidate":
        if current_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own profile"
            )
    else:
        # Recruiters/admins can see profiles in their organization
        profile_org_id = profile.get("organizationId")
        if not check_organization_access(current_user, str(profile_org_id) if profile_org_id else None):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return {
        "success": True,
        "data": {
            "profile": Profile.profile_to_dict(profile)
        }
    }

