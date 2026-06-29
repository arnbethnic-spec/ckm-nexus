"""WordPress content synchronization service."""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.article import Article
from app.integrations.wordpress.client import WordPressClient
from app.core.logging import logger


class WordPressSyncService:
    """Service for syncing WordPress posts to database."""
    
    def __init__(self, db: Session):
        """Initialize sync service with database session."""
        self.db = db
    
    def sync_posts(self, site_url: str, username: str, password: str):
        """Sync posts from WordPress to database.
        
        Args:
            site_url: WordPress site URL
            username: WordPress username
            password: WordPress password or app password
            
        Returns:
            dict with sync results
        """
        try:
            client = WordPressClient(site_url, username, password)
            posts = client.get_posts()
            
            synced_count = 0
            updated_count = 0
            
            for post in posts:
                # Skip drafts and other non-published posts
                if post.get("status") != "publish":
                    continue
                
                # Extract post data
                post_id = post.get("id")
                title = post.get("title", {})
                if isinstance(title, dict):
                    title = title.get("rendered", "")
                
                content = post.get("content", {})
                if isinstance(content, dict):
                    content = content.get("rendered", "")
                
                slug = post.get("slug", "")
                url = post.get("link", "")
                featured_image = post.get("featured_media")
                author = post.get("author")
                published_at = post.get("date_gmt")
                
                # Parse date
                if published_at:
                    published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                
                # Check if article already exists
                existing = self.db.query(Article).filter_by(
                    slug=slug
                ).first()
                
                if existing:
                    # Update existing article
                    existing.title = title
                    existing.content = content
                    existing.url = url
                    existing.featured_image = featured_image
                    existing.author = str(author) if author else None
                    existing.published_at = published_at
                    updated_count += 1
                    logger.info(f"Updated article: {title}")
                else:
                    # Create new article
                    article = Article(
                        title=title,
                        slug=slug,
                        content=content,
                        url=url,
                        featured_image=featured_image,
                        author=str(author) if author else None,
                        published_at=published_at
                    )
                    self.db.add(article)
                    synced_count += 1
                    logger.info(f"Created article: {title}")
            
            # Commit changes
            self.db.commit()
            
            result = {
                "status": "success",
                "synced": synced_count,
                "updated": updated_count,
                "total": synced_count + updated_count,
                "message": f"Synced {synced_count} new posts, updated {updated_count} existing posts"
            }
            logger.info(f"Sync completed: {result}")
            return result
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Sync failed: {str(e)}")
            raise
