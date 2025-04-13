from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel

TYPE_NATURAL_PERSON = 1
TYPE_LEGAL_PERSON = 2

class Person(BaseModel):
    __tablename__ = "person"
    
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    last_login = Column(DateTime, nullable=True)
    balance = Column(Float, default=0.0)
    type = Column(Integer, nullable=False)
    cpf = Column(String, nullable=True)
    cnpj = Column(String, nullable=True)
    
    sent_transactions = relationship("Transaction", foreign_keys="Transaction.sender_id", back_populates="sender")
    received_transactions = relationship("Transaction", foreign_keys="Transaction.recipient_id", back_populates="recipient")
