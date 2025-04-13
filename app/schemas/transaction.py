from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class TransferRequest(BaseModel):
    recipient_id: int = Field(..., gt=0, description="ID do destinatário da transferência")
    amount: float = Field(..., gt=0, description="Valor da transferência")

class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Valor do depósito")

class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Valor do saque")

class TransactionResponse(BaseModel):
    id: int
    amount: float
    transaction_type: str
    created_at: datetime
    sender_id: int
    recipient_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)
