from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.core.exceptions import AppException
from app.core.response_handler import ResponseHandler
import traceback
import logging
from starlette.exceptions import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseHandler.error(
            message=exc.message,
            data=exc.data,
            error_code=exc.error_code
        )
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    error_details = []
    for error in exc.errors():
        error_details.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseHandler.error(
            message="Erro de validação nos dados da requisição",
            data=error_details,
            error_code="VALIDATION_ERROR"
        )
    )

async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    error_details = []
    for error in exc.errors():
        error_details.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseHandler.error(
            message="Erro de validação nos dados",
            data=error_details,
            error_code="VALIDATION_ERROR"
        )
    )

async def python_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_details = str(exc)
    error_traceback = traceback.format_exc()
    logger.error(f"Exceção não tratada: {error_details}\n{error_traceback}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ResponseHandler.error(
            message="Ocorreu um erro inesperado",
            error_code="INTERNAL_SERVER_ERROR"
        )
    )

async def not_found_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ResponseHandler.error(
            message="Recurso não encontrado",
            error_code="NOT_FOUND"
        )
    )
