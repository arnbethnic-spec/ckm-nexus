"""Comprehensive tests for website management system."""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock
from app.models.website import Website
from app.repositories.website_repository import WebsiteRepository
from app.services.website_service import WebsiteService
from app.security.encryption import EncryptionService


# ============================================================================
# Encryption Service Tests
# ============================================================================

def test_encryption_service_encrypt_decrypt():
    """Test encryption and decryption."""
    service = EncryptionService()
    
    plaintext = "super_secret_password_123!"
    encrypted = service.encrypt(plaintext)
    
    assert encrypted != plaintext
    decrypted = service.decrypt(encrypted)
    assert decrypted == plaintext


def test_encryption_service_different_encryptions():
    """Test that same plaintext produces different ciphertexts."""
    service = EncryptionService()
    
    plaintext = "password"
    encrypted1 = service.encrypt(plaintext)
    encrypted2 = service.encrypt(plaintext)
    
    # Due to Fernet's IV, same plaintext produces different ciphertexts
    assert encrypted1 != encrypted2
    # But both decrypt to the same value
    assert service.decrypt(encrypted1) == plaintext
    assert service.decrypt(encrypted2) == plaintext


# ============================================================================
# Website Repository Tests
# ============================================================================

def test_repository_create_website(db):
    """Test creating a website via repository."""
    repo = WebsiteRepository(db)
    
    website = Website(
        name="Test Site",
        base_url="https://example.com",
        username="admin",
        encrypted_password="encrypted_pass"
    )
    
    created = repo.create(website)
    
    assert created.id is not None
    assert created.name == "Test Site"
    assert created.is_active is True


def test_repository_get_website_by_id(db):
    """Test retrieving website by ID."""
    repo = WebsiteRepository(db)
    
    website = Website(
        name="Test Site",
        base_url="https://example.com",
        username="admin",
        encrypted_password="encrypted_pass"
    )
    created = repo.create(website)
    
    retrieved = repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.name == "Test Site"


def test_repository_list_websites(db):
    """Test listing websites."""
    repo = WebsiteRepository(db)
    
    # Create multiple websites
    for i in range(3):
        website = Website(
            name=f"Site {i}",
            base_url=f"https://example{i}.com",
            username="admin",
            encrypted_password="pass"
        )
        repo.create(website)
    
    websites = repo.list_all()
    assert len(websites) >= 3


def test_repository_update_website(db):
    """Test updating a website."""
    repo = WebsiteRepository(db)
    
    website = Website(
        name="Original",
        base_url="https://example.com",
        username="admin",
        encrypted_password="pass"
    )
    created = repo.create(website)
    
    updated = repo.update(created.id, name="Updated")
    assert updated.name == "Updated"


def test_repository_delete_website(db):
    """Test deleting a website."""
    repo = WebsiteRepository(db)
    
    website = Website(
        name="Delete Me",
        base_url="https://example.com",
        username="admin",
        encrypted_password="pass"
    )
    created = repo.create(website)
    
    deleted = repo.delete(created.id)
    assert deleted is True
    assert repo.get_by_id(created.id) is None


def test_repository_enable_disable(db):
    """Test enabling/disabling websites."""
    repo = WebsiteRepository(db)
    
    website = Website(
        name="Test",
        base_url="https://example.com",
        username="admin",
        encrypted_password="pass",
        is_active=True
    )
    created = repo.create(website)
    
    disabled = repo.disable(created.id)
    assert disabled.is_active is False
    
    enabled = repo.enable(created.id)
    assert enabled.is_active is True


# ============================================================================
# Website Service Tests
# ============================================================================

def test_service_validate_url():
    """Test URL validation."""
    db = MagicMock()
    service = WebsiteService(db)
    
    assert service.validate_url("https://example.com") is True
    assert service.validate_url("http://example.com") is True
    assert service.validate_url("invalid-url") is False
    assert service.validate_url("ftp://example.com") is False


@patch('app.services.website_service.requests.get')
def test_service_test_connection_success(mock_get):
    """Test successful connection test."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "name": "Test WordPress",
        "namespaces": ["wp/v2"]
    }
    mock_get.return_value = mock_response
    
    db = MagicMock()
    service = WebsiteService(db)
    
    result = service.test_wordpress_connection(
        "https://example.com",
        "admin",
        "pass"
    )
    
    assert result["status"] == "success"
    assert result["connected"] is True


@patch('app.services.website_service.requests.get')
def test_service_test_connection_failed(mock_get):
    """Test failed connection test."""
    import requests
    mock_get.side_effect = requests.exceptions.ConnectionError()
    
    db = MagicMock()
    service = WebsiteService(db)
    
    result = service.test_wordpress_connection(
        "https://example.com",
        "admin",
        "pass"
    )
    
    assert result["status"] == "error"
    assert result["connected"] is False


@patch('app.services.website_service.requests.get')
def test_service_create_website_success(mock_get, db):
    """Test successful website creation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "name": "Test",
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


def test_service_create_website_invalid_url(db):
    """Test creating website with invalid URL."""
    service = WebsiteService(db)
    
    result = service.create_website(
        name="Bad",
        base_url="invalid",
        username="admin",
        password="pass",
        test_connection=False
    )
    
    assert result["status"] == "error"


def test_service_list_websites(db):
    """Test listing websites."""
    service = WebsiteService(db)
    
    result = service.list_websites()
    
    assert result["status"] == "success"
    assert "websites" in result


# ============================================================================
# API Integration Tests
# ============================================================================

def test_api_create_website_v1(client):
    """Test creating website via v1 API."""
    with patch('app.services.website_service.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "name": "Test",
            "namespaces": ["wp/v2"]
        }
        mock_get.return_value = mock_response
        
        response = client.post(
            "/api/v1/websites/",
            json={
                "name": "My Website",
                "base_url": "https://example.com",
                "username": "admin",
                "password": "pass",
                "test_connection": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


def test_api_list_websites_v1(client):
    """Test listing websites via v1 API."""
    response = client.get("/api/v1/websites/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "websites" in data


def test_api_get_website_not_found(client):
    """Test getting non-existent website."""
    fake_id = uuid4()
    response = client.get(f"/api/v1/websites/{fake_id}")
    
    assert response.status_code == 404


def test_api_delete_website_not_found(client):
    """Test deleting non-existent website."""
    fake_id = uuid4()
    response = client.delete(f"/api/v1/websites/{fake_id}")
    
    assert response.status_code == 404


def test_api_test_connection_not_found(client):
    """Test connection test endpoint with non-existent website."""
    fake_id = uuid4()
    response = client.post(f"/api/v1/websites/{fake_id}/test")
    
    assert response.status_code == 404


def test_api_sync_website_not_found(client):
    """Test sync endpoint with non-existent website."""
    fake_id = uuid4()
    response = client.post(f"/api/v1/websites/{fake_id}/sync")
    
    assert response.status_code == 404


def test_api_create_website_invalid_url(client):
    """Test creating website with invalid URL."""
    response = client.post(
        "/api/v1/websites/",
        json={
            "name": "Bad",
            "base_url": "not-a-url",
            "username": "admin",
            "password": "pass",
            "test_connection": False
        }
    )
    
    assert response.status_code == 400


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_workflow_create_and_retrieve(db, client):
    """Test full workflow: create website and retrieve it."""
    with patch('app.services.website_service.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "name": "WordPress Site",
            "namespaces": ["wp/v2"]
        }
        mock_get.return_value = mock_response
        
        # Create website
        create_response = client.post(
            "/api/v1/websites/",
            json={
                "name": "Integration Test",
                "base_url": "https://integration.test",
                "username": "testuser",
                "password": "testpass",
                "test_connection": True
            }
        )
        
        assert create_response.status_code == 200
        created_data = create_response.json()
        website_id = created_data["website"]["id"]
        
        # Retrieve website
        get_response = client.get(f"/api/v1/websites/{website_id}")
        assert get_response.status_code == 200
        
        retrieved_data = get_response.json()
        assert retrieved_data["website"]["name"] == "Integration Test"
        assert retrieved_data["website"]["base_url"] == "https://integration.test"


def test_password_encryption_in_storage(db):
    """Test that passwords are encrypted when stored."""
    service = WebsiteService(db)
    
    original_password = "MySecurePassword123!"
    
    # Create website
    result = service.create_website(
        name="Encryption Test",
        base_url="https://encrypt.test",
        username="admin",
        password=original_password,
        test_connection=False
    )
    
    assert result["status"] == "success"
    
    # Get the website from database
    website = service.repository.get_by_id(UUID(result["website"]["id"]))
    
    # Verify password is encrypted in storage
    assert website.encrypted_password != original_password
    
    # Verify we can decrypt it
    decrypted = service._decrypt_password(website.encrypted_password)
    assert decrypted == original_password


class UUID:
    """UUID wrapper for test compatibility."""
    def __init__(self, id_str):
        from uuid import UUID as PyUUID
        self.id = PyUUID(id_str)
    
    def __eq__(self, other):
        if isinstance(other, UUID):
            return self.id == other.id
        return self.id == other
