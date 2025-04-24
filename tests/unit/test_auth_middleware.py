import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import Request, status
from starlette.middleware.base import RequestResponseEndpoint
from fastapi.responses import JSONResponse
from app.core.auth_middleware import AuthMiddleware
import jwt
import logging
import re
from starlette.routing import Match

@pytest.mark.unit
class TestAuthMiddleware:
    
    @pytest.fixture
    def middleware(self):
        return AuthMiddleware()
    
    async def test_excluded_path(self, middleware):
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/user/login"
        
        mock_call_next = AsyncMock(spec=RequestResponseEndpoint)
        mock_response = JSONResponse(content={"status": "ok"})
        mock_call_next.return_value = mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        mock_call_next.assert_called_once_with(mock_request)
        assert response == mock_response
    
    async def test_wildcard_excluded_path(self, middleware):
        wildcard_path = "/public/*"
        middleware.exclude_paths.append(wildcard_path)
        middleware.wildcard_patterns.append(
            re.compile(f"^{re.escape(wildcard_path[:-1])}.+")
        )
        
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/public/health"
        mock_request.cookies = {}
        mock_request.headers = {}
        
        mock_call_next = AsyncMock(spec=RequestResponseEndpoint)
        mock_response = JSONResponse(content={"status": "ok"})
        mock_call_next.return_value = mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        mock_call_next.assert_called_once_with(mock_request)
        assert response == mock_response
    
    async def test_no_auth_cookie(self, middleware):
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/protected"
        mock_request.cookies = {}
        mock_request.headers = {}
        
        mock_call_next = AsyncMock(spec=RequestResponseEndpoint)
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert mock_call_next.call_count == 0
        
        content = response.body.decode()
        assert '"error_code":"INVALID_TOKEN"' in content
    
    @patch('app.core.auth_middleware.AuthMiddleware._verify_token')
    async def test_invalid_token(self, mock_verify_token, middleware):
        mock_verify_token.return_value = None
        
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/protected"
        mock_request.cookies = {"Authorization": "Bearer invalid_token"}
        mock_request.headers = {}
        
        mock_call_next = AsyncMock(spec=RequestResponseEndpoint)
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert mock_verify_token.call_count == 1
        assert mock_verify_token.call_args[0][0] == "invalid_token"
        assert mock_call_next.call_count == 0
        
        content = response.body.decode()
        assert '"error_code":"INVALID_TOKEN"' in content
    
    @patch('app.core.auth_middleware.AuthMiddleware._verify_token')
    async def test_valid_token(self, mock_verify_token, middleware):
        mock_user = Mock()
        mock_user.id = 1
        mock_verify_token.return_value = mock_user
        
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/protected"
        mock_request.cookies = {"Authorization": "Bearer valid_token"}
        mock_request.headers = {}
        mock_request.state = Mock()
        
        mock_call_next = AsyncMock(spec=RequestResponseEndpoint)
        mock_response = JSONResponse(content={"status": "ok"})
        mock_call_next.return_value = mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        mock_verify_token.assert_called_once_with("valid_token")
        assert hasattr(mock_request.state, "user")
        assert mock_request.state.user == mock_user
        
        mock_call_next.assert_called_once_with(mock_request)
        assert response == mock_response
    
    @patch('app.core.auth_middleware.AuthMiddleware._verify_token')
    async def test_token_without_bearer_prefix(self, mock_verify_token, middleware):
        mock_user = Mock()
        mock_user.id = 1
        mock_verify_token.return_value = mock_user
        
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/protected"
        mock_request.cookies = {"Authorization": "valid_token"}
        mock_request.headers = {}
        mock_request.state = Mock()
        
        mock_call_next = AsyncMock(spec=RequestResponseEndpoint)
        mock_response = JSONResponse(content={"status": "ok"})
        mock_call_next.return_value = mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        mock_verify_token.assert_called_once_with("valid_token")
        assert hasattr(mock_request.state, "user")
        mock_call_next.assert_called_once_with(mock_request)
        assert response == mock_response
    
    @patch('app.core.auth_middleware.AuthMiddleware._verify_token')
    async def test_auth_header(self, mock_verify_token, middleware):
        mock_user = Mock()
        mock_user.id = 1
        mock_verify_token.return_value = mock_user
        
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/protected"
        mock_request.cookies = {}
        mock_request.headers = {"Authorization": "Bearer header_token"}
        mock_request.state = Mock()
        
        mock_call_next = AsyncMock(spec=RequestResponseEndpoint)
        mock_response = JSONResponse(content={"status": "ok"})
        mock_call_next.return_value = mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        mock_verify_token.assert_called_once_with("header_token")
        assert hasattr(mock_request.state, "user")
        mock_call_next.assert_called_once_with(mock_request)
        assert response == mock_response
    
    @patch('app.core.auth_middleware.jwt.decode')
    @patch('app.core.auth_middleware.get_db')
    def test_verify_token_valid(self, mock_get_db, mock_jwt_decode, middleware):
        mock_jwt_decode.return_value = {"sub": "123"}
        
        mock_db = Mock()
        mock_db_generator = Mock()
        mock_db_generator.__next__ = Mock(return_value=mock_db)
        mock_db_generator.__next__.side_effect = [mock_db, StopIteration]
        mock_get_db.return_value = mock_db_generator
        
        mock_user = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = middleware._verify_token("valid_token")
        
        mock_jwt_decode.assert_called_once_with(
            "valid_token", 
            "testing_secret_key_for_consistent_tests", 
            algorithms=["HS256"]
        )
        assert result == mock_user
        mock_db.close.assert_called_once()
    
    @patch('app.core.auth_middleware.jwt.decode')
    @patch('app.core.auth_middleware.logger')
    def test_verify_token_jwt_error(self, mock_logger, mock_jwt_decode, middleware):
        mock_jwt_decode.side_effect = jwt.PyJWTError("Invalid token")
        
        result = middleware._verify_token("invalid_token")
        
        assert result is None
        mock_jwt_decode.assert_called_once()
        mock_logger.error.assert_called_once()
    
    @patch('app.core.auth_middleware.jwt.decode')
    @patch('app.core.auth_middleware.logger')
    def test_verify_token_missing_sub(self, mock_logger, mock_jwt_decode, middleware):
        mock_jwt_decode.return_value = {"exp": 1234567890}  # No 'sub' claim
        
        result = middleware._verify_token("incomplete_token")
        
        assert result is None
        mock_jwt_decode.assert_called_once()
        mock_logger.error.assert_called_once()
    
    async def test_existing_route_requires_auth(self, middleware):
        mock_app = Mock()
        mock_route = Mock()
        mock_route.matches.return_value = (Match.FULL, {})
        
        mock_app.routes = [mock_route]
        middleware.app = mock_app
        
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1/protected"
        mock_request.cookies = {}
        mock_request.headers = {}
        
        mock_call_next = AsyncMock(spec=RequestResponseEndpoint)
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        # Auth middleware should stop with 401 for existing protected routes
        assert response.status_code == 401
        assert mock_call_next.call_count == 0