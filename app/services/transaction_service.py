from sqlalchemy.orm import Session
from app.repositories.person_repository import PersonRepository
from app.repositories.transaction_repository import TransactionRepository
from app.models.person import Person, TYPE_NATURAL_PERSON
from app.schemas.transaction import TransferRequest, DepositRequest, WithdrawRequest
from app.models.transaction import TYPE_TRANSACTION_DEPOSIT, TYPE_TRANSACTION_WITHDRAW, TYPE_TRANSACTION_TRANSFER
from typing import Dict, Any
from app.core.response_handler import ResponseHandler
from app.core.exceptions import (
    BadRequestException,
    DatabaseException,
    AppException,
    NotFoundException
)

class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.person_repository = PersonRepository(db)
        self.transaction_repository = TransactionRepository(db)
        self.response = ResponseHandler()
    
    def transfer(self, data: TransferRequest, current_user: Person) -> Dict[str, Any]:
        try:
            sender = self._validate_sender(current_user.id)
            recipient = self._validate_recipient(data.recipient_id, sender.id)
            
            if sender.balance < data.amount:
                raise BadRequestException(message="Saldo insuficiente", error_code="INSUFFICIENT_FUNDS")
            
            try:
                self.person_repository.begin_transaction()
                
                self.person_repository.update_balance(sender.id, -data.amount)
                self.person_repository.update_balance(recipient.id, data.amount)
                
                transaction = self.transaction_repository.create_transaction(
                    amount=data.amount,
                    transaction_type=TYPE_TRANSACTION_TRANSFER,
                    sender_id=sender.id,
                    recipient_id=recipient.id
                )
                
                self.person_repository.commit()
                
                return self.response.success(
                    data={
                        "transaction_id": transaction.id,
                        "amount": data.amount,
                        "new_balance": sender.balance - data.amount
                    },
                    message="Transferência concluída com sucesso"
                )
            except Exception as e:
                self.person_repository.rollback()
                raise DatabaseException(message=f"Falha na transferência: {str(e)}")
        
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(message=f"Erro na transferência: {str(e)}")
    
    def deposit(self, data: DepositRequest, current_user: Person) -> Dict[str, Any]:
        try:
            user = self._validate_natural_person(current_user.id)
            
            try:
                updated_user = self.person_repository.update_balance(user.id, data.amount)
                
                transaction = self.transaction_repository.create_transaction(
                    amount=data.amount,
                    transaction_type=TYPE_TRANSACTION_DEPOSIT,
                    sender_id=user.id
                )
                
                return self.response.success(
                    data={
                        "transaction_id": transaction.id,
                        "amount": data.amount,
                        "new_balance": updated_user.balance
                    },
                    message="Depósito realizado com sucesso"
                )
            except Exception as e:
                self.person_repository.rollback()
                raise DatabaseException(message=f"Falha no depósito: {str(e)}")
        
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(message=f"Erro no depósito: {str(e)}")
    
    def withdraw(self, data: WithdrawRequest, current_user: Person) -> Dict[str, Any]:
        try:
            user = self._validate_natural_person(current_user.id)
            
            if user.balance < data.amount:
                raise BadRequestException(message="Saldo insuficiente", error_code="INSUFFICIENT_FUNDS")
            
            try:
                updated_user = self.person_repository.update_balance(user.id, -data.amount)
                
                transaction = self.transaction_repository.create_transaction(
                    amount=data.amount,
                    transaction_type=TYPE_TRANSACTION_WITHDRAW,
                    sender_id=user.id
                )
                
                return self.response.success(
                    data={
                        "transaction_id": transaction.id,
                        "amount": data.amount,
                        "new_balance": updated_user.balance
                    },
                    message="Saque realizado com sucesso"
                )
            except Exception as e:
                self.person_repository.rollback()
                raise DatabaseException(message=f"Falha no saque: {str(e)}")
        
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(message=f"Erro no saque: {str(e)}")

    def get_transaction_history(self, user_id: int) -> Dict[str, Any]:
        try:
            user = self.person_repository.get_by_id(user_id)
            if not user:
                raise NotFoundException(message="Usuário não encontrado", error_code="USER_NOT_FOUND")
                
            transactions = self.transaction_repository.get_user_transactions(user_id)
            
            formatted_transactions = []
            for transaction in transactions:
                transaction_data = {
                    "id": transaction.id,
                    "amount": transaction.amount,
                    "created_at": transaction.created_at,
                    "type": transaction.transaction_type
                }
                
                if transaction.transaction_type == TYPE_TRANSACTION_TRANSFER:
                    if transaction.sender_id == user_id:
                        transaction_data["description"] = f"Transferência enviada para ID {transaction.recipient_id}"
                        transaction_data["direction"] = "out"
                    else:
                        transaction_data["description"] = f"Transferência recebida de ID {transaction.sender_id}"
                        transaction_data["direction"] = "in"
                elif transaction.transaction_type == TYPE_TRANSACTION_DEPOSIT:
                    transaction_data["description"] = "Depósito"
                    transaction_data["direction"] = "in"
                elif transaction.transaction_type == TYPE_TRANSACTION_WITHDRAW:
                    transaction_data["description"] = "Saque"
                    transaction_data["direction"] = "out"
                
                formatted_transactions.append(transaction_data)
            
            return self.response.success(
                data={
                    "transactions": formatted_transactions
                },
                message="Extrato de transações recuperado com sucesso"
            )
        
        except Exception as e:
            if not isinstance(e, NotFoundException):
                raise DatabaseException(message=f"Erro ao recuperar extrato: {str(e)}")
            raise
        
    def get_balance(self, user_id: int) -> Dict[str, Any]:
        try:
            user = self.person_repository.get_by_id(user_id)
            
            if not user:
                raise NotFoundException(
                    message="Usuário não encontrado", 
                    error_code="USER_NOT_FOUND"
                )
            
            return self.response.success(
                data={"balance": user.balance},
                message="Saldo recuperado com sucesso"
            )
            
        except Exception as e:
            if not isinstance(e, NotFoundException):
                raise DatabaseException(message=f"Erro ao recuperar saldo: {str(e)}")
            raise


    def _validate_sender(self, sender_id: int) -> Person:
        sender = self.person_repository.get_by_id(sender_id)
        if not sender:
            raise BadRequestException(message="Remetente não encontrado", error_code="USER_NOT_FOUND")
        return sender
    
    def _validate_recipient(self, recipient_id: int, sender_id: int) -> Person:
        if sender_id == recipient_id:
            raise BadRequestException(message="Não é possível transferir para você mesmo", error_code="INVALID_RECIPIENT")
            
        recipient = self.person_repository.get_by_id(recipient_id)
        if not recipient:
            raise BadRequestException(message="Destinatário não encontrado", error_code="USER_NOT_FOUND")
            
        return recipient
    
    def _validate_natural_person(self, user_id: int) -> Person:
        user = self.person_repository.get_natural_person_by_id(user_id)
        if not user:
            raise BadRequestException(
                message="Operação disponível apenas para pessoas físicas", 
                error_code="NOT_NATURAL_PERSON"
            )
        return user
