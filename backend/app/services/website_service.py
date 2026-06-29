"""Website service with business logic."""
from uuid import UUID
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import requests
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from app.models.website import Website
from app.repositories.website_repository import WebsiteRepository
from app.core.config import settings
from app.core.logging import logger


class WebsiteService:
    """Service layer for website management with business logic."""
    
    def __init__(self, db: Session):
        """Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.repository = WebsiteRepository(db)
        # For encryption/decryption - in production, load from environment
        self.cipher = Fernet(self._get_encryption_key())
    
    def _get_encryption_key(self) -> bytes:
        """Get encryption key.
        
        In production, this should be loaded from environment or a secure key management service.
        
        Returns:
            Encryption key as bytes
        """
        # For development, generate a test key
        # In production, use: key = os.getenv("ENCRYPTION_KEY").encode()
        return Fernet.generate_key()
    
    def _encrypt_password(self, password: str) -> str:
        """Encrypt a password.
        
        Args:
            password: Plain text password
            
        Returns:
            Encrypted password as string
        """
        encrypted = self.cipher.encrypt(password.encode())
        return encrypted.decode()
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt a password.
        
        Args:
            encrypted_password: Encrypted password string
            
        Returns:
            Decrypted password
        """
        decrypted = self.cipher.decrypt(encrypted_password.encode())
        return decrypted.decode()
    
    def validate_url(self, url: str) -> bool:
        """Validate WordPress site URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            # Check if URL has scheme and netloc
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception as e:
            logger.error(f"URL validation failed: {str(e)}")
            return False
    
    def test_wordpress_connection(self, url: str, username: str, password: str) -> Dict[str, Any]:
        """Test connection to WordPress site.
        
        Args:
            url: WordPress site URL
            username: WordPress username
            password: WordPress password or app password
            
        Returns:
            Dictionary with connection test results
        """
        try:
            # Normalize URL
            url = url.rstrip("/")
            
            # Test basic connectivity
            response = requests.get(
                f"{url}/wp-json",
                auth=(username, password),
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "status": "success",
                "connected": True,
                "site_name": data.get("name", "Unknown"),
                "wordpress_version": data.get("namespaces", []),
                "url": url
            }
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection failed to {url}: {str(e)}")
            return {
                "status": "error",
                "connected": False,
                "error": "Could not connect to WordPress site"
            }
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Authentication failed for {url}: {str(e)}")
            return {
                "status": "error",
                "connected": False,
                "error": "Authentication failed. Check credentials."
            }
        except Exception as e:
            logger.error(f"Unexpected error testing connection: {str(e)}")
            return {
                "status": "error",
                "connected": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def create_website(
        self,
        name: str,
        base_url: str,
        username: str,
        password: str,
        test_connection: bool = True
    ) -> Dict[str, Any]:
        """Create a new website record.
        
        Args:
            name: Website name
            base_url: WordPress site URL
            username: WordPress username
            password: WordPress password or app password
            test_connection: Whether to test connection before creating
            
        Returns:
            Dictionary with creation result and website data
        """
        # Validate URL format
        if not self.validate_url(base_url):
            logger.error(f"Invalid URL format: {base_url}")
            return {
                "status": "error",
                "message": "Invalid URL format. Must be http:// or https://"
            }
        
        # Check if website already exists
        existing = self.repository.get_by_url(base_url)
        if existing:
            logger.warning(f"Website already exists for URL: {base_url}")
            return {
                "status": "error",
                "message": "Website with this URL already exists"
            }
        
        # Test connection if requested
        if test_connection:
            connection_result = self.test_wordpress_connection(base_url, username, password)
            if connection_result["status"] == "error":
                logger.warning(f"Connection test failed for {base_url}")
                return {
                    "status": "error",
                    "message": f"Connection test failed: {connection_result.get('error')}"
                }
        
        # Encrypt password
        encrypted_password = self._encrypt_password(password)
        
        # Create website record
        website = Website(
            name=name,
            base_url=base_url.rstrip("/"),
            username=username,
            encrypted_password=encrypted_password,
            is_active=True
        )
        
        created_website = self.repository.create(website)
        logger.info(f"Website created: {name} ({base_url})")
        
        return {
            "status": "success",
            "message": "Website created successfully",
            "website": {
                "id": str(created_website.id),
                "name": created_website.name,
                "base_url": created_website.base_url,
                "is_active": created_website.is_active
            }
        }
    
    def update_website(
        self,
        website_id: UUID,
        name: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update website record.
        
        Args:
            website_id: UUID of website to update
            name: New website name
            username: New username
            password: New password
            
        Returns:
            Dictionary with update result
        """
        website = self.repository.get_by_id(website_id)
        if not website:
            logger.warning(f"Website not found: {website_id}")
            return {
                "status": "error",
                "message": "Website not found"
            }
        
        update_data = {}
        
        if name:
            update_data["name"] = name
        
        if username:
            update_data["username"] = username
        
        if password:
            update_data["encrypted_password"] = self._encrypt_password(password)
        
        updated_website = self.repository.update(website_id, **update_data)
        logger.info(f"Website updated: {website_id}")
        
        return {
            "status": "success",
            "message": "Website updated successfully",
            "website": {
                "id": str(updated_website.id),
                "name": updated_website.name,
                "base_url": updated_website.base_url
            }
        }
    
    def rotate_credentials(
        self,
        website_id: UUID,
        new_username: str,
        new_password: str
    ) -> Dict[str, Any]:
        """Rotate website credentials.
        
        Args:
            website_id: UUID of website
            new_username: New username
            new_password: New password
            
        Returns:
            Dictionary with rotation result
        """
        website = self.repository.get_by_id(website_id)
        if not website:
            logger.warning(f"Website not found: {website_id}")
            return {
                "status": "error",
                "message": "Website not found"
            }
        
        # Test connection with new credentials
        connection_result = self.test_wordpress_connection(
            website.base_url,
            new_username,
            new_password
        )
        
        if connection_result["status"] == "error":
            logger.warning(f"Credential rotation test failed for {website_id}")
            return {
                "status": "error",
                "message": f"New credentials failed test: {connection_result.get('error')}"
            }
        
        # Update credentials
        encrypted_password = self._encrypt_password(new_password)
        updated_website = self.repository.update(
            website_id,
            username=new_username,
            encrypted_password=encrypted_password
        )
        
        logger.info(f"Credentials rotated for website: {website_id}")
        
        return {
            "status": "success",
            "message": "Credentials rotated successfully",
            "website": {
                "id": str(updated_website.id),
                "name": updated_website.name,
                "username": updated_website.username
            }
        }
    
    def get_website(self, website_id: UUID) -> Dict[str, Any]:
        """Get website details.
        
        Args:
            website_id: UUID of website
            
        Returns:
            Dictionary with website data
        """
        website = self.repository.get_by_id(website_id)
        if not website:
            return {
                "status": "error",
                "message": "Website not found"
            }
        
        return {
            "status": "success",
            "website": {
                "id": str(website.id),
                "name": website.name,
                "base_url": website.base_url,
                "username": website.username,
                "is_active": website.is_active,
                "created_at": website.created_at.isoformat() if website.created_at else None,
                "updated_at": website.updated_at.isoformat() if website.updated_at else None
            }
        }
    
    def list_websites(self, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """List all websites.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            Dictionary with website list
        """
        websites = self.repository.list_all(skip=skip, limit=limit)
        
        return {
            "status": "success",
            "count": len(websites),
            "websites": [
                {
                    "id": str(w.id),
                    "name": w.name,
                    "base_url": w.base_url,
                    "is_active": w.is_active,
                    "created_at": w.created_at.isoformat() if w.created_at else None
                }
                for w in websites
            ]
        }
    
    def delete_website(self, website_id: UUID) -> Dict[str, Any]:
        """Delete website.
        
        Args:
            website_id: UUID of website
            
        Returns:
            Dictionary with deletion result
        """
        deleted = self.repository.delete(website_id)
        
        if not deleted:
            logger.warning(f"Website not found for deletion: {website_id}")
            return {
                "status": "error",
                "message": "Website not found"
            }
        
        logger.info(f"Website deleted: {website_id}")
        
        return {
            "status": "success",
            "message": "Website deleted successfully"
        }
    
    def enable_website(self, website_id: UUID) -> Dict[str, Any]:
        """Enable website.
        
        Args:
            website_id: UUID of website
            
        Returns:
            Dictionary with result
        """
        website = self.repository.enable(website_id)
        
        if not website:
            return {
                "status": "error",
                "message": "Website not found"
            }
        
        logger.info(f"Website enabled: {website_id}")
        
        return {
            "status": "success",
            "message": "Website enabled",
            "website": {
                "id": str(website.id),
                "name": website.name,
                "is_active": website.is_active
            }
        }
    
    def disable_website(self, website_id: UUID) -> Dict[str, Any]:
        """Disable website.
        
        Args:
            website_id: UUID of website
            
        Returns:
            Dictionary with result
        """
        website = self.repository.disable(website_id)
        
        if not website:
            return {
                "status": "error",
                "message": "Website not found"
            }
        
        logger.info(f"Website disabled: {website_id}")
        
        return {
            "status": "success",
            "message": "Website disabled",
            "website": {
                "id": str(website.id),
                "name": website.name,
                "is_active": website.is_active
            }
        }
