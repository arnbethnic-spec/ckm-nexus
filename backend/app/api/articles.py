"""Article API endpoints (CRUD operations)."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.article import Article
from app.database.session import get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/articles", tags=["articles"])

# Pydantic schemas
class ArticleCreate(BaseModel):
    """Schema for creating an article."""
    title: str
    slug: str
    content: str
    url: Optional[str] = None
    featured_image: Optional[int] = None
    author: Optional[str] = None

class ArticleUpdate(BaseModel):
    """Schema for updating an article."""
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    featured_image: Optional[int] = None
    author: Optional[str] = None

class ArticleResponse(BaseModel):
    """Schema for article response."""
    id: int
    title: str
    slug: str
    content: str
    url: Optional[str] = None
    featured_image: Optional[int] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True

# CRUD Endpoints
@router.get("/", response_model=list[ArticleResponse])
def list_articles(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List all articles with pagination."""
    articles = db.query(Article).offset(skip).limit(limit).all()
    return articles

@router.post("/", response_model=ArticleResponse)
def create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db)
):
    """Create a new article."""
    # Check if slug already exists
    existing = db.query(Article).filter_by(slug=article.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Article with this slug already exists")
    
    db_article = Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific article by ID."""
    article = db.query(Article).filter_by(id=article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: int,
    article: ArticleUpdate,
    db: Session = Depends(get_db)
):
    """Update an article."""
    db_article = db.query(Article).filter_by(id=article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    update_data = article.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_article, field, value)
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@router.delete("/{article_id}")
def delete_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Delete an article."""
    db_article = db.query(Article).filter_by(id=article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    db.delete(db_article)
    db.commit()
    return {"message": "Article deleted successfully"}

@router.get("/search/{query}", response_model=list[ArticleResponse])
def search_articles(
    query: str,
    db: Session = Depends(get_db)
):
    """Search articles by title or content."""
    articles = db.query(Article).filter(
        (Article.title.ilike(f"%{query}%")) | 
        (Article.content.ilike(f"%{query}%"))
    ).all()
    return articles
