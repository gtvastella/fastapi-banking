from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.person import NaturalPersonCreate, LegalPersonCreate, LoginRequest
from app.services.auth_service import AuthService
from typing import Dict, Any

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
    
    return result
