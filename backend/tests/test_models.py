"""Tests for database models."""
import pytest
from datetime import datetime
from app.models.article import Article

def test_article_model_creation(db):
    """Test creating an article model instance."""
    article = Article(
        title="Test Article",
        slug="test-article",
        content="Test content",
        url="https://example.com",
        author="Test Author",
        published_at=datetime.now()
    )
    db.add(article)
    db.commit()
    
    # Verify the article was created
    retrieved = db.query(Article).filter_by(slug="test-article").first()
    assert retrieved is not None
    assert retrieved.title == "Test Article"
    assert retrieved.author == "Test Author"

def test_article_unique_slug(db):
    """Test that article slugs are unique."""
    article1 = Article(
        title="Article 1",
        slug="unique-slug",
        content="Content 1"
    )
    db.add(article1)
    db.commit()
    
    # Try to create another with same slug
    article2 = Article(
        title="Article 2",
        slug="unique-slug",
        content="Content 2"
    )
    db.add(article2)
    
    with pytest.raises(Exception):  # Should raise integrity error
        db.commit()

def test_article_optional_fields(db):
    """Test that optional fields can be null."""
    article = Article(
        title="Minimal Article",
        slug="minimal",
        content="Content"
    )
    db.add(article)
    db.commit()
    
    retrieved = db.query(Article).filter_by(slug="minimal").first()
    assert retrieved.url is None
    assert retrieved.author is None
    assert retrieved.featured_image is None
