"""WordPress authentication."""
from typing import Optional

class WordPressAuth:
    """Handle WordPress authentication."""
    
    def __init__(self, username: str = None, password: str = None, api_key: str = None):
        """Initialize WordPress auth."""
        self.username = username
        self.password = password
        self.api_key = api_key
    
    def get_headers(self) -> dict:
        """Get authentication headers."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
