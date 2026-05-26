# tests/test_aquariums.py
import pytest
from httpx import AsyncClient


class TestAquariums:
    async def test_create_aquarium_success(
        self, 
        authenticated_client: AsyncClient,
        test_parameters: list
    ):
        """Успешное создание аквариума"""
        param_ids = [p.id for p in test_parameters[:3]]
        
        response = await authenticated_client.post(
            "/api/aquariums",
            data={
                "name": "My New Aquarium",
                "inhabitants": "tropical_fish",
                "parameters": param_ids
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My New Aquarium"
        assert "id" in data

    async def test_create_aquarium_empty_name(
        self, 
        authenticated_client: AsyncClient,
        test_parameters: list
    ):
        """Создание аквариума с пустым названием"""
        param_ids = [p.id for p in test_parameters[:3]]
        
        response = await authenticated_client.post(
            "/api/aquariums",
            data={
                "name": "   ",
                "inhabitants": "tropical_fish",
                "parameters": param_ids
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "Название" in data["error"]

    async def test_create_aquarium_no_parameters(
        self,
        authenticated_client: AsyncClient
    ):
        """Создание аквариума без выбора параметров - должно вернуть 400"""
        response = await authenticated_client.post(
            "/api/aquariums",
            data={
                "name": "Test Aquarium",
                "inhabitants": "tropical_fish",
                "parameters": []
            }
        )
        # API возвращает 400, но может вернуть 422 - проверяем оба варианта
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data or "detail" in data

    async def test_get_aquariums(
        self, 
        authenticated_client: AsyncClient,
        test_parameters: list
    ):
        """Получение списка аквариумов"""
        # Создаем аквариум
        param_ids = [p.id for p in test_parameters[:3]]
        
        await authenticated_client.post(
            "/api/aquariums",
            data={
                "name": "Test Get Aquarium",
                "inhabitants": "tropical_fish",
                "parameters": param_ids
            }
        )
        
        response = await authenticated_client.get("/api/aquariums")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_delete_aquarium(
        self, 
        authenticated_client: AsyncClient,
        test_parameters: list
    ):
        """Удаление аквариума"""
        # Создаем аквариум
        param_ids = [p.id for p in test_parameters[:3]]
        
        create_response = await authenticated_client.post(
            "/api/aquariums",
            data={
                "name": "To Delete",
                "inhabitants": "tropical_fish",
                "parameters": param_ids
            }
        )
        assert create_response.status_code == 200
        aquarium_id = create_response.json()["id"]
        
        # Удаляем аквариум
        delete_response = await authenticated_client.delete(
            f"/api/aquariums/{aquarium_id}"
        )
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["success"] is True