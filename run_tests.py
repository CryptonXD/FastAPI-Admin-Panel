import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # Запускаем тесты с использованием pytest
    import pytest
    
    # Если тесты падают с ошибкой import, можно добавить отладочную информацию
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"sys.path: {sys.path}")
    
    # Запускаем тесты
    sys.exit(pytest.main(["-v", "app/tests/test_api.py"]))
