from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.profile_service import ProfileService
from app.core.security import get_current_user_from_request
from typing import Dict, Any

router = APIRouter(prefix="/user")

@router.get(
    "/profile",
    summary="Obter dados do perfil",
    description="Recupera os dados do perfil do usuário autenticado",
    status_code=status.HTTP_200_OK
)
def get_profile(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    current_user = get_current_user_from_request(request)
    profile_service = ProfileService(db)
    return profile_service.get_profile(current_user.id)
