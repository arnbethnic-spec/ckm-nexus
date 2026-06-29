"""Website API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.website_service import WebsiteService

router = APIRouter(prefix="/websites", tags=["websites"])

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
    """Create a new website."""
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
    """List all websites."""
    service = WebsiteService(db)
    return service.list_websites(skip=skip, limit=limit)


@router.get("/{website_id}", response_model=dict)
def get_website(
    website_id: UUID,
    db: Session = Depends(get_db)
):
    """Get website by ID."""
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
    """Update a website."""
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
    """Delete a website."""
    service = WebsiteService(db)
    result = service.delete_website(website_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.post("/{website_id}/enable", response_model=dict)
def enable_website(
    website_id: UUID,
    db: Session = Depends(get_db)
):
    """Enable a website."""
    service = WebsiteService(db)
    result = service.enable_website(website_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.post("/{website_id}/disable", response_model=dict)
def disable_website(
    website_id: UUID,
    db: Session = Depends(get_db)
):
    """Disable a website."""
    service = WebsiteService(db)
    result = service.disable_website(website_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.post("/{website_id}/rotate-credentials", response_model=dict)
def rotate_credentials(
    website_id: UUID,
    credentials: CredentialsRotate,
    db: Session = Depends(get_db)
):
    """Rotate website credentials."""
    service = WebsiteService(db)
    result = service.rotate_credentials(
        website_id=website_id,
        new_username=credentials.username,
        new_password=credentials.password
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/{website_id}/test-connection", response_model=dict)
def test_connection(
    website_id: UUID,
    db: Session = Depends(get_db)
):
    """Test connection to a website."""
    service = WebsiteService(db)
    
    # Get website
    website_result = service.get_website(website_id)
    if website_result["status"] == "error":
        raise HTTPException(status_code=404, detail=website_result["message"])
    
    website = website_result["website"]
    
    # For this endpoint, we can't test without the password
    # In production, you might store temporary connection tokens
    return {
        "status": "info",
        "message": "To test connection, use the credentials rotation endpoint or update website endpoint with new credentials"
    }
