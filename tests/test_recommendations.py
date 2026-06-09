
import json
import pytest
from httpx import AsyncClient


class TestRecommendations:
    async def test_get_recommendations(
        self,
        authenticated_client: AsyncClient,
        test_aquarium_with_params
    ):
        """Получение рекомендаций для аквариума"""
        values = {
            "temperature": 32.0,
            "ammonia": 0.5,
            "ph": 8.0
        }
        
        await authenticated_client.post(
            f"/api/aquariums/{test_aquarium_with_params.id}/measurements",
            data={
                "date_str": "2026-05-25",
                "values": json.dumps(values)
            }
        )
        
        response = await authenticated_client.get(
            f"/api/recommendations/{test_aquarium_with_params.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "has_issues" in data

    async def test_get_recommendations_aquarium_not_found(
        self,
        authenticated_client: AsyncClient
    ):
        """Рекомендации для несуществующего аквариума"""
        response = await authenticated_client.get("/api/recommendations/99999")
        assert response.status_code == 200
        data = response.json()
        assert data["recommendations"] == []
        assert data["has_issues"] is False
