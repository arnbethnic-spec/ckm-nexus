"""WordPress authentication methods."""

class WordPressAuth:
    """Handle WordPress authentication."""
    
    def __init__(self, auth_type: str = "app_password", **kwargs):
        """Initialize WordPress auth.
        
        Args:
            auth_type: Type of authentication ('app_password', 'jwt', 'oauth')
            **kwargs: Authentication credentials
        """
        self.auth_type = auth_type
        self.credentials = kwargs
    
    def get_credentials(self):
        """Get authentication credentials tuple."""
        if self.auth_type == "app_password":
            return (self.credentials.get("username"), self.credentials.get("password"))
        return None
