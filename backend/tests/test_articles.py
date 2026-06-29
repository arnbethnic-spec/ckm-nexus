"""Tests for article CRUD endpoints."""
import pytest
from datetime import datetime

def test_create_article(client):
    """Test creating a new article."""
    article_data = {
        "title": "Mining News",
        "slug": "mining-news",
        "content": "Latest mining news",
        "url": "https://example.com/mining-news",
        "author": "John Doe"
    }
    response = client.post("/articles/", json=article_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Mining News"
    assert response.json()["slug"] == "mining-news"

def test_list_articles(client):
    """Test listing articles."""
    # Create an article first
    article_data = {
        "title": "Test Article",
        "slug": "test-article",
        "content": "Test content",
    }
    client.post("/articles/", json=article_data)
    
    # List articles
    response = client.get("/articles/")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["title"] == "Test Article"

def test_get_article(client):
    """Test getting a specific article."""
    # Create an article
    article_data = {
        "title": "Single Article",
        "slug": "single-article",
        "content": "Content",
    }
    create_response = client.post("/articles/", json=article_data)
    article_id = create_response.json()["id"]
    
    # Get the article
    response = client.get(f"/articles/{article_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single Article"

def test_update_article(client):
    """Test updating an article."""
    # Create an article
    article_data = {
        "title": "Original Title",
        "slug": "original-title",
        "content": "Original content",
    }
    create_response = client.post("/articles/", json=article_data)
    article_id = create_response.json()["id"]
    
    # Update the article
    update_data = {"title": "Updated Title"}
    response = client.put(f"/articles/{article_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

def test_delete_article(client):
    """Test deleting an article."""
    # Create an article
    article_data = {
        "title": "Article to Delete",
        "slug": "article-to-delete",
        "content": "Content",
    }
    create_response = client.post("/articles/", json=article_data)
    article_id = create_response.json()["id"]
    
    # Delete the article
    response = client.delete(f"/articles/{article_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = client.get(f"/articles/{article_id}")
    assert get_response.status_code == 404

def test_search_articles(client):
    """Test searching articles."""
    # Create articles
    articles = [
        {"title": "Mining in Africa", "slug": "mining-africa", "content": "African mining news"},
        {"title": "Tech News", "slug": "tech-news", "content": "Technology updates"},
    ]
    for article in articles:
        client.post("/articles/", json=article)
    
    # Search for mining
    response = client.get("/articles/search/mining")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert "Mining" in response.json()[0]["title"]

def test_duplicate_slug_error(client):
    """Test that duplicate slugs are rejected."""
    article_data = {
        "title": "Article 1",
        "slug": "duplicate",
        "content": "Content",
    }
    client.post("/articles/", json=article_data)
    
    # Try to create another with same slug
    response = client.post("/articles/", json=article_data)
    assert response.status_code == 400
