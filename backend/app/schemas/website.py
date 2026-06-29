"""Pydantic schemas for website operations."""
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID
from typing import Optional
from datetime import datetime


class WebsiteCreateSchema(BaseModel):
    """Schema for creating a website."""
    name: str = Field(..., min_length=1, max_length=200, description="Website name")
    base_url: str = Field(..., min_length=1, max_length=500, description="WordPress site URL")
    username: str = Field(..., min_length=1, max_length=200, description="WordPress username")
    password: str = Field(..., min_length=1, max_length=500, description="WordPress password")
    test_connection: bool = Field(default=True, description="Test connection before creating")


class WebsiteUpdateSchema(BaseModel):
    """Schema for updating a website."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Website name")
    username: Optional[str] = Field(None, min_length=1, max_length=200, description="WordPress username")
    password: Optional[str] = Field(None, min_length=1, max_length=500, description="WordPress password")


class WebsiteResponseSchema(BaseModel):
    """Schema for website response."""
    id: str = Field(..., description="Website UUID")
    name: str = Field(..., description="Website name")
    base_url: str = Field(..., description="WordPress site URL")
    username: str = Field(..., description="WordPress username")
    is_active: bool = Field(..., description="Whether website is active")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class WebsiteListResponseSchema(BaseModel):
    """Schema for website list response."""
    status: str = Field(..., description="Response status")
    count: int = Field(..., description="Number of websites")
    websites: list[WebsiteResponseSchema] = Field(..., description="List of websites")


class CredentialsRotateSchema(BaseModel):
    """Schema for rotating credentials."""
    username: str = Field(..., min_length=1, max_length=200, description="New WordPress username")
    password: str = Field(..., min_length=1, max_length=500, description="New WordPress password")


class WebsiteTestConnectionSchema(BaseModel):
    """Schema for connection test response."""
    status: str = Field(..., description="Test status")
    connected: bool = Field(..., description="Whether connection was successful")
    site_name: Optional[str] = Field(None, description="WordPress site name")
    error: Optional[str] = Field(None, description="Error message if failed")


class WebsiteSyncResponseSchema(BaseModel):
    """Schema for sync operation response."""
    status: str = Field(..., description="Sync status")
    synced: int = Field(..., description="Number of new posts synced")
    updated: int = Field(..., description="Number of posts updated")
    total: int = Field(..., description="Total posts processed")
    message: str = Field(..., description="Sync result message")
