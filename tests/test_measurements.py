# tests/test_measurements.py
import json
import pytest
from httpx import AsyncClient


class TestMeasurements:
    async def test_add_measurement_success(
        self,
        authenticated_client: AsyncClient,
        test_parameters: list,
        db_session
    ):
        """Успешное добавление замера"""
        # Сначала создаем аквариум
        param_ids = [p.id for p in test_parameters[:3]]
        
        create_response = await authenticated_client.post(
            "/api/aquariums",
            data={
                "name": "Measurement Test Aquarium",
                "inhabitants": "tropical_fish",
                "parameters": param_ids
            }
        )
        assert create_response.status_code == 200
        aquarium_id = create_response.json()["id"]
        
        # Добавляем замеры
        values = {
            "temperature": 25.5,
            "ph": 7.2,
            "ammonia": 0.1
        }
        
        response = await authenticated_client.post(
            f"/api/aquariums/{aquarium_id}/measurements",
            data={
                "date_str": "2026-05-25",
                "values": json.dumps(values)
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_add_measurement_negative_value(
        self,
        authenticated_client: AsyncClient,
        test_parameters: list
    ):
        """Добавление замера с отрицательным значением"""
        # Создаем аквариум
        param_ids = [p.id for p in test_parameters[:3]]
        
        create_response = await authenticated_client.post(
            "/api/aquariums",
            data={
                "name": "Negative Test Aquarium",
                "inhabitants": "tropical_fish",
                "parameters": param_ids
            }
        )
        assert create_response.status_code == 200
        aquarium_id = create_response.json()["id"]
        
        # Добавляем замер с отрицательным значением
        values = {"temperature": -5.0}
        
        response = await authenticated_client.post(
            f"/api/aquariums/{aquarium_id}/measurements",
            data={
                "date_str": "2026-05-25",
                "values": json.dumps(values)
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "отрицательным" in data["error"]

    async def test_add_measurement_invalid_ph(
        self,
        authenticated_client: AsyncClient,
        test_parameters: list
    ):
        """Добавление замера с некорректным pH"""
        # Создаем аквариум
        param_ids = [p.id for p in test_parameters[:3]]
        
        create_response = await authenticated_client.post(
            "/api/aquariums",
            data={
                "name": "Invalid pH Test",
                "inhabitants": "tropical_fish",
                "parameters": param_ids
            }
        )
        assert create_response.status_code == 200
        aquarium_id = create_response.json()["id"]
        
        # Добавляем замер с некорректным pH
        values = {"ph": 15.0}
        
        response = await authenticated_client.post(
            f"/api/aquariums/{aquarium_id}/measurements",
            data={
                "date_str": "2026-05-25",
                "values": json.dumps(values)
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "pH должен быть" in data["error"] or "pH" in data["error"]

    async def test_get_measurements(
        self,
        authenticated_client: AsyncClient,
        test_parameters: list
    ):
        """Получение списка замеров"""
        # Создаем аквариум
        param_ids = [p.id for p in test_parameters[:3]]
        
        create_response = await authenticated_client.post(
            "/api/aquariums",
            data={
                "name": "Get Measurements Test",
                "inhabitants": "tropical_fish",
                "parameters": param_ids
            }
        )
        assert create_response.status_code == 200
        aquarium_id = create_response.json()["id"]
        
        # Добавляем замер
        values = {"temperature": 25.0, "ph": 7.0}
        
        await authenticated_client.post(
            f"/api/aquariums/{aquarium_id}/measurements",
            data={
                "date_str": "2026-05-25",
                "values": json.dumps(values)
            }
        )
        
        # Получаем замеры
        response = await authenticated_client.get(
            f"/api/aquariums/{aquarium_id}/measurements"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)