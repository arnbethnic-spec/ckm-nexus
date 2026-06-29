"""Pydantic schemas for WordPress integration."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WordPressPost(BaseModel):
    """WordPress post schema."""
    id: int
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    featured_media: Optional[int] = None
    author: int
    date_gmt: datetime

class WordPressSyncRequest(BaseModel):
    """Request to sync posts from WordPress."""
    site_url: str
    per_page: int = 10
    page: int = 1
