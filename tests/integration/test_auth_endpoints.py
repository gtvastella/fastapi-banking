import pytest
from app.models.person import Person, TYPE_NATURAL_PERSON, TYPE_LEGAL_PERSON
from app.core.security import verify_password
import re

@pytest.mark.integration
class TestAuthEndpoints:
    
    def test_register_natural_person(self, client, db_session):
        response = client.post(
            "/api/v1/user/register/natural",
            json={
                "name": "Carlos Silva",
                "email": "carlos@example.com",
                "password": "senha123",
                "address": "Rua das Flores, 123",
                "city": "Porto Alegre",
                "state": "RS",
                "cpf": "98765432101"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        
        user_id = data["data"]["id"]
        user = db_session.query(Person).filter(Person.id == user_id).first()
        assert user is not None
        assert user.email == "carlos@example.com"
        assert user.cpf == "98765432101"
        assert user.type == TYPE_NATURAL_PERSON
    
    def test_register_legal_person(self, client, db_session):
        response = client.post(
            "/api/v1/user/register/legal",
            json={
                "name": "Empresa ABC",
                "email": "contato@empresaabc.com",
                "password": "senha456",
                "address": "Av Empresarial, 999",
                "city": "Curitiba",
                "state": "PR",
                "cnpj": "98765432101234"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        
        user_id = data["data"]["id"]
        user = db_session.query(Person).filter(Person.id == user_id).first()
        assert user is not None
        assert user.email == "contato@empresaabc.com"
        assert user.cnpj == "98765432101234"
        assert user.type == TYPE_LEGAL_PERSON
    
    def test_register_duplicate_email(self, client, test_natural_person):
        response = client.post(
            "/api/v1/user/register/natural",
            json={
                "name": "Outro Usuário",
                "email": test_natural_person.email,
                "password": "outrasenha",
                "address": "Outro Endereço, 456",
                "city": "Recife",
                "state": "PE",
                "cpf": "11122233344"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "message" in data
        assert data["error_code"] == "EMAIL_EXISTS"
    
    def test_login_success(self, client, test_natural_person):
        response = client.post(
            "/api/v1/user/login",
            json={
                "email": test_natural_person.email,
                "password": "senha123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "token" in data["data"]
        assert data["data"]["token"] is not None
        assert "Authorization" in response.cookies
    
    def test_login_invalid_credentials(self, client, test_natural_person):
        response = client.post(
            "/api/v1/user/login",
            json={
                "email": test_natural_person.email,
                "password": "senha_errada"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "message" in data
        assert data["error_code"] == "INVALID_CREDENTIALS"
        
        assert "Authorization" not in response.cookies

    def test_register_natural_person_invalid_cpf(self, client):
        response = client.post(
            "/api/v1/user/register/natural",
            json={
                "name": "Pessoa Teste",
                "email": "pessoa@example.com",
                "password": "senha123",
                "address": "Rua Teste, 123",
                "city": "Brasília",
                "state": "DF",
                "cpf": "123"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "error_code" in data
        assert data["error_code"] == "VALIDATION_ERROR"
        
        cpf_error = next((error for error in data["data"] if "cpf" in error["loc"]), None)
        assert cpf_error is not None
        assert "cpf deve conter" in cpf_error["msg"].lower() or "comprimento" in cpf_error["msg"].lower()
        
    def test_register_legal_person_invalid_cnpj(self, client):
        response = client.post(
            "/api/v1/user/register/legal",
            json={
                "name": "Empresa Teste",
                "email": "empresa@example.com",
                "password": "senha123",
                "address": "Av Teste, 999",
                "city": "São Paulo",
                "state": "SP",
                "cnpj": "123456"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "error_code" in data
        assert data["error_code"] == "VALIDATION_ERROR"
        
        cnpj_error = next((error for error in data["data"] if "cnpj" in error["loc"]), None)
        assert cnpj_error is not None
        assert "cnpj deve conter" in cnpj_error["msg"].lower()
        
    def test_register_weak_password(self, client):
        response = client.post(
            "/api/v1/user/register/natural",
            json={
                "name": "Pessoa Fraca",
                "email": "fraca@example.com",
                "password": "123",
                "address": "Rua Fraca, 123",
                "city": "Belo Horizonte",
                "state": "MG",
                "cpf": "12345678901"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "error_code" in data
        assert data["error_code"] == "VALIDATION_ERROR"
        
        password_error = next((error for error in data["data"] if "password" in error["loc"]), None)
        assert password_error is not None
        assert "senha deve ter pelo menos" in password_error["msg"].lower()
        
    def test_nonexistent_user_login(self, client):
        response = client.post(
            "/api/v1/user/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "message" in data
        assert data["error_code"] == "INVALID_CREDENTIALS"
        assert "Authorization" not in response.cookies
