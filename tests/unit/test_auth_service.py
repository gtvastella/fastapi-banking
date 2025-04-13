import pytest
from unittest.mock import MagicMock, patch
from app.services.auth_service import AuthService
from app.schemas.person import NaturalPersonCreate, LegalPersonCreate, LoginRequest
from fastapi import HTTPException
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.models.person import TYPE_NATURAL_PERSON, TYPE_LEGAL_PERSON

@pytest.mark.unit
class TestAuthService:
    
    @patch('app.services.auth_service.PersonRepository')
    def test_register_natural_person_success(self, mock_repo):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_email.return_value = None
        mock_repo_instance.create_natural_person.return_value = mock_user
        mock_repo.return_value = mock_repo_instance
        
        user_data = NaturalPersonCreate(
            name="Maria Silva",
            email="maria@example.com",
            password="senha123",
            address="Rua ABC, 123",
            city="Rio de Janeiro",
            state="RJ",
            cpf="12345678901"
        )
        
        db = MagicMock()
        service = AuthService(db)
        result = service.register_natural_person(user_data)
        
        assert "data" in result
        assert "id" in result["data"]
        assert result["data"]["id"] == 1
        mock_repo_instance.get_by_email.assert_called_once_with(user_data.email)
        mock_repo_instance.create_natural_person.assert_called_once()
    
    @patch('app.services.auth_service.PersonRepository')
    def test_register_legal_person_success(self, mock_repo):
        mock_user = MagicMock()
        mock_user.id = 2
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_email.return_value = None
        mock_repo_instance.create_legal_person.return_value = mock_user
        mock_repo.return_value = mock_repo_instance
        
        user_data = LegalPersonCreate(
            name="Empresa XYZ",
            email="contato@empresaxyz.com",
            password="senha456",
            address="Av Principal, 1000",
            city="São Paulo",
            state="SP",
            cnpj="12345678901234"
        )
        
        db = MagicMock()
        service = AuthService(db)
        result = service.register_legal_person(user_data)
        
        assert "data" in result
        assert "id" in result["data"]
        assert result["data"]["id"] == 2
        mock_repo_instance.get_by_email.assert_called_once_with(user_data.email)
        mock_repo_instance.create_legal_person.assert_called_once()
    
    @patch('app.services.auth_service.PersonRepository')
    def test_register_user_email_exists(self, mock_repo):
        mock_existing_user = MagicMock()
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_email.return_value = mock_existing_user
        mock_repo.return_value = mock_repo_instance
        
        user_data = NaturalPersonCreate(
            name="Maria Silva",
            email="maria@example.com",
            password="senha123",
            address="Rua ABC, 123",
            city="Rio de Janeiro",
            state="RJ",
            cpf="12345678901"
        )
        
        db = MagicMock()
        service = AuthService(db)
        
        with pytest.raises(BadRequestException) as exc_info:
            service.register_natural_person(user_data)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == "EMAIL_EXISTS"
        mock_repo_instance.get_by_email.assert_called_once_with(user_data.email)
        mock_repo_instance.create_natural_person.assert_not_called()
    
    @patch('app.services.auth_service.PersonRepository')
    @patch('app.services.auth_service.verify_password')
    @patch('app.services.auth_service.create_access_token')
    def test_login_success(self, mock_create_token, mock_verify, mock_repo):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.password = "hashed_password"
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_email.return_value = mock_user
        mock_repo.return_value = mock_repo_instance
        
        mock_verify.return_value = True
        mock_create_token.return_value = "fake_token"
        
        login_data = LoginRequest(
            email="maria@example.com",
            password="senha123"
        )
        
        db = MagicMock()
        service = AuthService(db)
        token, result = service.login_user(login_data)
         
        assert "message" in result
        assert "success" in result
        assert result["success"] == True
        assert token == "fake_token"
        mock_repo_instance.get_by_email.assert_called_once_with(login_data.email)
        mock_verify.assert_called_once_with(login_data.password, mock_user.password)
        mock_repo_instance.update_last_login.assert_called_once_with(mock_user.id)
        
    @patch('app.services.auth_service.PersonRepository')
    def test_login_user_not_found(self, mock_repo):
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_email.return_value = None
        mock_repo.return_value = mock_repo_instance
        
        login_data = LoginRequest(
            email="inexistente@example.com",
            password="senha123"
        )
        
        db = MagicMock()
        service = AuthService(db)
        
        with pytest.raises(UnauthorizedException) as exc_info:
            service.login_user(login_data)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_CREDENTIALS"
        
    @patch('app.services.auth_service.PersonRepository')
    @patch('app.services.auth_service.verify_password')
    def test_login_invalid_password(self, mock_verify, mock_repo):
        mock_user = MagicMock()
        mock_user.password = "hashed_password"
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_email.return_value = mock_user
        mock_repo.return_value = mock_repo_instance
        
        mock_verify.return_value = False
        
        login_data = LoginRequest(
            email="maria@example.com",
            password="senha_errada"
        )
        
        db = MagicMock()
        service = AuthService(db)
        
        with pytest.raises(UnauthorizedException) as exc_info:
            service.login_user(login_data)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_CREDENTIALS"
