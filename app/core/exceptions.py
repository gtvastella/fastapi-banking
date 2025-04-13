from fastapi import HTTPException, status
from typing import Optional, Dict, Any, Union

class AppException(HTTPException):
    def __init__(
        self, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "Ocorreu um erro durante a operação",
        data: Any = [],
        error_code: Optional[Union[str, int]] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.data = data
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=message, headers=headers)

class ValidationException(AppException):
    def __init__(
        self,
        message: str = "Erro de validação",
        data: Any = [],
        error_code: Optional[Union[str, int]] = "VALIDATION_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            data=data,
            error_code=error_code
        )

class NotFoundException(AppException):
    def __init__(
        self,
        message: str = "Recurso não encontrado",
        data: Any = [],
        error_code: Optional[Union[str, int]] = "NOT_FOUND",
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            data=data,
            error_code=error_code
        )

class UnauthorizedException(AppException):
    def __init__(
        self,
        message: str = "Acesso não autorizado",
        data: Any = [],
        error_code: Optional[Union[str, int]] = "UNAUTHORIZED",
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            data=data,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"}
        )

class ForbiddenException(AppException):
    def __init__(
        self,
        message: str = "Operação não permitida",
        data: Any = [],
        error_code: Optional[Union[str, int]] = "FORBIDDEN",
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            data=data,
            error_code=error_code
        )

class BadRequestException(AppException):
    def __init__(
        self,
        message: str = "Requisição inválida",
        data: Any = [],
        error_code: Optional[Union[str, int]] = "BAD_REQUEST",
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            data=data,
            error_code=error_code
        )

class DatabaseException(AppException):
    def __init__(
        self,
        message: str = "Ocorreu um erro no banco de dados",
        data: Any = [],
        error_code: Optional[Union[str, int]] = "DATABASE_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            data=data,
            error_code=error_code
        )

class BusinessLogicException(AppException):
    def __init__(
        self,
        message: str = "Violação de regra de negócio",
        data: Any = [],
        error_code: Optional[Union[str, int]] = "BUSINESS_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            data=data,
            error_code=error_code
        )
