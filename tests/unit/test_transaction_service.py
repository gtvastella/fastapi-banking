import pytest
from unittest.mock import MagicMock, patch
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransferRequest, DepositRequest, WithdrawRequest
from app.models.person import TYPE_NATURAL_PERSON, TYPE_LEGAL_PERSON
from app.core.exceptions import BadRequestException, ForbiddenException

@pytest.mark.unit
class TestTransactionService:
    
    @patch('app.services.transaction_service.PersonRepository')
    @patch('app.services.transaction_service.TransactionRepository')
    def test_transfer_success(self, mock_transaction_repo, mock_person_repo):
        mock_sender = MagicMock()
        mock_sender.id = 1
        mock_sender.balance = 1000.0
        
        mock_recipient = MagicMock()
        mock_recipient.id = 2
        
        mock_transaction = MagicMock()
        mock_transaction.id = 101
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_by_id.side_effect = lambda id: mock_sender if id == 1 else mock_recipient
        mock_person_repo_instance.update_balance.return_value = mock_sender
        mock_person_repo.return_value = mock_person_repo_instance
        
        mock_transaction_repo_instance = MagicMock()
        mock_transaction_repo_instance.create_transaction.return_value = mock_transaction
        mock_transaction_repo.return_value = mock_transaction_repo_instance
        
        transfer_data = TransferRequest(
            recipient_id=2,
            amount=500.0
        )
        current_user = MagicMock()
        current_user.id = 1
        current_user.balance = 1000.0
        
        db = MagicMock()
        service = TransactionService(db)
        result = service.transfer(transfer_data, current_user)
        
        assert result["success"] is True
        assert result["data"]["transaction_id"] == 101
        assert result["data"]["amount"] == 500.0
        assert "message" in result
        
        assert mock_person_repo_instance.get_by_id.call_count == 2
        mock_person_repo_instance.update_balance.assert_any_call(1, -500.0)
        mock_person_repo_instance.update_balance.assert_any_call(2, 500.0)
        mock_transaction_repo_instance.create_transaction.assert_called_once()
    
    @patch('app.services.transaction_service.PersonRepository')
    def test_transfer_insufficient_balance(self, mock_person_repo):
        mock_sender = MagicMock()
        mock_sender.id = 1
        mock_sender.balance = 100.0
        
        mock_recipient = MagicMock()
        mock_recipient.id = 2
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_by_id.side_effect = lambda id: mock_sender if id == 1 else mock_recipient
        mock_person_repo.return_value = mock_person_repo_instance
        
        transfer_data = TransferRequest(
            recipient_id=2,
            amount=500.0
        )
        current_user = MagicMock()
        current_user.id = 1
        current_user.balance = 100.0
        
        db = MagicMock()
        service = TransactionService(db)
        
        with pytest.raises(BadRequestException) as exc_info:
            service.transfer(transfer_data, current_user)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == "INSUFFICIENT_FUNDS"
        
        mock_person_repo_instance.update_balance.assert_not_called()
    
    @patch('app.services.transaction_service.PersonRepository')
    def test_transfer_to_self_account(self, mock_person_repo):
        mock_person = MagicMock()
        mock_person.id = 1
        mock_person.balance = 1000.0
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_by_id.return_value = mock_person
        mock_person_repo.return_value = mock_person_repo_instance
        
        transfer_data = TransferRequest(
            recipient_id=1,
            amount=500.0
        )
        current_user = MagicMock()
        current_user.id = 1
        current_user.balance = 1000.0
        
        db = MagicMock()
        service = TransactionService(db)
        
        with pytest.raises(BadRequestException) as exc_info:
            service.transfer(transfer_data, current_user)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == "INVALID_RECIPIENT"
        
        mock_person_repo_instance.update_balance.assert_not_called()
    
    @patch('app.services.transaction_service.PersonRepository')
    @patch('app.services.transaction_service.TransactionRepository')
    def test_deposit_success(self, mock_transaction_repo, mock_person_repo):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.balance = 1000.0
        mock_user.type = TYPE_NATURAL_PERSON
        
        mock_updated_user = MagicMock()
        mock_updated_user.balance = 1200.0
        
        mock_transaction = MagicMock()
        mock_transaction.id = 201
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_natural_person_by_id.return_value = mock_user
        mock_person_repo_instance.update_balance.return_value = mock_updated_user
        mock_person_repo.return_value = mock_person_repo_instance
        
        mock_transaction_repo_instance = MagicMock()
        mock_transaction_repo_instance.create_transaction.return_value = mock_transaction
        mock_transaction_repo.return_value = mock_transaction_repo_instance
        
        deposit_data = DepositRequest(
            amount=200.0
        )
        current_user = MagicMock()
        current_user.id = 1
        
        db = MagicMock()
        service = TransactionService(db)
        result = service.deposit(deposit_data, current_user)
        
        assert result["success"] is True
        assert result["data"]["transaction_id"] == 201
        assert result["data"]["amount"] == 200.0
        assert result["data"]["new_balance"] == 1200.0
        assert "message" in result
        
        mock_person_repo_instance.update_balance.assert_called_once_with(1, 200.0)
        mock_transaction_repo_instance.create_transaction.assert_called_once()

    @patch('app.services.transaction_service.PersonRepository')
    def test_withdraw_success(self, mock_person_repo):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.balance = 1000.0
        mock_user.type = TYPE_NATURAL_PERSON
        
        mock_updated_user = MagicMock()
        mock_updated_user.balance = 800.0
        
        mock_transaction = MagicMock()
        mock_transaction.id = 301
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_natural_person_by_id.return_value = mock_user
        mock_person_repo_instance.update_balance.return_value = mock_updated_user
        mock_person_repo.return_value = mock_person_repo_instance
        
        mock_transaction_repo = MagicMock()
        mock_transaction_repo.create_transaction.return_value = mock_transaction
        
        with patch('app.services.transaction_service.TransactionRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_transaction_repo
            
            withdraw_data = WithdrawRequest(amount=200.0)
            current_user = MagicMock()
            current_user.id = 1
            
            db = MagicMock()
            service = TransactionService(db)
            result = service.withdraw(withdraw_data, current_user)
            
            assert result["success"] is True
            assert result["data"]["new_balance"] == 800.0
            assert "message" in result

    @patch('app.services.transaction_service.PersonRepository')
    def test_deposit_legal_person_fails(self, mock_person_repo):
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_natural_person_by_id.return_value = None
        mock_person_repo.return_value = mock_person_repo_instance
        
        deposit_data = DepositRequest(amount=200.0)
        current_user = MagicMock()
        current_user.id = 1
        current_user.type = TYPE_LEGAL_PERSON
        
        db = MagicMock()
        service = TransactionService(db)
        
        with pytest.raises(BadRequestException) as exc_info:
            service.deposit(deposit_data, current_user)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == "NOT_NATURAL_PERSON"

    @patch('app.services.transaction_service.PersonRepository')
    def test_withdraw_insufficient_balance(self, mock_person_repo):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.balance = 100.0
        mock_user.type = TYPE_NATURAL_PERSON
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_natural_person_by_id.return_value = mock_user
        mock_person_repo.return_value = mock_person_repo_instance
        
        withdraw_data = WithdrawRequest(amount=200.0)
        current_user = MagicMock()
        current_user.id = 1
        
        db = MagicMock()
        service = TransactionService(db)
        
        with pytest.raises(BadRequestException) as exc_info:
            service.withdraw(withdraw_data, current_user)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == "INSUFFICIENT_FUNDS"

    @patch('app.services.transaction_service.PersonRepository')
    def test_withdraw_legal_person_fails(self, mock_person_repo):
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_natural_person_by_id.return_value = None
        mock_person_repo.return_value = mock_person_repo_instance
        
        withdraw_data = WithdrawRequest(amount=100.0)
        current_user = MagicMock()
        current_user.id = 1
        current_user.type = TYPE_LEGAL_PERSON
        
        db = MagicMock()
        service = TransactionService(db)
        
        with pytest.raises(BadRequestException) as exc_info:
            service.withdraw(withdraw_data, current_user)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == "NOT_NATURAL_PERSON"

    @patch('app.services.transaction_service.PersonRepository')
    def test_transfer_recipient_not_found(self, mock_person_repo):
        mock_sender = MagicMock()
        mock_sender.id = 1
        mock_sender.balance = 1000.0
        
        mock_person_repo_instance = MagicMock()
        mock_person_repo_instance.get_by_id.side_effect = lambda id: mock_sender if id == 1 else None
        mock_person_repo.return_value = mock_person_repo_instance
        
        transfer_data = TransferRequest(
            recipient_id=999,
            amount=500.0
        )
        current_user = MagicMock()
        current_user.id = 1
        
        db = MagicMock()
        service = TransactionService(db)
        
        with pytest.raises(BadRequestException) as exc_info:
            service.transfer(transfer_data, current_user)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == "USER_NOT_FOUND"
