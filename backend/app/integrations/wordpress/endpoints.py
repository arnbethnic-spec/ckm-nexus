"""WordPress API endpoints."""
from fastapi import APIRouter, HTTPException
from app.integrations.wordpress.client import WordPressClient
from app.integrations.wordpress.auth import WordPressAuth

router = APIRouter(prefix="/wordpress", tags=["wordpress"])

@router.get("/posts")
async def get_wordpress_posts(site_url: str, per_page: int = 10, page: int = 1):
    """Fetch posts from WordPress site."""
    try:
        auth = WordPressAuth()
        client = WordPressClient(site_url, auth)
        posts = await client.get_posts(per_page=per_page, page=page)
        return {"data": posts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
