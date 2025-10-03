"""
API tests for security endpoints
"""
import pytest


@pytest.mark.api
def test_csrf_token_endpoint(client):
    """Test CSRF token generation endpoint"""
    response = client.get('/api/security/csrf-token')
    assert response.status_code == 200

    data = response.get_json()
    assert 'csrf_token' in data
    assert data['csrf_token'] is not None
    assert len(data['csrf_token']) > 0


@pytest.mark.api
def test_csrf_token_in_response(client):
    """Test CSRF token is returned in response"""
    response = client.get('/api/security/csrf-token')
    assert response.status_code == 200

    data = response.get_json()
    assert 'csrf_token' in data
    assert isinstance(data['csrf_token'], str)
