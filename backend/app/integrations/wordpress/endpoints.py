"""WordPress API endpoints."""
from fastapi import APIRouter, HTTPException
from app.integrations.wordpress.client import WordPressClient
from app.integrations.wordpress.auth import WordPressAuth

router = APIRouter(prefix="/wordpress", tags=["wordpress"])

@router.get("/test")
def test_wordpress_connection(
    site_url: str,
    username: str,
    password: str
):
    """Test connection to WordPress site."""
    try:
        client = WordPressClient(site_url, username, password)
        
        # Test basic connection
        response = client.session.get(f"{client.url}/wp-json")
        response.raise_for_status()
        
        data = response.json()
        wordpress_version = data.get("name", "Unknown")
        site_name = data.get("description", "Unknown")
        
        return {
            "status": "connected",
            "wordpress_version": wordpress_version,
            "site": site_name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/posts")
def get_wordpress_posts(
    site_url: str,
    username: str,
    password: str
):
    """Fetch posts from WordPress site."""
    try:
        client = WordPressClient(site_url, username, password)
        posts = client.get_posts()
        return {"data": posts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/categories")
def get_wordpress_categories(
    site_url: str,
    username: str,
    password: str
):
    """Fetch categories from WordPress site."""
    try:
        client = WordPressClient(site_url, username, password)
        categories = client.get_categories()
        return {"data": categories}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tags")
def get_wordpress_tags(
    site_url: str,
    username: str,
    password: str
):
    """Fetch tags from WordPress site."""
    try:
        client = WordPressClient(site_url, username, password)
        tags = client.get_tags()
        return {"data": tags}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
