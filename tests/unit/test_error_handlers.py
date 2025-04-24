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
    python_exception_handler,
    not_found_exception_handler
)
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

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
    
    async def test_not_found_exception_handler(self, mock_request):
        # Test custom 404 handler
        exc = StarletteHTTPException(status_code=404, detail="Resource not found")
        response = await not_found_exception_handler(mock_request, exc)
        
        assert response.status_code == 404
        content = response.body.decode()
        assert "success" in content
        assert "false" in content.lower()
        assert "error_code" in content
        assert "NOT_FOUND" in content
    
    async def test_app_exception_handler_for_not_found(self, mock_request):
        # Test app exception handler with NotFoundException
        exc = NotFoundException(message="User profile not found", error_code="PROFILE_NOT_FOUND")
        response = await app_exception_handler(mock_request, exc)
        
        assert response.status_code == 404
        content = response.body.decode()
        assert "success" in content
        assert "false" in content.lower()
        assert "error_code" in content
        assert "PROFILE_NOT_FOUND" in content
        assert "User profile not found" in content
    
    async def test_app_exception_handler_with_custom_data(self, mock_request):
        # Test app exception with custom data
        custom_data = {"resource_type": "user", "requested_id": 123}
        exc = NotFoundException(
            message="The requested user could not be found", 
            error_code="USER_NOT_FOUND",
            data=custom_data
        )
        response = await app_exception_handler(mock_request, exc)
        
        assert response.status_code == 404
        content = response.body.decode()
        assert "success" in content
        assert "false" in content.lower()
        assert '"resource_type":"user"' in content.replace(" ", "")
        assert '"requested_id":123' in content.replace(" ", "")
    
    async def test_validation_exception_handler_with_complex_errors(self, mock_request):
        errors = [
            {
                "loc": ("body", "user", "email"),
                "msg": "value is not a valid email address",
                "type": "value_error.email"
            },
            {
                "loc": ("body", "user", "password"),
                "msg": "ensure this value has at least 8 characters",
                "type": "value_error.any_str.min_length"
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
        assert "value is not a valid email address" in content
        assert "ensure this value has at least 8 characters" in content
