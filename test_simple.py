import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_root():
    """
    Тест главной страницы API
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Welcome to" in response.json()["message"]

def test_api_docs():
    """
    Тест доступности документации API
    """
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()

def test_openapi_json():
    """
    Тест доступности JSON-документации OpenAPI
    """
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()
    assert "components" in response.json()
