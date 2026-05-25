import pytest
from app.auth import hash_password, verify_password

pytestmark = pytest.mark.anyio

class TestAuth:
    
    def test_hash_password(self):
        password = "mypassword123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)
    
    def test_verify_password_wrong(self):
        password = "correct123"
        hashed = hash_password(password)
        assert not verify_password("wrong123", hashed)
    
    async def test_register_endpoint(self, client):
        response = await client.post(
            "/api/register",
            data={"username": "registeruser", "password": "registerpass"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["username"] == "registeruser"
    
    async def test_register_duplicate(self, client):
        await client.post("/api/register", data={"username": "dupuser", "password": "pass"})
        response = await client.post("/api/register", data={"username": "dupuser", "password": "pass"})
        assert response.status_code == 400
        assert "уже существует" in response.json()["error"]
    
    async def test_login_success(self, client):
        await client.post("/api/register", data={"username": "loginuser", "password": "loginpass"})
        response = await client.post("/api/login", data={"username": "loginuser", "password": "loginpass"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    async def test_login_wrong_password(self, client):
        await client.post("/api/register", data={"username": "wronguser", "password": "correct"})
        response = await client.post("/api/login", data={"username": "wronguser", "password": "wrong"})
        assert response.status_code == 401
    
    async def test_logout(self, client):
        await client.post("/api/register", data={"username": "logoutuser", "password": "pass"})
        await client.post("/api/login", data={"username": "logoutuser", "password": "pass"})
        response = await client.post("/api/logout")
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    async def test_get_user_authenticated(self, client):
        await client.post("/api/register", data={"username": "getuser", "password": "pass"})
        await client.post("/api/login", data={"username": "getuser", "password": "pass"})
        response = await client.get("/api/user")
        assert response.status_code == 200
        assert response.json()["username"] == "getuser"