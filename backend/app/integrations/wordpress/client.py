"""WordPress client for API communication."""
import httpx
from app.integrations.wordpress.auth import WordPressAuth

class WordPressClient:
    """Client for WordPress REST API."""
    
    def __init__(self, site_url: str, auth: WordPressAuth):
        """Initialize WordPress client."""
        self.site_url = site_url
        self.auth = auth
        self.base_url = f"{site_url}/wp-json/wp/v2"
    
    async def get_posts(self, per_page: int = 10, page: int = 1):
        """Fetch posts from WordPress."""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/posts"
            params = {
                "per_page": per_page,
                "page": page,
            }
            response = await client.get(url, params=params)
            return response.json()
    
    async def get_post(self, post_id: int):
        """Fetch a single post by ID."""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/posts/{post_id}"
            response = await client.get(url)
            return response.json()
