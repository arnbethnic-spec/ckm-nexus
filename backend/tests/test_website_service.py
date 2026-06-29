"""Tests for website service."""
import pytest
from unittest.mock import patch, MagicMock
from app.services.website_service import WebsiteService


def test_validate_url():
    """Test URL validation."""
    db = MagicMock()
    service = WebsiteService(db)
    
    assert service.validate_url("https://example.com") is True
    assert service.validate_url("http://example.com") is True
    assert service.validate_url("invalid-url") is False
    assert service.validate_url("ftp://example.com") is False


def test_encrypt_decrypt_password():
    """Test password encryption and decryption."""
    db = MagicMock()
    service = WebsiteService(db)
    
    original = "my_secure_password"
    encrypted = service._encrypt_password(original)
    
    assert encrypted != original
    decrypted = service._decrypt_password(encrypted)
    assert decrypted == original


@patch('app.services.website_service.requests.get')
def test_test_wordpress_connection_success(mock_get):
    """Test successful WordPress connection test."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "name": "Test WordPress Site",
        "namespaces": ["wp/v2"]
    }
    mock_get.return_value = mock_response
    
    db = MagicMock()
    service = WebsiteService(db)
    
    result = service.test_wordpress_connection(
        "https://example.com",
        "admin",
        "password"
    )
    
    assert result["status"] == "success"
    assert result["connected"] is True


@patch('app.services.website_service.requests.get')
def test_test_wordpress_connection_failure(mock_get):
    """Test failed WordPress connection test."""
    import requests
    mock_get.side_effect = requests.exceptions.ConnectionError()
    
    db = MagicMock()
    service = WebsiteService(db)
    
    result = service.test_wordpress_connection(
        "https://example.com",
        "admin",
        "password"
    )
    
    assert result["status"] == "error"
    assert result["connected"] is False


def test_create_website_invalid_url(db):
    """Test creating website with invalid URL."""
    service = WebsiteService(db)
    
    result = service.create_website(
        name="Test",
        base_url="invalid-url",
        username="admin",
        password="pass",
        test_connection=False
    )
    
    assert result["status"] == "error"
    assert "Invalid URL format" in result["message"]


@patch('app.services.website_service.requests.get')
def test_create_website_success(mock_get, db):
    """Test successful website creation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "name": "Test Site",
        "namespaces": ["wp/v2"]
    }
    mock_get.return_value = mock_response
    
    service = WebsiteService(db)
    
    result = service.create_website(
        name="Test Site",
        base_url="https://example.com",
        username="admin",
        password="password",
        test_connection=True
    )
    
    assert result["status"] == "success"
    assert "website" in result


def test_list_websites(db):
    """Test listing websites."""
    service = WebsiteService(db)
    
    result = service.list_websites()
    
    assert result["status"] == "success"
    assert "websites" in result
    assert "count" in result


def test_get_website(db):
    """Test getting website."""
    service = WebsiteService(db)
    
    # Create a website first
    from app.models.website import Website
    from app.repositories.website_repository import WebsiteRepository
    
    repo = WebsiteRepository(db)
    website = Website(
        name="Test Site",
        base_url="https://example.com",
        username="admin",
        encrypted_password="encrypted"
    )
    created = repo.create(website)
    
    # Get it
    result = service.get_website(created.id)
    
    assert result["status"] == "success"
    assert result["website"]["name"] == "Test Site"


def test_delete_website(db):
    """Test deleting website."""
    from app.models.website import Website
    from app.repositories.website_repository import WebsiteRepository
    
    repo = WebsiteRepository(db)
    website = Website(
        name="Test Site",
        base_url="https://example.com",
        username="admin",
        encrypted_password="encrypted"
    )
    created = repo.create(website)
    
    service = WebsiteService(db)
    result = service.delete_website(created.id)
    
    assert result["status"] == "success"


def test_enable_disable_website(db):
    """Test enabling and disabling website."""
    from app.models.website import Website
    from app.repositories.website_repository import WebsiteRepository
    
    repo = WebsiteRepository(db)
    website = Website(
        name="Test Site",
        base_url="https://example.com",
        username="admin",
        encrypted_password="encrypted",
        is_active=True
    )
    created = repo.create(website)
    
    service = WebsiteService(db)
    
    # Disable
    result = service.disable_website(created.id)
    assert result["status"] == "success"
    assert result["website"]["is_active"] is False
    
    # Enable
    result = service.enable_website(created.id)
    assert result["status"] == "success"
    assert result["website"]["is_active"] is True
