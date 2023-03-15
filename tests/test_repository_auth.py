import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
import src.repository.auth as r_auth


class TestRepositoryAuth(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User()

    async def test_get_user_by_email(self):
        self.session.query().filter().first.return_value = self.user
        result = await r_auth.get_user_by_email(email=self.user.email, db=self.session)
        self.assertEqual(result, self.user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await r_auth.get_user_by_email(email=self.user.email, db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(username='Irina', email='IraOlijnyk@gmail.com', password='qwert-11')
        result = await r_auth.create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "avatar"))

    async def test_update_token(self):
        self.session.query().filter().first.return_value = self.user
        self.session.commit.return_value = None
        token = 'new_token'
        await r_auth.update_token(user=self.user, token=token, db=self.session)
        self.assertTrue(self.user.refresh_token)
        self.assertEqual(self.user.refresh_token, token)

    async def test_confirmed_user(self):
        self.session.query().filter().first.return_value = self.user
        self.session.commit.return_value = None
        email = 'IraOlijnyk@gmail.com'
        await r_auth.confirmed_user(email=email, db=self.session)
        self.assertTrue(self.user.confirmed)

    async def test_update_avatar(self):
        self.session.query().filter().first.return_value = self.user
        url = 'http://my.com/1.jpg'
        result = await r_auth.update_avatar(email=self.user.email, avatar_url=url, db=self.session)
        self.assertEqual(result.avatar, url)

    async def test_update_avatar_not_found(self):
        self.session.query().filter().first.return_value = None
        url = 'http://my.com/1.jpg'
        result = await r_auth.update_avatar(email=self.user.email, avatar_url=url, db=self.session)
        self.assertEqual(result, None)

    async def test_update_password(self):
        self.session.query().filter().first.return_value = self.user
        password = 'new_password'
        result = await r_auth.update_password(email=self.user.email, password=password, db=self.session)
        self.assertEqual(result.password, password)

    async def test_update_password_not_found_user(self):
        self.session.query().filter().first.return_value = None
        password = 'new_password'
        result = await r_auth.update_password(email=self.user.email, password=password, db=self.session)
        self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()
