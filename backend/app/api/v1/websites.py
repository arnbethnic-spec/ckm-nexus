"""API v1 - Websites endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.website_service import WebsiteService

router = APIRouter(prefix="/api/v1/websites", tags=["websites"])

# Pydantic schemas
class WebsiteCreate(BaseModel):
    """Schema for creating a website."""
    name: str
    base_url: str
    username: str
    password: str
    test_connection: bool = True


class WebsiteUpdate(BaseModel):
    """Schema for updating a website."""
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class CredentialsRotate(BaseModel):
    """Schema for rotating credentials."""
    username: str
    password: str


class WebsiteResponse(BaseModel):
    """Schema for website response."""
    id: str
    name: str
    base_url: str
    username: str
    is_active: bool
    created_at: Optional[str] = None


# CRUD Endpoints
@router.post("/", response_model=dict)
def create_website(
    website_data: WebsiteCreate,
    db: Session = Depends(get_db)
):
    """Create a new website.
    
    Args:
        website_data: Website creation data
        db: Database session
        
    Returns:
        Created website data or error
    """
    service = WebsiteService(db)
    result = service.create_website(
        name=website_data.name,
        base_url=website_data.base_url,
        username=website_data.username,
        password=website_data.password,
        test_connection=website_data.test_connection
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/", response_model=dict)
def list_websites(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List all websites with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        db: Database session
        
    Returns:
        List of websites
    """
    service = WebsiteService(db)
    return service.list_websites(skip=skip, limit=limit)


@router.get("/{website_id}", response_model=dict)
def get_website(
    website_id: UUID,
    db: Session = Depends(get_db)
):
    """Get website by ID.
    
    Args:
        website_id: Website UUID
        db: Database session
        
    Returns:
        Website data or 404 error
    """
    service = WebsiteService(db)
    result = service.get_website(website_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.put("/{website_id}", response_model=dict)
def update_website(
    website_id: UUID,
    website_data: WebsiteUpdate,
    db: Session = Depends(get_db)
):
    """Update a website.
    
    Args:
        website_id: Website UUID
        website_data: Update data
        db: Database session
        
    Returns:
        Updated website or error
    """
    service = WebsiteService(db)
    result = service.update_website(
        website_id=website_id,
        name=website_data.name,
        username=website_data.username,
        password=website_data.password
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.delete("/{website_id}", response_model=dict)
def delete_website(
    website_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a website.
    
    Args:
        website_id: Website UUID
        db: Database session
        
    Returns:
        Deletion confirmation or error
    """
    service = WebsiteService(db)
    result = service.delete_website(website_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.post("/{website_id}/test", response_model=dict)
def test_connection(
    website_id: UUID,
    db: Session = Depends(get_db)
):
    """Test connection to a website.
    
    Args:
        website_id: Website UUID
        db: Database session
        
    Returns:
        Connection test result
    """
    service = WebsiteService(db)
    
    # Get website
    website_result = service.get_website(website_id)
    if website_result["status"] == "error":
        raise HTTPException(status_code=404, detail=website_result["message"])
    
    website = website_result["website"]
    
    return {
        "status": "info",
        "message": "To test connection, rotate credentials or update website with new credentials",
        "website_id": str(website_id),
        "website_name": website["name"]
    }


@router.post("/{website_id}/sync", response_model=dict)
def sync_website_posts(
    website_id: UUID,
    db: Session = Depends(get_db)
):
    """Sync posts from a website to database.
    
    Args:
        website_id: Website UUID
        db: Database session
        
    Returns:
        Sync result
    """
    from app.services.wordpress_sync import WordPressSyncService
    
    service = WebsiteService(db)
    
    # Get website
    website_result = service.get_website(website_id)
    if website_result["status"] == "error":
        raise HTTPException(status_code=404, detail=website_result["message"])
    
    website = website_result["website"]
    
    if not website["is_active"]:
        raise HTTPException(status_code=400, detail="Website is not active")
    
    try:
        # Decrypt password
        from app.repositories.website_repository import WebsiteRepository
        repo = WebsiteRepository(db)
        website_record = repo.get_by_id(website_id)
        password = service._decrypt_password(website_record.encrypted_password)
        
        # Perform sync
        sync_service = WordPressSyncService(db)
        result = sync_service.sync_posts(
            site_url=website["base_url"],
            username=website["username"],
            password=password
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Sync failed: {str(e)}")
