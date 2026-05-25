import pytest

pytestmark = pytest.mark.anyio

class TestAquariums:
    
    async def test_create_aquarium_success(self, client):
        await client.post("/api/register", data={"username": "aquaowner", "password": "pass"})
        await client.post("/api/login", data={"username": "aquaowner", "password": "pass"})
        
        response = await client.post(
            "/api/aquariums",
            data={
                "name": "My Reef Tank",
                "inhabitants": "marine",
                "parameters": [1, 2, 3]
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "My Reef Tank"
    
    async def test_create_aquarium_no_parameters(self, client):
        await client.post("/api/register", data={"username": "noparamuser", "password": "pass"})
        await client.post("/api/login", data={"username": "noparamuser", "password": "pass"})
        
        response = await client.post(
            "/api/aquariums",
            data={
                "name": "Bad Aquarium",
                "inhabitants": "tropical_fish",
                "parameters": []
            }
        )
        assert response.status_code == 400
        assert "параметр" in response.json()["error"]
    
    async def test_create_aquarium_empty_name(self, client):
        await client.post("/api/register", data={"username": "emptyname", "password": "pass"})
        await client.post("/api/login", data={"username": "emptyname", "password": "pass"})
        
        response = await client.post(
            "/api/aquariums",
            data={
                "name": "",
                "inhabitants": "tropical_fish",
                "parameters": [1, 2]
            }
        )
        assert response.status_code == 400
    
    async def test_get_aquariums(self, client):
        await client.post("/api/register", data={"username": "listowner", "password": "pass"})
        await client.post("/api/login", data={"username": "listowner", "password": "pass"})
        
        await client.post("/api/aquariums", data={"name": "Aquarium 1", "inhabitants": "goldfish", "parameters": [1]})
        await client.post("/api/aquariums", data={"name": "Aquarium 2", "inhabitants": "shrimp", "parameters": [2]})
        
        response = await client.get("/api/aquariums")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    async def test_get_single_aquarium(self, client):
        await client.post("/api/register", data={"username": "singleowner", "password": "pass"})
        await client.post("/api/login", data={"username": "singleowner", "password": "pass"})
        
        create_resp = await client.post("/api/aquariums", data={"name": "Single Tank", "inhabitants": "cichlids", "parameters": [1, 2]})
        aquarium_id = create_resp.json()["id"]
        
        response = await client.get(f"/api/aquariums/{aquarium_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Single Tank"
    
    async def test_delete_aquarium(self, client):
        await client.post("/api/register", data={"username": "deleteowner", "password": "pass"})
        await client.post("/api/login", data={"username": "deleteowner", "password": "pass"})
        
        create_resp = await client.post("/api/aquariums", data={"name": "To Delete", "inhabitants": "plants", "parameters": [1]})
        aquarium_id = create_resp.json()["id"]
        
        response = await client.delete(f"/api/aquariums/{aquarium_id}")
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        get_resp = await client.get(f"/api/aquariums/{aquarium_id}")
        assert get_resp.status_code == 404