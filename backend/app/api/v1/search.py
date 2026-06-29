"""Search API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.session import get_db
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/articles", response_model=dict)
def search_articles(
    q: str = Query(..., min_length=2, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Simple full-text search across articles.
    
    Searches in: title, content, author
    
    Args:
        q: Search query (minimum 2 characters)
        skip: Pagination offset
        limit: Pagination limit
        db: Database session
        
    Returns:
        Search results with matching articles
    """
    service = SearchService(db)
    result = service.simple_search(query=q, skip=skip, limit=limit)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/articles/advanced", response_model=dict)
def advanced_search(
    title: str = Query(None, description="Search in title"),
    content: str = Query(None, description="Search in content"),
    author: str = Query(None, description="Search by author"),
    published_after: datetime = Query(None, description="Filter articles after this date"),
    published_before: datetime = Query(None, description="Filter articles before this date"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Advanced search with field-specific filters and date range.
    
    Args:
        title: Search in title field
        content: Search in content field
        author: Search by author
        published_after: Filter after this date
        published_before: Filter before this date
        skip: Pagination offset
        limit: Pagination limit
        db: Database session
        
    Returns:
        Search results with filtered articles
    """
    if not any([title, content, author, published_after, published_before]):
        raise HTTPException(
            status_code=400,
            detail="At least one search criterion is required"
        )
    
    service = SearchService(db)
    result = service.advanced_search(
        title=title,
        content=content,
        author=author,
        published_after=published_after,
        published_before=published_before,
        skip=skip,
        limit=limit
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/articles/fulltext", response_model=dict)
def fulltext_search(
    q: str = Query(..., min_length=2, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Full-text search using database capabilities.
    
    Args:
        q: Search query (minimum 2 characters)
        skip: Pagination offset
        limit: Pagination limit
        db: Database session
        
    Returns:
        Full-text search results
    """
    service = SearchService(db)
    result = service.fulltext_search(query=q, skip=skip, limit=limit)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/articles/author/{author_name}", response_model=dict)
def search_by_author(
    author_name: str = Query(..., description="Author name to search for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Search articles by author.
    
    Args:
        author_name: Author name to search for
        skip: Pagination offset
        limit: Pagination limit
        db: Database session
        
    Returns:
        Articles by the specified author
    """
    service = SearchService(db)
    result = service.search_by_author(author=author_name, skip=skip, limit=limit)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/articles/date-range", response_model=dict)
def search_date_range(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Search articles within a date range.
    
    Args:
        start_date: Start date (ISO format, e.g., 2024-01-01)
        end_date: End date (ISO format, e.g., 2024-12-31)
        skip: Pagination offset
        limit: Pagination limit
        db: Database session
        
    Returns:
        Articles published in the specified date range
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date"
        )
    
    service = SearchService(db)
    result = service.search_by_date_range(
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/statistics", response_model=dict)
def get_statistics(db: Session = Depends(get_db)):
    """Get search statistics about articles.
    
    Returns:
        Statistics including total articles, unique authors, date range
    """
    service = SearchService(db)
    return service.search_statistics()
