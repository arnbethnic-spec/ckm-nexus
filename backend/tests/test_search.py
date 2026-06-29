"""Tests for search functionality."""
import pytest
from datetime import datetime, timedelta
from app.services.search_service import SearchService
from app.models.article import Article


# ============================================================================
# Search Service Tests
# ============================================================================

@pytest.fixture
def sample_articles(db):
    """Create sample articles for search testing."""
    articles = [
        Article(
            title="African Mining Industry Growth",
            slug="african-mining-growth",
            content="The African mining industry is experiencing significant growth...",
            author="John Smith",
            published_at=datetime(2024, 1, 15)
        ),
        Article(
            title="Copper Production in Zambia",
            slug="copper-zambia",
            content="Zambia's copper production continues to lead the continent...",
            author="Jane Doe",
            published_at=datetime(2024, 2, 20)
        ),
        Article(
            title="Gold Mining Techniques",
            slug="gold-mining",
            content="Modern gold mining techniques are revolutionizing extraction...",
            author="John Smith",
            published_at=datetime(2024, 3, 10)
        ),
        Article(
            title="Environmental Impact of Mining",
            slug="mining-environment",
            content="The environmental impact of mining operations requires careful management...",
            author="Mary Johnson",
            published_at=datetime(2024, 4, 5)
        ),
        Article(
            title="Lithium Mining for Battery Production",
            slug="lithium-mining",
            content="Lithium mining has become critical for battery production globally...",
            author="Jane Doe",
            published_at=datetime(2024, 5, 12)
        ),
    ]
    
    for article in articles:
        db.add(article)
    db.commit()
    
    return articles


def test_simple_search_basic(db, sample_articles):
    """Test basic simple search."""
    service = SearchService(db)
    
    result = service.simple_search(query="mining", skip=0, limit=10)
    
    assert result["status"] == "success"
    assert result["search_type"] == "simple"
    assert result["total"] >= 4  # Multiple articles contain "mining"
    assert len(result["articles"]) > 0


def test_simple_search_case_insensitive(db, sample_articles):
    """Test that simple search is case insensitive."""
    service = SearchService(db)
    
    result_lower = service.simple_search(query="mining", skip=0, limit=10)
    result_upper = service.simple_search(query="MINING", skip=0, limit=10)
    
    assert result_lower["total"] == result_upper["total"]


def test_simple_search_pagination(db, sample_articles):
    """Test simple search pagination."""
    service = SearchService(db)
    
    result_page1 = service.simple_search(query="mining", skip=0, limit=2)
    result_page2 = service.simple_search(query="mining", skip=2, limit=2)
    
    assert len(result_page1["articles"]) <= 2
    assert len(result_page2["articles"]) <= 2
    assert result_page1["skip"] == 0
    assert result_page2["skip"] == 2


def test_simple_search_min_query_length(db):
    """Test that search requires minimum query length."""
    service = SearchService(db)
    
    result = service.simple_search(query="a", skip=0, limit=10)
    
    assert result["status"] == "error"
    assert "at least 2 characters" in result["message"].lower()


def test_simple_search_by_title(db, sample_articles):
    """Test search by title."""
    service = SearchService(db)
    
    result = service.simple_search(query="Copper Production", skip=0, limit=10)
    
    assert result["status"] == "success"
    assert len(result["articles"]) > 0
    assert any("copper" in article["title"].lower() for article in result["articles"])


def test_simple_search_by_author(db, sample_articles):
    """Test search by author."""
    service = SearchService(db)
    
    result = service.simple_search(query="John Smith", skip=0, limit=10)
    
    assert result["status"] == "success"
    assert len(result["articles"]) > 0


def test_simple_search_no_results(db, sample_articles):
    """Test search with no results."""
    service = SearchService(db)
    
    result = service.simple_search(query="NonexistentQuery12345", skip=0, limit=10)
    
    assert result["status"] == "success"
    assert result["total"] == 0
    assert len(result["articles"]) == 0


def test_advanced_search_by_title(db, sample_articles):
    """Test advanced search by title."""
    service = SearchService(db)
    
    result = service.advanced_search(
        title="Mining",
        skip=0,
        limit=10
    )
    
    assert result["status"] == "success"
    assert result["search_type"] == "advanced"
    assert len(result["articles"]) > 0


def test_advanced_search_by_author(db, sample_articles):
    """Test advanced search by author."""
    service = SearchService(db)
    
    result = service.advanced_search(
        author="Jane Doe",
        skip=0,
        limit=10
    )
    
    assert result["status"] == "success"
    assert len(result["articles"]) > 0
    assert all(article["author"] == "Jane Doe" for article in result["articles"])


def test_advanced_search_by_content(db, sample_articles):
    """Test advanced search by content."""
    service = SearchService(db)
    
    result = service.advanced_search(
        content="environmental",
        skip=0,
        limit=10
    )
    
    assert result["status"] == "success"
    assert len(result["articles"]) > 0


def test_advanced_search_date_range(db, sample_articles):
    """Test advanced search with date range."""
    service = SearchService(db)
    
    start_date = datetime(2024, 2, 1)
    end_date = datetime(2024, 4, 30)
    
    result = service.advanced_search(
        published_after=start_date,
        published_before=end_date,
        skip=0,
        limit=10
    )
    
    assert result["status"] == "success"
    assert len(result["articles"]) > 0
    assert all(
        start_date <= datetime.fromisoformat(article["published_at"]) <= end_date
        for article in result["articles"]
    )


def test_advanced_search_multiple_filters(db, sample_articles):
    """Test advanced search with multiple filters."""
    service = SearchService(db)
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)
    
    result = service.advanced_search(
        author="John Smith",
        published_after=start_date,
        published_before=end_date,
        skip=0,
        limit=10
    )
    
    assert result["status"] == "success"
    assert len(result["articles"]) > 0


def test_search_by_author_endpoint(db, sample_articles):
    """Test author search."""
    service = SearchService(db)
    
    result = service.search_by_author(author="Jane Doe", skip=0, limit=10)
    
    assert result["status"] == "success"
    assert result["search_type"] == "author"
    assert len(result["articles"]) > 0


def test_search_by_date_range(db, sample_articles):
    """Test date range search."""
    service = SearchService(db)
    
    start_date = datetime(2024, 2, 1)
    end_date = datetime(2024, 4, 30)
    
    result = service.search_by_date_range(
        start_date=start_date,
        end_date=end_date,
        skip=0,
        limit=10
    )
    
    assert result["status"] == "success"
    assert result["search_type"] == "date_range"
    assert len(result["articles"]) > 0


def test_fulltext_search(db, sample_articles):
    """Test full-text search."""
    service = SearchService(db)
    
    result = service.fulltext_search(query="mining", skip=0, limit=10)
    
    assert result["status"] == "success"
    assert result["search_type"] == "fulltext"
    assert len(result["articles"]) > 0


def test_search_statistics(db, sample_articles):
    """Test search statistics."""
    service = SearchService(db)
    
    result = service.search_statistics()
    
    assert result["status"] == "success"
    assert "statistics" in result
    assert result["statistics"]["total_articles"] >= 5
    assert result["statistics"]["unique_authors"] >= 3


# ============================================================================
# API Integration Tests
# ============================================================================

def test_api_simple_search(client, db, sample_articles):
    """Test simple search API endpoint."""
    response = client.get("/api/v1/search/articles?q=mining")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "articles" in data


def test_api_search_pagination(client, db, sample_articles):
    """Test search API pagination."""
    response = client.get("/api/v1/search/articles?q=mining&skip=0&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) <= 2


def test_api_search_min_query(client):
    """Test search API with query too short."""
    response = client.get("/api/v1/search/articles?q=a")
    
    assert response.status_code == 400


def test_api_advanced_search_title(client, db, sample_articles):
    """Test advanced search API by title."""
    response = client.get("/api/v1/search/articles/advanced?title=Mining")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_api_advanced_search_author(client, db, sample_articles):
    """Test advanced search API by author."""
    response = client.get("/api/v1/search/articles/advanced?author=John+Smith")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_api_search_by_author(client, db, sample_articles):
    """Test author search API endpoint."""
    response = client.get("/api/v1/search/articles/author/Jane%20Doe")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["search_type"] == "author"


def test_api_search_date_range(client, db, sample_articles):
    """Test date range search API endpoint."""
    response = client.get(
        "/api/v1/search/articles/date-range"
        "?start_date=2024-02-01&end_date=2024-04-30"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_api_search_date_range_invalid(client):
    """Test date range search with invalid dates."""
    response = client.get(
        "/api/v1/search/articles/date-range"
        "?start_date=2024-12-31&end_date=2024-01-01"
    )
    
    assert response.status_code == 400


def test_api_fulltext_search(client, db, sample_articles):
    """Test full-text search API endpoint."""
    response = client.get("/api/v1/search/articles/fulltext?q=mining")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["search_type"] == "fulltext"


def test_api_search_statistics(client, db, sample_articles):
    """Test search statistics API endpoint."""
    response = client.get("/api/v1/search/statistics")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "statistics" in data


def test_api_search_no_criteria(client):
    """Test advanced search without any criteria."""
    response = client.get("/api/v1/search/articles/advanced")
    
    assert response.status_code == 400
