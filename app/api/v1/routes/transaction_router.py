from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.transaction import TransferRequest, DepositRequest, WithdrawRequest
from app.services.transaction_service import TransactionService
from app.core.security import get_current_user_from_request
from typing import Dict, Any

router = APIRouter(prefix="/operation")

@router.post(
    "/transfer",
    summary="Transferir valores entre contas",
    description="Transfere um valor da sua conta para a conta de outro usuário",
    status_code=status.HTTP_200_OK
)
def transfer(
    request: Request,
    data: TransferRequest, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    current_user = get_current_user_from_request(request)
    transaction_service = TransactionService(db)
    return transaction_service.transfer(data, current_user)

@router.post(
    "/deposit",
    summary="Depositar valores em conta",
    description="Realiza um depósito na sua conta (apenas pessoa física)",
    status_code=status.HTTP_200_OK
)
def deposit(
    request: Request,
    data: DepositRequest, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    current_user = get_current_user_from_request(request)
    transaction_service = TransactionService(db)
    return transaction_service.deposit(data, current_user)

@router.post(
    "/withdraw",
    summary="Sacar valores da conta",
    description="Realiza um saque da sua conta (apenas pessoa física)",
    status_code=status.HTTP_200_OK
)
def withdraw(
    request: Request,
    data: WithdrawRequest, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    current_user = get_current_user_from_request(request)
    transaction_service = TransactionService(db)
    return transaction_service.withdraw(data, current_user)

@router.get(
    "/history",
    summary="Obter extrato de transações",
    description="Recupera o histórico de transações do usuário",
    status_code=status.HTTP_200_OK
)
def get_transaction_history(
    request: Request, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    current_user = get_current_user_from_request(request)
    transaction_service = TransactionService(db)
    return transaction_service.get_transaction_history(current_user.id)

@router.get(
    "/balance",
    summary="Obter saldo do usuário",
    description="Recupera apenas o saldo atual do usuário autenticado",
    status_code=status.HTTP_200_OK
)
def get_balance(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    current_user = get_current_user_from_request(request)
    transaction_service = TransactionService(db)
    return transaction_service.get_balance(current_user.id)