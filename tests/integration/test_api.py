"""Integration tests for API."""

import pytest
from httpx import AsyncClient, ASGITransport

from chembldiscovery.api.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "ChEMBL Discovery API" in data["message"]


@pytest.mark.asyncio
async def test_health_check():
    """Test health endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_docs_available():
    """Test API documentation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/docs")
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_invalid_disease():
    """Test search with invalid input."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/drugs/search?disease=")
        
        # Empty disease should return 422 for validation error
        assert response.status_code == 422