from sqlalchemy.orm import Session
from fastapi import Request
from app.repositories.person_repository import PersonRepository
from app.core.security import verify_password, create_access_token
from app.schemas.person import NaturalPersonCreate, LegalPersonCreate, LoginRequest, PersonCreate
from datetime import timedelta
from app.core import config
from app.models.person import Person, TYPE_NATURAL_PERSON, TYPE_LEGAL_PERSON
from app.core.response_handler import ResponseHandler
from app.core.exceptions import (
    AppException,
    ValidationException,
    UnauthorizedException,
    DatabaseException,
    BadRequestException
)
from typing import Dict, Any, Tuple


class AuthService:
    def __init__(self, db: Session):
        self.person_repository = PersonRepository(db)
        self.response = ResponseHandler()

    def register_natural_person(self, user_data: NaturalPersonCreate) -> Dict[str, Any]:
        try:
            self._check_email_availability(user_data.email)

            user = self.person_repository.create_natural_person(
                name=user_data.name,
                email=user_data.email,
                password=user_data.password,
                address=user_data.address,
                city=user_data.city,
                state=user_data.state,
                cpf=user_data.cpf
            )

            return self.response.success(data={"id": user.id}, message="Usuário cadastrado com sucesso")
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(message=f"Falha no cadastro: {str(e)}")

    def register_legal_person(self, user_data: LegalPersonCreate) -> Dict[str, Any]:
        try:
            self._check_email_availability(user_data.email)

            user = self.person_repository.create_legal_person(
                name=user_data.name,
                email=user_data.email,
                password=user_data.password,
                address=user_data.address,
                city=user_data.city,
                state=user_data.state,
                cnpj=user_data.cnpj
            )

            return self.response.success(data={"id": user.id}, message="Usuário cadastrado com sucesso")
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(message=f"Falha no cadastro: {str(e)}")

    def register_user(self, user_data: PersonCreate) -> Dict[str, Any]:
        if user_data.person_type == TYPE_NATURAL_PERSON:
            natural_data = NaturalPersonCreate(
                name=user_data.name,
                email=user_data.email,
                password=user_data.password,
                address=user_data.address,
                city=user_data.city,
                state=user_data.state,
                cpf=user_data.cpf
            )
            return self.register_natural_person(natural_data)
        elif user_data.person_type == TYPE_LEGAL_PERSON:
            legal_data = LegalPersonCreate(
                name=user_data.name,
                email=user_data.email,
                password=user_data.password,
                address=user_data.address,
                city=user_data.city,
                state=user_data.state,
                cnpj=user_data.cnpj
            )
            return self.register_legal_person(legal_data)
        else:
            raise ValidationException(
                message="Tipo de pessoa inválido", error_code="INVALID_PERSON_TYPE")

    def login_user(self, login_data: LoginRequest) -> Tuple[str, Dict[str, Any]]:
        try:
            user = self.person_repository.get_by_email(login_data.email)

            if not user or not verify_password(login_data.password, user.password):
                raise UnauthorizedException(
                    message="Email ou senha incorretos", error_code="INVALID_CREDENTIALS")

            self.person_repository.update_last_login(user.id)

            access_token_expires = timedelta(
                minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user.id)}, expires_delta=access_token_expires
            )

            return access_token, self.response.success(
                message="Login realizado com sucesso",
                data={"token": access_token,
                      "user": {
                          "id": user.id,
                          "name": user.name,
                          "email": user.email,
                          "type": user.type
                      }
                }

            )
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(message=f"Falha no login: {str(e)}")
        
    def logout_user(self, request : Request) -> Dict[str, Any]:
        try:
            token = request.cookies.get("Authorization")
            if not token:
                raise UnauthorizedException(
                    message="Token de autenticação inválido ou expirado",
                    error_code="INVALID_TOKEN"
                )

            return self.response.success(message="Logout realizado com sucesso")
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(message=f"Falha no logout: {str(e)}")

    def _check_email_availability(self, email: str) -> None:
        existing_user = self.person_repository.get_by_email(email)
        if existing_user:
            raise BadRequestException(
                message="Email já cadastrado", error_code="EMAIL_EXISTS")
