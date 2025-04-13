import pytest
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError, BaseModel
from app.core.exceptions import (
    AppException,
    ValidationException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    BadRequestException
)
from app.core.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    pydantic_validation_exception_handler,
    python_exception_handler
)

@pytest.mark.unit
class TestErrorHandlers:
    
    @pytest.fixture
    def mock_request(self):
        return Request(scope={"type": "http", "path": "/test"})
    
    async def test_app_exception_handler(self, mock_request):
        exc = AppException(status_code=400, message="Test error")
        response = await app_exception_handler(mock_request, exc)
        
        assert response.status_code == 400
        content = response.body.decode()
        assert "success" in content
        assert "false" in content.lower()
    
    async def test_validation_exception_handler(self, mock_request):
        errors = [
            {
                "loc": ("body", "name"),
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
        exc = RequestValidationError(errors=errors)
        
        response = await validation_exception_handler(mock_request, exc)
        
        assert response.status_code == 422
        content = response.body.decode()
        assert "success" in content
        assert "false" in content.lower()
        assert "error_code" in content
        assert "VALIDATION_ERROR" in content
    
    async def test_pydantic_validation_exception_handler(self, mock_request):
        class TestModel(BaseModel):
            name: str
            age: int
        
        try:
            TestModel(age="not an int")
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            response = await pydantic_validation_exception_handler(mock_request, e)
            
            assert response.status_code == 422
            content = response.body.decode()
            assert "success" in content
            assert "false" in content.lower()
            assert "error_code" in content
            assert "VALIDATION_ERROR" in content
    
    async def test_python_exception_handler(self, mock_request):
        exc = ValueError("Test value error")
        response = await python_exception_handler(mock_request, exc)
        
        assert response.status_code == 500
        content = response.body.decode()
        assert "success" in content
        assert "false" in content.lower()
        assert "error_code" in content
        assert "INTERNAL_SERVER_ERROR" in content
