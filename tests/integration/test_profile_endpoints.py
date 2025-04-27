import pytest
from app.models.person import Person

@pytest.mark.integration
class TestProfileEndpoints:
    
    def test_get_profile_natural_person(self, client_natural_person, test_natural_person):
        response = client_natural_person.get("/api/v1/user/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_natural_person.id
        assert data["data"]["name"] == test_natural_person.name
        assert data["data"]["email"] == test_natural_person.email
        assert data["data"]["balance"] == float(test_natural_person.balance)
        assert "cpf" in data["data"]
        assert "password" not in data["data"]
    
    def test_get_profile_legal_person(self, client_legal_person, test_legal_person):
        response = client_legal_person.get("/api/v1/user/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_legal_person.id
        assert data["data"]["name"] == test_legal_person.name
        assert data["data"]["email"] == test_legal_person.email
        assert data["data"]["balance"] == float(test_legal_person.balance)
        assert "cnpj" in data["data"]
        assert "password" not in data["data"]
    
    def test_get_profile_unauthenticated(self, client):
        response = client.get("/api/v1/user/profile")
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "error_code" in data
        assert data["error_code"] == "INVALID_TOKEN"
    

