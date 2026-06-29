"""Search service with full-text search capabilities."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.models.article import Article
from app.core.logging import logger


class SearchService:
    """Service for searching articles with multiple strategies."""
    
    def __init__(self, db: Session):
        """Initialize search service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def simple_search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Simple text search using ILIKE (case-insensitive LIKE).
        
        Searches in: title, content, author
        
        Args:
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            Dictionary with search results
        """
        try:
            if not query or len(query.strip()) < 2:
                return {
                    "status": "error",
                    "message": "Query must be at least 2 characters"
                }
            
            search_pattern = f"%{query}%"
            
            # Search in title, content, and author
            articles = self.db.query(Article).filter(
                or_(
                    Article.title.ilike(search_pattern),
                    Article.content.ilike(search_pattern),
                    Article.author.ilike(search_pattern)
                )
            ).offset(skip).limit(limit).all()
            
            total = self.db.query(Article).filter(
                or_(
                    Article.title.ilike(search_pattern),
                    Article.content.ilike(search_pattern),
                    Article.author.ilike(search_pattern)
                )
            ).count()
            
            logger.info(f"Simple search for '{query}': found {len(articles)} results")
            
            return {
                "status": "success",
                "query": query,
                "search_type": "simple",
                "total": total,
                "count": len(articles),
                "skip": skip,
                "limit": limit,
                "articles": [self._format_article(article) for article in articles]
            }
        except Exception as e:
            logger.error(f"Simple search failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }
    
    def advanced_search(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None,
        author: Optional[str] = None,
        published_after: Optional[datetime] = None,
        published_before: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Advanced search with field-specific filtering.
        
        Args:
            title: Search in title field
            content: Search in content field
            author: Search in author field
            published_after: Filter articles published after this date
            published_before: Filter articles published before this date
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            Dictionary with search results
        """
        try:
            query = self.db.query(Article)
            filters = []
            
            # Add field-specific filters
            if title:
                filters.append(Article.title.ilike(f"%{title}%"))
            
            if content:
                filters.append(Article.content.ilike(f"%{content}%"))
            
            if author:
                filters.append(Article.author.ilike(f"%{author}%"))
            
            # Add date range filters
            if published_after:
                filters.append(Article.published_at >= published_after)
            
            if published_before:
                filters.append(Article.published_at <= published_before)
            
            # Apply all filters with AND logic
            if filters:
                query = query.filter(and_(*filters))
            
            # Get total count
            total = query.count()
            
            # Get paginated results
            articles = query.offset(skip).limit(limit).all()
            
            search_params = {
                "title": title,
                "content": content,
                "author": author,
                "published_after": published_after.isoformat() if published_after else None,
                "published_before": published_before.isoformat() if published_before else None
            }
            
            logger.info(f"Advanced search with params {search_params}: found {len(articles)} results")
            
            return {
                "status": "success",
                "search_type": "advanced",
                "search_params": search_params,
                "total": total,
                "count": len(articles),
                "skip": skip,
                "limit": limit,
                "articles": [self._format_article(article) for article in articles]
            }
        except Exception as e:
            logger.error(f"Advanced search failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }
    
    def fulltext_search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Full-text search using PostgreSQL capabilities.
        
        Note: Requires PostgreSQL with full-text search support.
        Falls back to simple ILIKE search if not available.
        
        Args:
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            Dictionary with search results
        """
        try:
            if not query or len(query.strip()) < 2:
                return {
                    "status": "error",
                    "message": "Query must be at least 2 characters"
                }
            
            # For now, using ILIKE as fallback
            # In production with PostgreSQL, you could use:
            # from sqlalchemy import func
            # query_vector = func.to_tsquery('english', query)
            # Article.title_search.match(query_vector)
            
            search_pattern = f"%{query}%"
            
            articles = self.db.query(Article).filter(
                or_(
                    Article.title.ilike(search_pattern),
                    Article.content.ilike(search_pattern),
                    Article.author.ilike(search_pattern)
                )
            ).offset(skip).limit(limit).all()
            
            total = self.db.query(Article).filter(
                or_(
                    Article.title.ilike(search_pattern),
                    Article.content.ilike(search_pattern),
                    Article.author.ilike(search_pattern)
                )
            ).count()
            
            logger.info(f"Full-text search for '{query}': found {len(articles)} results")
            
            return {
                "status": "success",
                "query": query,
                "search_type": "fulltext",
                "total": total,
                "count": len(articles),
                "skip": skip,
                "limit": limit,
                "articles": [self._format_article(article) for article in articles]
            }
        except Exception as e:
            logger.error(f"Full-text search failed: {str(e)}")
            # Fallback to simple search
            return self.simple_search(query, skip, limit)
    
    def search_by_author(
        self,
        author: str,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search articles by author.
        
        Args:
            author: Author name to search for
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            Dictionary with search results
        """
        try:
            articles = self.db.query(Article).filter(
                Article.author.ilike(f"%{author}%")
            ).offset(skip).limit(limit).all()
            
            total = self.db.query(Article).filter(
                Article.author.ilike(f"%{author}%")
            ).count()
            
            logger.info(f"Author search for '{author}': found {len(articles)} results")
            
            return {
                "status": "success",
                "search_type": "author",
                "query": author,
                "total": total,
                "count": len(articles),
                "skip": skip,
                "limit": limit,
                "articles": [self._format_article(article) for article in articles]
            }
        except Exception as e:
            logger.error(f"Author search failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }
    
    def search_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search articles within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            Dictionary with search results
        """
        try:
            articles = self.db.query(Article).filter(
                and_(
                    Article.published_at >= start_date,
                    Article.published_at <= end_date
                )
            ).offset(skip).limit(limit).all()
            
            total = self.db.query(Article).filter(
                and_(
                    Article.published_at >= start_date,
                    Article.published_at <= end_date
                )
            ).count()
            
            logger.info(f"Date range search ({start_date} to {end_date}): found {len(articles)} results")
            
            return {
                "status": "success",
                "search_type": "date_range",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total": total,
                "count": len(articles),
                "skip": skip,
                "limit": limit,
                "articles": [self._format_article(article) for article in articles]
            }
        except Exception as e:
            logger.error(f"Date range search failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }
    
    def search_statistics(self) -> Dict[str, Any]:
        """Get search statistics about articles.
        
        Returns:
            Dictionary with statistics
        """
        try:
            total_articles = self.db.query(Article).count()
            
            # Get unique authors
            unique_authors = self.db.query(
                func.count(func.distinct(Article.author))
            ).scalar() or 0
            
            # Get date range
            first_article = self.db.query(Article).order_by(
                Article.published_at.asc()
            ).first()
            latest_article = self.db.query(Article).order_by(
                Article.published_at.desc()
            ).first()
            
            return {
                "status": "success",
                "statistics": {
                    "total_articles": total_articles,
                    "unique_authors": unique_authors,
                    "first_publication": first_article.published_at.isoformat() if first_article else None,
                    "latest_publication": latest_article.published_at.isoformat() if latest_article else None
                }
            }
        except Exception as e:
            logger.error(f"Statistics retrieval failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve statistics: {str(e)}"
            }
    
    def _format_article(self, article: Article) -> Dict[str, Any]:
        """Format article for response.
        
        Args:
            article: Article model instance
            
        Returns:
            Formatted article dictionary
        """
        return {
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "content": article.content[:200] + "..." if len(article.content) > 200 else article.content,
            "url": article.url,
            "author": article.author,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "featured_image": article.featured_image
        }
