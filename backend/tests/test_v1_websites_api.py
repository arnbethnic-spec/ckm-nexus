"""Tests for v1 websites API endpoints."""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock


def test_create_website_v1(client):
    """Test creating a website via v1 API."""
    with patch('app.services.website_service.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "name": "Test Site",
            "namespaces": ["wp/v2"]
        }
        mock_get.return_value = mock_response
        
        response = client.post(
            "/api/v1/websites/",
            json={
                "name": "Test Website",
                "base_url": "https://example.com",
                "username": "admin",
                "password": "password",
                "test_connection": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "website" in data


def test_list_websites_v1(client):
    """Test listing websites via v1 API."""
    response = client.get("/api/v1/websites/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "websites" in data
    assert "count" in data


def test_get_website_v1_not_found(client):
    """Test getting non-existent website via v1 API."""
    fake_id = uuid4()
    response = client.get(f"/api/v1/websites/{fake_id}")
    
    assert response.status_code == 404


def test_update_website_v1_not_found(client):
    """Test updating non-existent website via v1 API."""
    fake_id = uuid4()
    response = client.put(
        f"/api/v1/websites/{fake_id}",
        json={"name": "Updated Name"}
    )
    
    assert response.status_code == 404


def test_delete_website_v1_not_found(client):
    """Test deleting non-existent website via v1 API."""
    fake_id = uuid4()
    response = client.delete(f"/api/v1/websites/{fake_id}")
    
    assert response.status_code == 404


def test_test_connection_v1_not_found(client):
    """Test connection endpoint with non-existent website."""
    fake_id = uuid4()
    response = client.post(f"/api/v1/websites/{fake_id}/test")
    
    assert response.status_code == 404


def test_sync_website_v1_not_found(client):
    """Test sync endpoint with non-existent website."""
    fake_id = uuid4()
    response = client.post(f"/api/v1/websites/{fake_id}/sync")
    
    assert response.status_code == 404


def test_create_website_invalid_url_v1(client):
    """Test creating website with invalid URL via v1 API."""
    response = client.post(
        "/api/v1/websites/",
        json={
            "name": "Bad Website",
            "base_url": "invalid-url",
            "username": "admin",
            "password": "password",
            "test_connection": False
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_create_website_connection_failed_v1(client):
    """Test creating website with failed connection test."""
    import requests
    
    with patch('app.services.website_service.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        response = client.post(
            "/api/v1/websites/",
            json={
                "name": "Test Website",
                "base_url": "https://example.com",
                "username": "admin",
                "password": "password",
                "test_connection": True
            }
        )
        
        assert response.status_code == 400
