"""Pydantic schemas for WordPress integration."""
from pydantic import BaseModel

class WPPost(BaseModel):
    """WordPress post schema."""
    id: int
    title: dict
    content: dict
    status: str

class WPCategory(BaseModel):
    """WordPress category schema."""
    id: int
    name: str

class WPTag(BaseModel):
    """WordPress tag schema."""
    id: int
    name: str
