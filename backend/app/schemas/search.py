"""Pydantic schemas for search operations."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ArticleSearchResultSchema(BaseModel):
    """Schema for individual search result."""
    id: int = Field(..., description="Article ID")
    title: str = Field(..., description="Article title")
    slug: str = Field(..., description="Article slug")
    content: str = Field(..., description="Article content (truncated)")
    url: Optional[str] = Field(None, description="Article URL")
    author: Optional[str] = Field(None, description="Article author")
    published_at: Optional[str] = Field(None, description="Publication date")
    featured_image: Optional[int] = Field(None, description="Featured image ID")


class SimpleSearchResponseSchema(BaseModel):
    """Schema for simple search response."""
    status: str = Field(..., description="Response status")
    query: str = Field(..., description="Search query")
    search_type: str = Field(default="simple", description="Type of search")
    total: int = Field(..., description="Total matching articles")
    count: int = Field(..., description="Number of results returned")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
    articles: List[ArticleSearchResultSchema] = Field(..., description="Search results")


class AdvancedSearchResponseSchema(BaseModel):
    """Schema for advanced search response."""
    status: str = Field(..., description="Response status")
    search_type: str = Field(default="advanced", description="Type of search")
    search_params: dict = Field(..., description="Search parameters used")
    total: int = Field(..., description="Total matching articles")
    count: int = Field(..., description="Number of results returned")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
    articles: List[ArticleSearchResultSchema] = Field(..., description="Search results")


class FulltextSearchResponseSchema(BaseModel):
    """Schema for full-text search response."""
    status: str = Field(..., description="Response status")
    query: str = Field(..., description="Search query")
    search_type: str = Field(default="fulltext", description="Type of search")
    total: int = Field(..., description="Total matching articles")
    count: int = Field(..., description="Number of results returned")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
    articles: List[ArticleSearchResultSchema] = Field(..., description="Search results")


class DateRangeSearchResponseSchema(BaseModel):
    """Schema for date range search response."""
    status: str = Field(..., description="Response status")
    search_type: str = Field(default="date_range", description="Type of search")
    start_date: str = Field(..., description="Start date")
    end_date: str = Field(..., description="End date")
    total: int = Field(..., description="Total matching articles")
    count: int = Field(..., description="Number of results returned")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
    articles: List[ArticleSearchResultSchema] = Field(..., description="Search results")


class AuthorSearchResponseSchema(BaseModel):
    """Schema for author search response."""
    status: str = Field(..., description="Response status")
    search_type: str = Field(default="author", description="Type of search")
    query: str = Field(..., description="Author name searched for")
    total: int = Field(..., description="Total matching articles")
    count: int = Field(..., description="Number of results returned")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
    articles: List[ArticleSearchResultSchema] = Field(..., description="Search results")


class SearchStatisticsSchema(BaseModel):
    """Schema for search statistics response."""
    status: str = Field(..., description="Response status")
    statistics: dict = Field(..., description="Search statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "statistics": {
                    "total_articles": 150,
                    "unique_authors": 25,
                    "first_publication": "2024-01-01T00:00:00",
                    "latest_publication": "2024-12-31T23:59:59"
                }
            }
        }
