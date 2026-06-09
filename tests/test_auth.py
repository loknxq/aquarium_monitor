
import pytest
from httpx import AsyncClient


class TestAuth:
    async def test_register_success(self, client: AsyncClient):
        """Успешная регистрация"""
        response = await client.post(
            "/api/register",
            data={"username": "newuser", "password": "newpass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["username"] == "newuser"
        assert "user_id" in data

    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Регистрация с существующим логином"""
        response = await client.post(
            "/api/register",
            data={"username": test_user.username, "password": "testpass123"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "уже существует" in data["error"]

    async def test_login_success(self, client: AsyncClient, test_user):
        """Успешный вход"""
        response = await client.post(
            "/api/login",
            data={"username": test_user.username, "password": "testpass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["username"] == test_user.username
        assert "user_id" in data

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Вход с неверным паролем"""
        response = await client.post(
            "/api/login",
            data={"username": test_user.username, "password": "wrongpass"}
        )
        assert response.status_code == 401
        data = response.json()
        assert "Неверный" in data["error"]

    async def test_logout(self, authenticated_client: AsyncClient):
        """Выход из системы"""
        response = await authenticated_client.post("/api/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_get_user_authenticated(self, authenticated_client: AsyncClient):
        """Получение данных авторизованного пользователя"""
        response = await authenticated_client.get("/api/user")
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "id" in data

    async def test_get_user_unauthenticated(self, client: AsyncClient):
        """Получение данных неавторизованного пользователя"""
        response = await client.get("/api/user")
        assert response.status_code == 401