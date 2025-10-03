"""
Pytest configuration and fixtures for Fantasy Grid tests
"""
import pytest
import os
from app import create_app


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    os.environ['TESTING'] = 'True'
    os.environ['CSRF_ENABLED'] = 'False'  # Disable CSRF for testing
    os.environ['REDIS_URL'] = 'memory://'  # Use in-memory rate limiting

    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })

    yield app


@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI test runner"""
    return app.test_cli_runner()
