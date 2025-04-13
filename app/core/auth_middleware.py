from fastapi import Request, status
from fastapi.responses import JSONResponse
import jwt 
from typing import Optional, List, Pattern
import re
from app.core import config
from app.core.database import get_db
from app.models.person import Person
from app.core.response_handler import ResponseHandler
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app=None):
        if app is not None:
            super().__init__(app)
        self.exclude_paths: List[str] = [
            "/api/v1/user/login", 
            "/api/v1/user/register/natural",
            "/api/v1/user/register/legal", 
            "/docs", 
            "/redoc", 
            "/openapi.json", 
            "/"
        ]
        self.wildcard_patterns: List[Pattern] = [
            re.compile(f"^{re.escape(path[:-1])}.+") 
            for path in self.exclude_paths 
            if path.endswith("*")
        ]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if self._is_path_excluded(request.url.path):
            return await call_next(request)
        
        token = self._extract_token(request)
        if not token:
            return self._handle_no_auth()
        
        user = self._verify_token(token)
        if user is None:
            return self._handle_no_auth()
        
        request.state.user = user
        return await call_next(request)
    
    def _is_path_excluded(self, path: str) -> bool:
        if path in self.exclude_paths:
            return True
            
        return any(pattern.match(path) for pattern in self.wildcard_patterns)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        token = request.cookies.get("Authorization")
        if token:
            return token.split(" ")[1] if " " in token else token
            
        auth_header = request.headers.get("Authorization")
        if auth_header:
            return auth_header.split(" ")[1] if " " in auth_header else auth_header
            
        return None
    
    def _handle_no_auth(self):
        response_handler = ResponseHandler()
        response_data = response_handler.error(
            message="Token de autenticação inválido ou expirado",
            error_code="INVALID_TOKEN"
        )
        return JSONResponse(
            content=response_data,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    def _verify_token(self, token: str) -> Optional[Person]:
        try:
            payload = jwt.decode(
                token,
                config.SECRET_KEY, 
                algorithms=[config.ALGORITHM]
            )
            user_id = payload.get("sub")
            if not user_id:
                logger.error("Token missing 'sub' claim")
                return None
            
            db_generator = get_db()
            db = next(db_generator)
            try:
                return db.query(Person).filter(Person.id == user_id).first()
            finally:
                db.close()
                try:
                    next(db_generator)
                except StopIteration:
                    pass
                
        except jwt.PyJWTError as e:
            logger.error(f"JWT verification error: {str(e)}")
            return None
