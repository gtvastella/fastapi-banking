from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.repositories.base_repository import BaseRepository

class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(db, Transaction)

    def create_transaction(self, amount: float, transaction_type: int, sender_id: int, recipient_id: int = None):
        return self.create(
            amount=amount,
            transaction_type=transaction_type,
            sender_id=sender_id,
            recipient_id=recipient_id
        )
    
    def get_user_transactions(self, user_id: int):
        return self.db.query(Transaction).filter(
            (Transaction.sender_id == user_id) | (Transaction.recipient_id == user_id)
        ).all()
