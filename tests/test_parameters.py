# tests/test_parameters.py
import pytest
from httpx import AsyncClient


class TestParameters:
    async def test_get_parameters(
        self,
        client: AsyncClient,
        test_parameters  # фикстура уже создает параметры
    ):
        """Получение списка всех параметров"""
        response = await client.get("/api/parameters")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Параметры должны быть созданы фикстурой test_parameters
        assert len(data) >= 5
        
        if data:
            param = data[0]
            assert "id" in param
            assert "name" in param
            assert "display_name" in param
            assert "unit" in param

    async def test_parameters_contain_expected(
        self,
        client: AsyncClient,
        test_parameters  # фикстура создает параметры
    ):
        """Проверка наличия основных параметров"""
        response = await client.get("/api/parameters")
        assert response.status_code == 200
        data = response.json()
        param_names = [p["name"] for p in data]
        
        expected_params = ["temperature", "ph", "ammonia", "nitrites", "nitrates"]
        for param in expected_params:
            assert param in param_names, f"Parameter {param} not found"