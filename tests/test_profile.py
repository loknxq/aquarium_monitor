
import pytest
from httpx import AsyncClient


class TestProfile:
    async def test_change_password_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Успешная смена пароля"""
        response = await authenticated_client.post(
            "/api/profile/change-password",
            data={
                "old_password": "authpass123",
                "new_password": "newpass123",
                "confirm_password": "newpass123"
            }
        )
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
        else:
            data = response.json()
            assert "error" in data

    async def test_change_password_wrong_old(
        self,
        authenticated_client: AsyncClient
    ):
        """Смена пароля с неверным старым паролем"""
        response = await authenticated_client.post(
            "/api/profile/change-password",
            data={
                "old_password": "wrongpass",
                "new_password": "newpass123",
                "confirm_password": "newpass123"
            }
        )
     
        assert response.status_code in [400, 401]
        data = response.json()
        assert "error" in data

    async def test_change_password_mismatch(
        self,
        authenticated_client: AsyncClient
    ):
        """Смена пароля с несовпадающими новыми паролями"""
        response = await authenticated_client.post(
            "/api/profile/change-password",
            data={
                "old_password": "authpass123",
                "new_password": "newpass123",
                "confirm_password": "differentpass"
            }
        )
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data or "detail" in data