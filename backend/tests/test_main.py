"""
Main Application Tests
Run with: pytest tests/test_main.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the app instance from main
from main import app

@pytest.fixture
def client():
    """
    Test client fixture that handles the lifespan (startup/shutdown)
    'with' statement triggers the @asynccontextmanager lifespan in main.py
    """
    with TestClient(app) as c:
        yield c

def test_root_endpoint(client):
    """Test the root GET endpoint for status and version"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AegisAI"
    assert data["status"] == "operational"
    assert "version" in data

def test_docs_accessible(client):
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200

@patch("main.db_service")
@patch("main.settings")
def test_lifespan_startup_shutdown(mock_settings, mock_db_service):
    """
    Test the startup and shutdown logic specifically.
    - Startup: Creates evidence directory.
    - Shutdown: Cleans up old incidents.
    """
    # Setup mocks
    mock_settings.EVIDENCE_DIR = MagicMock(spec=Path)
    mock_settings.MAX_EVIDENCE_AGE_DAYS = 30
    mock_db_service.cleanup_old_incidents.return_value = 5
    
    # Trigger lifespan by using the context manager
    with TestClient(app):
        # Startup checks
        mock_settings.EVIDENCE_DIR.mkdir.assert_called_once_with(
            exist_ok=True, parents=True
        )
    
    # Shutdown checks (after 'with' block ends)
    mock_db_service.cleanup_old_incidents.assert_called_once_with(30)

def test_cors_headers(client):
    """Test that CORS middleware is active"""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Requested-With",
        },
    )
    # If the origin is allowed in settings, this should be 200
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers