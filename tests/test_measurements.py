import json
import pytest

pytestmark = pytest.mark.anyio

class TestMeasurements:
    
    async def test_add_measurement_success(self, client):
        await client.post("/api/register", data={"username": "measuser", "password": "pass"})
        await client.post("/api/login", data={"username": "measuser", "password": "pass"})
        
        create_resp = await client.post("/api/aquariums", data={"name": "Meas Tank", "inhabitants": "tropical_fish", "parameters": [1, 2]})
        aquarium_id = create_resp.json()["id"]
        
        values = {"temperature": 25.5, "ph": 7.2}
        response = await client.post(
            f"/api/aquariums/{aquarium_id}/measurements",
            data={
                "date_str": "2024-01-15",
                "values": json.dumps(values)
            }
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    async def test_add_measurement_negative_value(self, client):
        await client.post("/api/register", data={"username": "neguser", "password": "pass"})
        await client.post("/api/login", data={"username": "neguser", "password": "pass"})
        
        create_resp = await client.post("/api/aquariums", data={"name": "Neg Tank", "inhabitants": "tropical_fish", "parameters": [1]})
        aquarium_id = create_resp.json()["id"]
        
        values = {"temperature": -5.0}
        response = await client.post(
            f"/api/aquariums/{aquarium_id}/measurements",
            data={
                "date_str": "2024-01-15",
                "values": json.dumps(values)
            }
        )
        assert response.status_code == 400
        assert "отрицательным" in response.json()["error"]
    
    async def test_add_measurement_invalid_number(self, client):
        await client.post("/api/register", data={"username": "invaliduser", "password": "pass"})
        await client.post("/api/login", data={"username": "invaliduser", "password": "pass"})
        
        create_resp = await client.post("/api/aquariums", data={"name": "Invalid Tank", "inhabitants": "tropical_fish", "parameters": [1]})
        aquarium_id = create_resp.json()["id"]
        
        values = {"temperature": "abc"}
        response = await client.post(
            f"/api/aquariums/{aquarium_id}/measurements",
            data={
                "date_str": "2024-01-15",
                "values": json.dumps(values)
            }
        )
        assert response.status_code == 400
    
    async def test_get_measurements(self, client):
        await client.post("/api/register", data={"username": "getmeasuser", "password": "pass"})
        await client.post("/api/login", data={"username": "getmeasuser", "password": "pass"})
        
        create_resp = await client.post("/api/aquariums", data={"name": "Get Meas", "inhabitants": "tropical_fish", "parameters": [1, 2]})
        aquarium_id = create_resp.json()["id"]
        
        values1 = {"temperature": 24.0, "ph": 7.0}
        await client.post(f"/api/aquariums/{aquarium_id}/measurements", data={"date_str": "2024-01-10", "values": json.dumps(values1)})
        
        values2 = {"temperature": 25.0, "ph": 7.2}
        await client.post(f"/api/aquariums/{aquarium_id}/measurements", data={"date_str": "2024-01-15", "values": json.dumps(values2)})
        
        response = await client.get(f"/api/aquariums/{aquarium_id}/measurements")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    async def test_get_measurements_with_date_filter(self, client):
        await client.post("/api/register", data={"username": "filteruser", "password": "pass"})
        await client.post("/api/login", data={"username": "filteruser", "password": "pass"})
        
        create_resp = await client.post("/api/aquariums", data={"name": "Filter Tank", "inhabitants": "tropical_fish", "parameters": [1]})
        aquarium_id = create_resp.json()["id"]
        
        values = {"temperature": 25.0}
        await client.post(f"/api/aquariums/{aquarium_id}/measurements", data={"date_str": "2024-01-10", "values": json.dumps(values)})
        await client.post(f"/api/aquariums/{aquarium_id}/measurements", data={"date_str": "2024-01-20", "values": json.dumps(values)})
        
        response = await client.get(f"/api/aquariums/{aquarium_id}/measurements?start_date=2024-01-15&end_date=2024-01-25")
        assert response.status_code == 200
        data = response.json()
        for m in data:
            assert m["date"] >= "2024-01-15"
            assert m["date"] <= "2024-01-25"
    
    async def test_export_csv(self, client):
        await client.post("/api/register", data={"username": "exportuser", "password": "pass"})
        await client.post("/api/login", data={"username": "exportuser", "password": "pass"})
        
        create_resp = await client.post("/api/aquariums", data={"name": "Export Tank", "inhabitants": "tropical_fish", "parameters": [1]})
        aquarium_id = create_resp.json()["id"]
        
        values = {"temperature": 25.5}
        await client.post(f"/api/aquariums/{aquarium_id}/measurements", data={"date_str": "2024-01-15", "values": json.dumps(values)})
        
        response = await client.get(f"/api/aquariums/{aquarium_id}/export")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]