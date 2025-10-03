# Fantasy Grid Testing

Comprehensive test suite for Fantasy Grid API using pytest.

## Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── unit/                # Unit tests for individual components
│   └── test_analyzer.py
├── integration/         # Integration tests
└── api/                 # API endpoint tests
    ├── test_health.py
    └── test_security.py
```

## Running Tests

### Run all tests
```bash
cd backend
source venv/bin/activate
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest -m unit

# API tests only
pytest -m api

# Integration tests only
pytest -m integration
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/unit/test_analyzer.py
```

### Run specific test
```bash
pytest tests/unit/test_analyzer.py::TestPlayerAnalyzer::test_calculate_matchup_score_best_defense
```

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Slow running tests

## Coverage Requirements

- Minimum coverage: 70%
- Target coverage: 80%+

## Writing Tests

### Unit Test Example
```python
import pytest
from app.services.analyzer import PlayerAnalyzer

@pytest.mark.unit
def test_matchup_score():
    analyzer = PlayerAnalyzer()
    score = analyzer.calculate_matchup_score({}, {'rank': 1})
    assert 0 <= score <= 100
```

### API Test Example
```python
import pytest

@pytest.mark.api
def test_endpoint(client):
    response = client.get('/api/players/search?q=mahomes')
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
```

### Using Fixtures
```python
@pytest.fixture
def sample_player():
    return {
        'id': '123',
        'name': 'Patrick Mahomes',
        'position': 'QB'
    }

def test_with_fixture(sample_player):
    assert sample_player['position'] == 'QB'
```

## Mocking External APIs

Use `responses` library to mock HTTP requests:

```python
import responses

@responses.activate
def test_api_call():
    responses.add(
        responses.GET,
        'https://nfl.wearemachina.com/api/v1/players/123',
        json={'data': {'name': 'Test Player'}},
        status=200
    )

    # Your test here
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run tests
  run: |
    cd backend
    pytest --cov=app --cov-fail-under=70
```

### Pre-commit Hook
```bash
#!/bin/bash
pytest --cov=app --cov-fail-under=70 || exit 1
```

## Test Data

- Use fixtures in `conftest.py` for shared test data
- Mock external API responses
- Use in-memory databases for integration tests

## Troubleshooting

### Import errors
- Ensure you're in the backend directory
- Activate virtual environment: `source venv/bin/activate`

### CSRF errors in tests
- CSRF is disabled in test environment (see conftest.py)

### Rate limiting in tests
- Uses in-memory limiter (no Redis required)
