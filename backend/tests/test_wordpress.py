"""Tests for WordPress integration."""
import pytest
from unittest.mock import patch, MagicMock

def test_wordpress_client_initialization():
    """Test WordPress client initialization."""
    from app.integrations.wordpress.client import WordPressClient
    
    client = WordPressClient("https://example.com", "user", "password")
    assert client.url == "https://example.com"
    assert client.session is not None

def test_wordpress_auth_credentials():
    """Test WordPress auth credentials."""
    from app.integrations.wordpress.auth import WordPressAuth
    
    auth = WordPressAuth(
        auth_type="app_password",
        username="user",
        password="pass"
    )
    creds = auth.get_credentials()
    assert creds == ("user", "pass")

@patch('app.integrations.wordpress.client.requests.Session.get')
def test_get_posts(mock_get):
    """Test fetching posts from WordPress."""
    from app.integrations.wordpress.client import WordPressClient
    
    # Mock the response
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"id": 1, "title": {"rendered": "Post 1"}},
        {"id": 2, "title": {"rendered": "Post 2"}},
    ]
    mock_get.return_value = mock_response
    
    client = WordPressClient("https://example.com", "user", "password")
    posts = client.get_posts()
    
    assert len(posts) == 2
    mock_get.assert_called_once()

@patch('app.integrations.wordpress.client.requests.Session.get')
def test_get_categories(mock_get):
    """Test fetching categories from WordPress."""
    from app.integrations.wordpress.client import WordPressClient
    
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"id": 1, "name": "Mining"},
        {"id": 2, "name": "Tech"},
    ]
    mock_get.return_value = mock_response
    
    client = WordPressClient("https://example.com", "user", "password")
    categories = client.get_categories()
    
    assert len(categories) == 2
    assert categories[0]["name"] == "Mining"

def test_wordpress_test_endpoint(client):
    """Test WordPress connection test endpoint."""
    # This will fail without real credentials, but tests the endpoint exists
    response = client.get(
        "/wordpress/test",
        params={
            "site_url": "https://example.com",
            "username": "user",
            "password": "pass"
        }
    )
    # Endpoint should either return success or connection error
    assert response.status_code in [200, 400]

@patch('app.integrations.wordpress.client.WordPressClient.get_posts')
def test_sync_posts_endpoint(mock_get_posts, client, db):
    """Test WordPress sync endpoint."""
    # Mock WordPress posts
    mock_get_posts.return_value = [
        {
            "id": 1,
            "status": "publish",
            "title": {"rendered": "Test Post"},
            "content": {"rendered": "Test content"},
            "slug": "test-post",
            "link": "https://example.com/test-post",
            "featured_media": None,
            "author": 1,
            "date_gmt": "2024-01-01T00:00:00Z"
        }
    ]
    
    response = client.post(
        "/wordpress/sync",
        params={
            "site_url": "https://example.com",
            "username": "user",
            "password": "pass"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
