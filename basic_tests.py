"""
Базовые тесты для проверки работоспособности API
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path для корректных импортов
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import unittest
from fastapi.testclient import TestClient
from main import app

class TestAPI(unittest.TestCase):
    """Базовые тесты API"""
    
    def setUp(self):
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Тест главной страницы"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("Welcome to", data["message"])
    
    def test_docs_available(self):
        """Проверка доступности Swagger документации"""
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)
    
    def test_openapi_json(self):
        """Проверка доступности OpenAPI JSON"""
        response = self.client.get("/api/v1/openapi.json")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
