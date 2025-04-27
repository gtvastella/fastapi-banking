from fastapi import APIRouter, Depends, Response, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.person import NaturalPersonCreate, LegalPersonCreate, LoginRequest
from app.services.auth_service import AuthService
from typing import Dict, Any
from app.core.response_handler import ResponseHandler

router = APIRouter()

@router.post(
    "/user/register/natural",
    summary="Cadastrar pessoa física",
    description="Cadastra um novo usuário como pessoa física",
    status_code=status.HTTP_200_OK
)
def register_natural_person(
    user_data: NaturalPersonCreate, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    auth_service = AuthService(db)
    return auth_service.register_natural_person(user_data)

@router.post(
    "/user/register/legal",
    summary="Cadastrar pessoa jurídica",
    description="Cadastra um novo usuário como pessoa jurídica",
    status_code=status.HTTP_200_OK
)
def register_legal_person(
    user_data: LegalPersonCreate, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    auth_service = AuthService(db)
    return auth_service.register_legal_person(user_data)

@router.post(
    "/user/login",
    summary="Realizar login",
    description="Autentica o usuário no sistema",
    status_code=status.HTTP_200_OK
)
def login(
    login_data: LoginRequest, 
    response: Response, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    auth_service = AuthService(db)
    access_token, result = auth_service.login_user(login_data)
    
    if result["success"]:
        response.set_cookie(
            key="Authorization",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=1800, 
            secure=False,
            samesite="lax"
        )
        response.set_cookie(
            key="x-bnk-auth",
            value="true",
            httponly=False,
            max_age=1800, 
            secure=False,
            samesite="lax"
        )
    
    return result

@router.post(
    "/user/logout",
    summary="Realizar logout",
    description="Encerra a sessão do usuário atual",
    status_code=status.HTTP_200_OK
)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    auth_service = AuthService(db)
    result = auth_service.logout_user(request)
    
    response.delete_cookie("Authorization")
    response.delete_cookie("x-bnk-auth")
    
    return result