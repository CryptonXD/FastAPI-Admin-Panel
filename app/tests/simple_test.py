import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path для корректных импортов
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from fastapi.testclient import TestClient

from main import app  # Импортируем из корня проекта

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
