from sqlalchemy import Column, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

TYPE_TRANSACTION_DEPOSIT = 1
TYPE_TRANSACTION_WITHDRAW = 2
TYPE_TRANSACTION_TRANSFER = 3

class Transaction(BaseModel):
    __tablename__ = "transaction"

    amount = Column(Float, nullable=False)
    transaction_type = Column(Integer, nullable=False)
    sender_id = Column(Integer, ForeignKey("person.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("person.id"), nullable=True)
    
    sender = relationship("Person", foreign_keys=[sender_id], back_populates="sent_transactions")
    recipient = relationship("Person", foreign_keys=[recipient_id], back_populates="received_transactions")
