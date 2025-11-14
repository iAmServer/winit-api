import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "mode" in data
    assert "fixtures_available" in data


def test_search_valid_request():
    payload = {
        "first_name": "Jose",
        "last_name": "Gracia"
    }
    response = client.post("/api/search", json=payload)
    
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert "total_results" in data
        assert "cases" in data
        assert "metadata" in data
        assert data["query"]["first_name"] == "Jose"
        assert data["query"]["last_name"] == "Gracia"


def test_search_missing_first_name():
    payload = {
        "last_name": "Gracia"
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 422 


def test_search_missing_last_name():
    payload = {
        "first_name": "John"
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 422 


def test_search_empty_names():
    payload = {
        "first_name": "",
        "last_name": ""
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 422 


def test_search_whitespace_names():
    payload = {
        "first_name": "   ",
        "last_name": "   "
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 422 


def test_search_response_schema():
    payload = {
        "first_name": "John",
        "last_name": "Smith"
    }
    response = client.post("/api/search", json=payload)
    
    if response.status_code == 200:
        data = response.json()

        assert isinstance(data["total_results"], int)
        assert isinstance(data["cases"], list)
        
        metadata = data["metadata"]
        assert "search_url" in metadata
        assert "scrape_timestamp" in metadata
        assert "data_source" in metadata

        if data["cases"]:
            case = data["cases"][0]
            assert "case_number" in case
            assert "parties" in case
            assert isinstance(case["parties"], (int, type(None)))


def test_get_case_detail_not_found():
    response = client.get("/api/case/INVALID123")
    assert response.status_code == 404


def test_get_case_detail_invalid_format():
    test_cases = ["", "   ", "12345", "ABC-123"]
    for case_num in test_cases:
        response = client.get(f"/api/case/{case_num}")
        assert response.status_code in [404, 422]


def test_long_names():
    payload = {
        "first_name": "A" * 101,
        "last_name": "B" * 101
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 422


def test_special_characters():
    payload = {
        "first_name": "John-Paul",
        "last_name": "O'Brien"
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code in [200, 404]


def test_numeric_names():
    payload = {
        "first_name": "12345",
        "last_name": "67890"
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=html"])