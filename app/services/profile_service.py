from sqlalchemy.orm import Session
from app.repositories.person_repository import PersonRepository
from app.core.response_handler import ResponseHandler
from app.core.exceptions import NotFoundException, DatabaseException
from typing import Dict, Any

class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.person_repository = PersonRepository(db)
        self.response = ResponseHandler()
    
    def get_profile(self, user_id: int) -> Dict[str, Any]:
        try:
            user = self.person_repository.get_profile_by_id(user_id)
            
            if not user:
                raise NotFoundException(
                    message="Usuário não encontrado", 
                    error_code="USER_NOT_FOUND"
                )
            
            profile_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "address": user.address,
                "city": user.city,
                "state": user.state,
                "balance": user.balance,
                "type": user.type,
            }
            
            if user.type == 1: 
                profile_data["cpf"] = user.cpf
            elif user.type == 2:
                profile_data["cnpj"] = user.cnpj
                
            return self.response.success(
                data=profile_data,
                message="Dados do perfil recuperados com sucesso"
            )
            
        except Exception as e:
            if not isinstance(e, NotFoundException):
                raise DatabaseException(message=f"Erro ao recuperar perfil: {str(e)}")
            raise
