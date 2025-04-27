import pytest
from app.models.transaction import Transaction, TYPE_TRANSACTION_DEPOSIT, TYPE_TRANSACTION_WITHDRAW, TYPE_TRANSACTION_TRANSFER
from datetime import datetime, timedelta

@pytest.mark.integration
class TestTransactionHistoryEndpoints:
    
    def test_get_transaction_history(self, db_session, test_natural_person, test_legal_person, client_natural_person):
        # Create some test transactions first
        transactions = [
            Transaction(
                amount=200.0,
                transaction_type=TYPE_TRANSACTION_DEPOSIT,
                sender_id=test_natural_person.id
            ),
            Transaction(
                amount=50.0,
                transaction_type=TYPE_TRANSACTION_WITHDRAW,
                sender_id=test_natural_person.id
            ),
            Transaction(
                amount=100.0,
                transaction_type=TYPE_TRANSACTION_TRANSFER,
                sender_id=test_natural_person.id,
                recipient_id=test_legal_person.id
            ),
            Transaction(
                amount=25.0,
                transaction_type=TYPE_TRANSACTION_TRANSFER,
                sender_id=test_legal_person.id,
                recipient_id=test_natural_person.id
            )
        ]
        
        for transaction in transactions:
            db_session.add(transaction)
        db_session.commit()
        
        response = client_natural_person.get("/api/v1/operation/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        transactions = data["data"]["transactions"]
        assert len(transactions) == 4
        
        # Check transaction types and directions
        deposit = next((t for t in transactions if t["type"] == TYPE_TRANSACTION_DEPOSIT), None)
        assert deposit is not None
        assert deposit["direction"] == "in"
        assert "Depósito" in deposit["description"]
        
        withdraw = next((t for t in transactions if t["type"] == TYPE_TRANSACTION_WITHDRAW), None)
        assert withdraw is not None
        assert withdraw["direction"] == "out"
        assert "Saque" in withdraw["description"]
        
        # Should have both outgoing and incoming transfers
        outgoing = next((t for t in transactions if t["type"] == TYPE_TRANSACTION_TRANSFER and t["direction"] == "out"), None)
        assert outgoing is not None
        assert "enviada" in outgoing["description"]
        
        incoming = next((t for t in transactions if t["type"] == TYPE_TRANSACTION_TRANSFER and t["direction"] == "in"), None)
        assert incoming is not None
        assert "recebida" in incoming["description"]
    
    def test_get_transaction_history_empty(self, client_legal_person):
        # Legal person with no transactions yet
        response = client_legal_person.get("/api/v1/operation/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["transactions"]) == 0
    
    def test_get_transaction_history_unauthenticated(self, client):
        response = client.get("/api/v1/operation/history")
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "error_code" in data
        assert data["error_code"] == "INVALID_TOKEN"
    
   