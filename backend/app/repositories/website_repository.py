"""Website repository for database operations."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.website import Website


class WebsiteRepository:
    """Repository for website model database operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def create(self, website: Website) -> Website:
        """Create a new website record.
        
        Args:
            website: Website model instance
            
        Returns:
            Created website record
        """
        self.db.add(website)
        self.db.commit()
        self.db.refresh(website)
        return website
    
    def get_by_id(self, website_id: UUID) -> Optional[Website]:
        """Get website by ID.
        
        Args:
            website_id: UUID of the website
            
        Returns:
            Website record or None if not found
        """
        return self.db.query(Website).filter(Website.id == website_id).first()
    
    def get_by_url(self, base_url: str) -> Optional[Website]:
        """Get website by base URL.
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            Website record or None if not found
        """
        return self.db.query(Website).filter(Website.base_url == base_url).first()
    
    def list_all(self, skip: int = 0, limit: int = 10) -> List[Website]:
        """List all websites with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of website records
        """
        return self.db.query(Website).offset(skip).limit(limit).all()
    
    def list_active(self) -> List[Website]:
        """List all active websites.
        
        Returns:
            List of active website records
        """
        return self.db.query(Website).filter(Website.is_active == True).all()
    
    def update(self, website_id: UUID, **kwargs) -> Optional[Website]:
        """Update website record.
        
        Args:
            website_id: UUID of the website
            **kwargs: Fields to update
            
        Returns:
            Updated website record or None if not found
        """
        website = self.get_by_id(website_id)
        if not website:
            return None
        
        for key, value in kwargs.items():
            if hasattr(website, key):
                setattr(website, key, value)
        
        self.db.commit()
        self.db.refresh(website)
        return website
    
    def delete(self, website_id: UUID) -> bool:
        """Delete website record.
        
        Args:
            website_id: UUID of the website
            
        Returns:
            True if deleted, False if not found
        """
        website = self.get_by_id(website_id)
        if not website:
            return False
        
        self.db.delete(website)
        self.db.commit()
        return True
    
    def enable(self, website_id: UUID) -> Optional[Website]:
        """Enable website.
        
        Args:
            website_id: UUID of the website
            
        Returns:
            Updated website record or None if not found
        """
        return self.update(website_id, is_active=True)
    
    def disable(self, website_id: UUID) -> Optional[Website]:
        """Disable website.
        
        Args:
            website_id: UUID of the website
            
        Returns:
            Updated website record or None if not found
        """
        return self.update(website_id, is_active=False)
