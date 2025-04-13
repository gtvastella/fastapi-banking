import pytest
from app.models.transaction import Transaction, TYPE_TRANSACTION_DEPOSIT, TYPE_TRANSACTION_WITHDRAW, TYPE_TRANSACTION_TRANSFER
from app.models.person import Person
from decimal import Decimal

@pytest.mark.integration
class TestTransactionEndpoints:
    
    def test_transfer_success(self, db_session, test_natural_person, test_legal_person, client_natural_person):
        initial_sender_balance = test_natural_person.balance
        initial_recipient_balance = test_legal_person.balance
        
        response = client_natural_person.post(
            "/api/v1/operation/transfer",
            json={
                "recipient_id": test_legal_person.id,
                "amount": 100.0
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["amount"] == 100.0
        assert "message" in data
        
        assert test_natural_person.balance == initial_sender_balance - 100.0
        assert test_legal_person.balance == initial_recipient_balance + 100.0
        
        transaction = db_session.query(Transaction).order_by(Transaction.id.desc()).first()
        assert transaction is not None
        assert transaction.amount == 100.0
        assert transaction.transaction_type == TYPE_TRANSACTION_TRANSFER
        assert transaction.sender_id == test_natural_person.id
        assert transaction.recipient_id == test_legal_person.id
    
    def test_transfer_insufficient_funds(self, db_session, test_natural_person, test_legal_person, client_natural_person):

        test_natural_person.balance = 50.0
        db_session.commit()
       
        response = client_natural_person.post(
            "/api/v1/operation/transfer",
            json={
                "recipient_id": test_legal_person.id,
                "amount": 100.0
            },
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "message" in data
        assert data["error_code"] == "INSUFFICIENT_FUNDS"
    
    def test_deposit_success(self, db_session, test_natural_person, client_natural_person):
        initial_balance = test_natural_person.balance
        
        response = client_natural_person.post(
            "/api/v1/operation/deposit",
            json={
                "amount": 200.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["amount"] == 200.0
        assert "message" in data
        
        db_session.refresh(test_natural_person)
        assert test_natural_person.balance == initial_balance + 200.0
        
        transaction = db_session.query(Transaction).order_by(Transaction.id.desc()).first()
        assert transaction is not None
        assert transaction.amount == 200.0
        assert transaction.transaction_type == TYPE_TRANSACTION_DEPOSIT
        assert transaction.sender_id == test_natural_person.id
    
    def test_deposit_legal_person_fails(self, db_session, client_legal_person):
        response = client_legal_person.post(
            "/api/v1/operation/deposit",
            json={
                "amount": 200.0
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "message" in data
        assert data["error_code"] == "NOT_NATURAL_PERSON"
    
    def test_withdraw_success(self, db_session, test_natural_person, client_natural_person):
        initial_balance = test_natural_person.balance
        
        response = client_natural_person.post(
            "/api/v1/operation/withdraw",
            json={
                "amount": 100.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["amount"] == 100.0
        assert "message" in data
        
        db_session.refresh(test_natural_person)
        assert test_natural_person.balance == initial_balance - 100.0
        
        transaction = db_session.query(Transaction).order_by(Transaction.id.desc()).first()
        assert transaction is not None
        assert transaction.amount == 100.0
        assert transaction.transaction_type == TYPE_TRANSACTION_WITHDRAW
        assert transaction.sender_id == test_natural_person.id

    def test_withdraw_insufficient_funds(self, db_session, test_natural_person, client_natural_person):
        test_natural_person.balance = 50.0
        db_session.commit()
        
        response = client_natural_person.post(
            "/api/v1/operation/withdraw",
            json={
                "amount": 100.0
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "message" in data
        assert data["error_code"] == "INSUFFICIENT_FUNDS"
    
    def test_transfer_to_nonexistent_recipient(self, db_session, client_natural_person):
        response = client_natural_person.post(
            "/api/v1/operation/transfer",
            json={
                "recipient_id": 9999,
                "amount": 50.0
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "message" in data
        assert data["error_code"] == "USER_NOT_FOUND"
        
    def test_transfer_to_self(self, test_natural_person, client_natural_person):
        response = client_natural_person.post(
            "/api/v1/operation/transfer",
            json={
                "recipient_id": test_natural_person.id,
                "amount": 50.0
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "message" in data
        assert data["error_code"] == "INVALID_RECIPIENT"
        
    def test_withdraw_legal_person_fails(self, db_session, client_legal_person):
        response = client_legal_person.post(
            "/api/v1/operation/withdraw",
            json={"amount": 50.0}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "message" in data
        assert data["error_code"] == "NOT_NATURAL_PERSON"
