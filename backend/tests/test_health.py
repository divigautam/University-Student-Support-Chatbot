"""Tests for the /health endpoint."""
import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    """GET /health returns 200 with status and project name."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "ChatBot"
