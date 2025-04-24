import pytest
from unittest.mock import MagicMock, patch
from app.services.profile_service import ProfileService
from app.models.person import TYPE_NATURAL_PERSON, TYPE_LEGAL_PERSON
from app.core.exceptions import NotFoundException, BadRequestException

@pytest.mark.unit
class TestProfileService:
    
    @patch('app.services.profile_service.PersonRepository')
    def test_get_profile_natural_person_success(self, mock_person_repo):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.name = "João Silva"
        mock_user.email = "joao@example.com"
        mock_user.address = "Rua Teste, 123"
        mock_user.city = "São Paulo"
        mock_user.state = "SP"
        mock_user.balance = 1000.0
        mock_user.type = TYPE_NATURAL_PERSON
        mock_user.created_at = "2023-01-01T00:00:00"
        mock_user.last_login = "2023-01-02T00:00:00"
        mock_user.cpf = "12345678901"
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_profile_by_id.return_value = mock_user
        mock_person_repo.return_value = mock_person_repo_instance
        
        db = MagicMock()
        service = ProfileService(db)
        result = service.get_profile(user_id=1)
        
        assert result["success"] is True
        assert "message" in result
        assert result["data"]["id"] == 1
        assert result["data"]["name"] == "João Silva"
        assert result["data"]["email"] == "joao@example.com"
        assert result["data"]["cpf"] == "12345678901"
        assert "password" not in result["data"]
        
        mock_person_repo_instance.get_profile_by_id.assert_called_once_with(1)
    
    @patch('app.services.profile_service.PersonRepository')
    def test_get_profile_legal_person_success(self, mock_person_repo):
        mock_user = MagicMock()
        mock_user.id = 2
        mock_user.name = "Empresa Teste LTDA"
        mock_user.email = "empresa@example.com"
        mock_user.address = "Av Comercial, 456"
        mock_user.city = "São Paulo"
        mock_user.state = "SP"
        mock_user.balance = 5000.0
        mock_user.type = TYPE_LEGAL_PERSON
        mock_user.created_at = "2023-01-01T00:00:00"
        mock_user.last_login = "2023-01-02T00:00:00"
        mock_user.cnpj = "12345678901234"
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_profile_by_id.return_value = mock_user
        mock_person_repo.return_value = mock_person_repo_instance
        
        db = MagicMock()
        service = ProfileService(db)
        result = service.get_profile(user_id=2)
        
        assert result["success"] is True
        assert "message" in result
        assert result["data"]["id"] == 2
        assert result["data"]["name"] == "Empresa Teste LTDA"
        assert result["data"]["email"] == "empresa@example.com"
        assert result["data"]["cnpj"] == "12345678901234"
        assert "password" not in result["data"]
        
        mock_person_repo_instance.get_profile_by_id.assert_called_once_with(2)
    
    @patch('app.services.profile_service.PersonRepository')
    def test_get_profile_user_not_found(self, mock_person_repo):
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_profile_by_id.return_value = None
        mock_person_repo.return_value = mock_person_repo_instance
        
        db = MagicMock()
        service = ProfileService(db)
        
        with pytest.raises(NotFoundException) as exc_info:
            service.get_profile(user_id=999)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.error_code == "USER_NOT_FOUND"
        
        mock_person_repo_instance.get_profile_by_id.assert_called_once_with(999)
    
    