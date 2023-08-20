import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Account
from src.schemas import AccountSchema
from src.repository.acc import get_acc_by_email, create_acc, update_token, confirmed_email


class TestAccountRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_acc_by_email(self):
        email = "test@example.com"
        expected_account = Account(email=email)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_account
        self.session.execute.return_value = mock_result

        result = await get_acc_by_email(email, self.session)
        self.assertEqual(result, expected_account)

    async def test_create_acc(self):
        account_schema = AccountSchema(email="test@example.com")
        expected_account = Account(email=account_schema.email)
        mock_gravatar = MagicMock()
        mock_gravatar.get_image.return_value = None
        Gravatar = MagicMock(return_value=mock_gravatar)

        result = await create_acc(account_schema, self.session)
        self.assertEqual(result.email, account_schema.email)
        self.assertTrue(self.session.add.called)
        self.assertTrue(self.session.commit.called)

    async def test_update_token(self):
        account = Account(email="test@example.com")
        token = "new_token"
        await update_token(account, token, self.session)
        self.assertEqual(account.refresh_token, token)

    async def test_confirmed_email(self):
        email = "test@example.com"
        account = Account(email=email)
        mock_get_acc_by_email = AsyncMock(return_value=account)
        with unittest.mock.patch('src.repository.acc.get_acc_by_email', mock_get_acc_by_email):
            await confirmed_email(email, self.session)
            self.assertTrue(account.confirmed)
            self.assertTrue(self.session.commit.called)
