"""Tests for website repository."""
import pytest
from uuid import uuid4
from app.models.website import Website
from app.repositories.website_repository import WebsiteRepository


def test_create_website(db):
    """Test creating a website record."""
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
    assert created.base_url == "https://example.com"
    assert created.is_active is True


def test_get_by_id(db):
    """Test getting website by ID."""
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


def test_get_by_url(db):
    """Test getting website by URL."""
    repo = WebsiteRepository(db)
    
    website = Website(
        name="Test Site",
        base_url="https://example.com",
        username="admin",
        encrypted_password="encrypted_pass"
    )
    repo.create(website)
    
    retrieved = repo.get_by_url("https://example.com")
    
    assert retrieved is not None
    assert retrieved.base_url == "https://example.com"


def test_list_all(db):
    """Test listing all websites."""
    repo = WebsiteRepository(db)
    
    # Create multiple websites
    for i in range(3):
        website = Website(
            name=f"Site {i}",
            base_url=f"https://example{i}.com",
            username="admin",
            encrypted_password="encrypted_pass"
        )
        repo.create(website)
    
    websites = repo.list_all()
    
    assert len(websites) >= 3


def test_list_active(db):
    """Test listing active websites."""
    repo = WebsiteRepository(db)
    
    # Create active website
    website1 = Website(
        name="Active Site",
        base_url="https://active.com",
        username="admin",
        encrypted_password="encrypted_pass",
        is_active=True
    )
    repo.create(website1)
    
    # Create inactive website
    website2 = Website(
        name="Inactive Site",
        base_url="https://inactive.com",
        username="admin",
        encrypted_password="encrypted_pass",
        is_active=False
    )
    repo.create(website2)
    
    active_websites = repo.list_active()
    
    # Should have at least the active website
    assert any(w.base_url == "https://active.com" for w in active_websites)
    assert not any(w.base_url == "https://inactive.com" for w in active_websites)


def test_update(db):
    """Test updating a website."""
    repo = WebsiteRepository(db)
    
    website = Website(
        name="Original Name",
        base_url="https://example.com",
        username="admin",
        encrypted_password="encrypted_pass"
    )
    created = repo.create(website)
    
    updated = repo.update(created.id, name="Updated Name")
    
    assert updated.name == "Updated Name"


def test_enable_disable(db):
    """Test enabling and disabling websites."""
    repo = WebsiteRepository(db)
    
    website = Website(
        name="Test Site",
        base_url="https://example.com",
        username="admin",
        encrypted_password="encrypted_pass",
        is_active=True
    )
    created = repo.create(website)
    
    # Disable
    disabled = repo.disable(created.id)
    assert disabled.is_active is False
    
    # Enable
    enabled = repo.enable(created.id)
    assert enabled.is_active is True


def test_delete(db):
    """Test deleting a website."""
    repo = WebsiteRepository(db)
    
    website = Website(
        name="Test Site",
        base_url="https://example.com",
        username="admin",
        encrypted_password="encrypted_pass"
    )
    created = repo.create(website)
    
    deleted = repo.delete(created.id)
    
    assert deleted is True
    assert repo.get_by_id(created.id) is None
