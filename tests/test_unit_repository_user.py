import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Account
from src.schemas import UserSchema, UserUpdateSchema
from src.repository.users import get_users, create_user, update_user


class TestAsync(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.acc = Account(id=1, email="test@tes.com", password="qwerty", confirmed=True)

    async def test_get_users(self):
        limit = 10
        offset = 0
        expected_users = [User(), User(), User(), User()]
        mock_users = MagicMock()
        mock_users.scalars.return_value.all.return_value = expected_users
        self.session.execute.return_value = mock_users
        result = await get_users(limit, offset, self.session, self.acc)
        self.assertEqual(result, expected_users)

    async def test_create_user(self):
        body = UserSchema(first_name="Test", last_name="Test", email="test@tes.com", phone_number="111111",
                          birthday="09.09.1999")
        result = await create_user(body, self.session, self.acc)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertTrue(hasattr(result, "data"))

    async def test_update_user(self):
        body = UserUpdateSchema(first_name="Test", last_name="Test", email="test@tes.com", phone_number="111111",
                                birthday="09.09.1999", data=True)
        user = User(first_name="Test old", last_name="Test old", email="testold@tes.com", phone_number="222222",
                    birthday="10.09.1999", data=False)
        mock_user = MagicMock()
        mock_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mock_user

        result = await update_user(user.id, body, self.session, self.acc)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertTrue(result.data, True)
