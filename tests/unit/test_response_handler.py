import pytest
from app.core.response_handler import ResponseHandler


@pytest.mark.unit
class TestResponseHandler:
    
    def test_success_response_default(self):
        response = ResponseHandler.success()
        assert response["success"] is True
        assert response["data"] == []
        assert "message" in response
    
    def test_success_response_with_data(self):
        test_data = {"id": 1, "nome": "Teste"}
        response = ResponseHandler.success(data=test_data)
        assert response["success"] is True
        assert response["data"] == test_data
        assert "message" in response
    
    def test_success_response_with_custom_message(self):
        custom_message = "Cadastro realizado com sucesso"
        response = ResponseHandler.success(message=custom_message)
        assert response["success"] is True
        assert response["data"] == []
        assert response["message"] == custom_message
    
    def test_error_response_default(self):
        response = ResponseHandler.error()
        assert response["success"] is False
        assert response["data"] == []
        assert "message" in response
        assert "error_code" not in response
    
    def test_error_response_with_custom_message(self):
        custom_message = "Saldo insuficiente"
        response = ResponseHandler.error(message=custom_message)
        assert response["success"] is False
        assert response["data"] == []
        assert response["message"] == custom_message
    
    def test_error_response_with_error_code(self):
        response = ResponseHandler.error(error_code="INSUFFICIENT_FUNDS")
        assert response["success"] is False
        assert "message" in response
        assert response["error_code"] == "INSUFFICIENT_FUNDS"
    
    def test_error_response_with_data(self):
        error_data = {"campo": "saldo", "valor_minimo": 100}
        response = ResponseHandler.error(data=error_data)
        assert response["success"] is False
        assert response["data"] == error_data
        assert "message" in response
