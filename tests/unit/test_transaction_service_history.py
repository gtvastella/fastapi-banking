import pytest
from unittest.mock import MagicMock, patch
from app.services.transaction_service import TransactionService
from app.models.transaction import TYPE_TRANSACTION_DEPOSIT, TYPE_TRANSACTION_WITHDRAW, TYPE_TRANSACTION_TRANSFER
from app.core.exceptions import NotFoundException
from datetime import datetime, timedelta

@pytest.mark.unit
class TestTransactionServiceHistory:
    
    @patch('app.services.transaction_service.PersonRepository')
    @patch('app.services.transaction_service.TransactionRepository')
    def test_get_transaction_history_success(self, mock_transaction_repo, mock_person_repo):
        # Set up mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.balance = 1200.0
        
        # Set up mock transactions
        mock_transactions = [
            # Deposit
            MagicMock(
                id=101,
                amount=500.0,
                transaction_type=TYPE_TRANSACTION_DEPOSIT,
                created_at=datetime(2023, 1, 1, 10, 0, 0),
                sender_id=1,
                recipient_id=None
            ),
            # Withdrawal
            MagicMock(
                id=102,
                amount=200.0,
                transaction_type=TYPE_TRANSACTION_WITHDRAW,
                created_at=datetime(2023, 1, 2, 11, 0, 0),
                sender_id=1,
                recipient_id=None
            ),
            # Outgoing transfer
            MagicMock(
                id=103,
                amount=300.0,
                transaction_type=TYPE_TRANSACTION_TRANSFER,
                created_at=datetime(2023, 1, 3, 12, 0, 0),
                sender_id=1,
                recipient_id=2
            ),
            # Incoming transfer
            MagicMock(
                id=104,
                amount=100.0,
                transaction_type=TYPE_TRANSACTION_TRANSFER,
                created_at=datetime(2023, 1, 4, 13, 0, 0),
                sender_id=2,
                recipient_id=1
            )
        ]
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_by_id.return_value = mock_user
        mock_person_repo.return_value = mock_person_repo_instance
        
        mock_transaction_repo_instance = MagicMock()
        mock_transaction_repo_instance.get_user_transactions.return_value = mock_transactions
        mock_transaction_repo.return_value = mock_transaction_repo_instance
        
        db = MagicMock()
        service = TransactionService(db)
        result = service.get_transaction_history(user_id=1)
        
        assert result["success"] is True
        assert "message" in result
        assert result["data"]["balance"] == 1200.0
        assert len(result["data"]["transactions"]) == 4
        
        # Check deposit transaction
        deposit = next(t for t in result["data"]["transactions"] if t["id"] == 101)
        assert deposit["amount"] == 500.0
        assert deposit["direction"] == "in"
        assert "Depósito" in deposit["description"]
        
        # Check withdrawal transaction
        withdrawal = next(t for t in result["data"]["transactions"] if t["id"] == 102)
        assert withdrawal["amount"] == 200.0
        assert withdrawal["direction"] == "out"
        assert "Saque" in withdrawal["description"]
        
        # Check outgoing transfer
        outgoing = next(t for t in result["data"]["transactions"] if t["id"] == 103)
        assert outgoing["amount"] == 300.0
        assert outgoing["direction"] == "out"
        assert "Transferência enviada" in outgoing["description"]
        
        # Check incoming transfer
        incoming = next(t for t in result["data"]["transactions"] if t["id"] == 104)
        assert incoming["amount"] == 100.0
        assert incoming["direction"] == "in"
        assert "Transferência recebida" in incoming["description"]
        
        mock_person_repo_instance.get_by_id.assert_called_once_with(1)
        mock_transaction_repo_instance.get_user_transactions.assert_called_once_with(1)
    
    @patch('app.services.transaction_service.PersonRepository')
    def test_get_transaction_history_user_not_found(self, mock_person_repo):
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_by_id.return_value = None
        mock_person_repo.return_value = mock_person_repo_instance
        
        db = MagicMock()
        service = TransactionService(db)
        
        with pytest.raises(NotFoundException) as exc_info:
            service.get_transaction_history(user_id=999)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.error_code == "USER_NOT_FOUND"
        
        mock_person_repo_instance.get_by_id.assert_called_once_with(999)
    
    @patch('app.services.transaction_service.PersonRepository')
    @patch('app.services.transaction_service.TransactionRepository')
    def test_get_transaction_history_empty(self, mock_transaction_repo, mock_person_repo):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.balance = 0.0
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_by_id.return_value = mock_user
        mock_person_repo.return_value = mock_person_repo_instance
        
        mock_transaction_repo_instance = MagicMock()
        mock_transaction_repo_instance.get_user_transactions.return_value = []
        mock_transaction_repo.return_value = mock_transaction_repo_instance
        
        db = MagicMock()
        service = TransactionService(db)
        result = service.get_transaction_history(user_id=1)
        
        assert result["success"] is True
        assert "message" in result
        assert result["data"]["balance"] == 0.0
        assert len(result["data"]["transactions"]) == 0
        
        mock_person_repo_instance.get_by_id.assert_called_once_with(1)
        mock_transaction_repo_instance.get_user_transactions.assert_called_once_with(1)
    
