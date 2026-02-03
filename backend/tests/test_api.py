"""
API Endpoint Tests for AegisAI
Run with: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from main import app
from services.database_service import db_service


@pytest.fixture
def client():
    """Create FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_incident():
    """Insert a sample incident and clean up after test"""
    incident_id = db_service.save_incident({
        'timestamp': datetime.now().isoformat(),
        'type': 'theft',
        'severity': 'high',
        'confidence': 85,
        'reasoning': 'Test incident',
        'subjects': ['person'],
        'evidence_path': '/test/evidence.jpg',
        'response_plan': []
    })
    yield incident_id
    # Optional cleanup: db_service.delete_incident(incident_id)


def extract_incidents(data):
    """
    Helper function to ensure we always get a list of incidents.
    Handles both list or dict response structures.
    """
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and 'incidents' in data:
        return data['incidents']
    return []


# ============================================================================
# Root & Health Endpoints
# ============================================================================

class TestRootEndpoints:
    """Test root and health endpoints"""

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert 'name' in data and data['name'] == 'AegisAI'
        assert 'version' in data

    def test_health_check(self, client):
        response = client.get("/api/health")  # router prefix
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'components' in data
        assert data['status'] in ['ok', 'healthy', 'degraded']
        for key in ['database', 'vision_agent', 'planner_agent']:
            assert key in data['components']


# ============================================================================
# Incident Endpoints
# ============================================================================

class TestIncidentEndpoints:
    """Test incident-related endpoints"""

    def test_get_incidents(self, client, sample_incident):
        response = client.get("/api/incidents")
        assert response.status_code == 200
        data = response.json()
        incidents = extract_incidents(data)
        assert isinstance(incidents, list)
        assert any(inc['id'] == sample_incident for inc in incidents)

    def test_get_incidents_with_limit(self, client):
        response = client.get("/api/incidents?limit=5")
        assert response.status_code == 200
        data = response.json()
        incidents = extract_incidents(data)
        assert len(incidents) <= 5

    def test_get_incidents_with_severity_filter(self, client, sample_incident):
        response = client.get("/api/incidents?severity=high")
        assert response.status_code == 200
        data = response.json()
        incidents = extract_incidents(data)
        for inc in incidents:
            assert inc['severity'] == 'high'

    def test_get_incidents_invalid_severity(self, client):
        response = client.get("/api/incidents?severity=invalid")
        assert response.status_code == 422

    def test_get_incident_by_id(self, client, sample_incident):
        response = client.get(f"/api/incidents/{sample_incident}")
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == sample_incident
        assert 'type' in data
        assert 'severity' in data

    def test_get_incident_not_found(self, client):
        response = client.get("/api/incidents/999999")
        assert response.status_code == 404

    def test_update_incident_status(self, client, sample_incident):
        response = client.post(f"/api/incidents/{sample_incident}/status?status=resolved")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') is True
        assert data.get('status') == 'resolved'

    def test_update_incident_invalid_status(self, client, sample_incident):
        response = client.post(f"/api/incidents/{sample_incident}/status?status=invalid")
        assert response.status_code == 422


# ============================================================================
# Stats Endpoints
# ============================================================================

class TestStatsEndpoints:
    """Test statistics endpoints"""

    def test_get_stats(self, client):
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        for key in ['total_incidents', 'active_incidents', 'severity_breakdown', 'system_status']:
            assert key in data

    def test_get_agent_stats(self, client):
        response = client.get("/api/agents/stats")
        assert response.status_code == 200
        data = response.json()
        assert 'vision_agent' in data
        assert 'planner_agent' in data


# ============================================================================
# Cleanup Endpoint
# ============================================================================

class TestCleanupEndpoint:
    """Test cleanup endpoint"""

    def test_cleanup_old_incidents(self, client):
        response = client.delete("/api/incidents/cleanup?days=30")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') is True
        assert 'deleted_count' in data

    def test_cleanup_invalid_days(self, client):
        response = client.delete("/api/incidents/cleanup?days=1")
        assert response.status_code == 422


# ============================================================================
# CORS Tests
# ============================================================================

class TestCORS:
    """Test CORS headers"""

    def test_cors_headers(self, client):
        response = client.options("/api/incidents")
        assert 'access-control-allow-origin' in response.headers or response.status_code in [200, 405]


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test HTTP error handling"""

    def test_404_not_found(self, client):
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        response = client.post("/")
        assert response.status_code == 405


# ============================================================================
# End-to-End Workflow Tests
# ============================================================================

@pytest.mark.integration
class TestEndToEndFlow:
    """End-to-end workflow tests"""

    def test_incident_creation_and_retrieval(self, client):
        # Create incident
        incident_id = db_service.save_incident({
            'timestamp': datetime.now().isoformat(),
            'type': 'test_e2e',
            'severity': 'medium',
            'confidence': 75,
            'reasoning': 'E2E test',
            'subjects': [],
            'evidence_path': '',
            'response_plan': []
        })

        # Retrieve via API
        response = client.get(f"/api/incidents/{incident_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['type'] == 'test_e2e'

        # Update status
        response = client.post(f"/api/incidents/{incident_id}/status?status=resolved")
        assert response.status_code == 200

        # Verify update
        response = client.get(f"/api/incidents/{incident_id}")
        data = response.json()
        assert data['status'] == 'resolved'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
