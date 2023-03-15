import pytest
from unittest.mock import MagicMock, patch

from src.database.models import User
from src.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_mail_verify", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_get_user_me(client, token, user):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["username"] == user.get('username')
        assert data["email"] == user.get('email')


def test_forgot_password(client, token, user, monkeypatch):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.users.send_mail_password", mock_send_email)
        response = client.post("/api/users/forgot_password", json=user)
        assert response.status_code == 200, response.text


def test_forgot_password_wrong_email(client, token, wrong_user, monkeypatch):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.users.send_mail_password", mock_send_email)
        response = client.post("/api/users/forgot_password", json=wrong_user)
        assert response.status_code == 409, response.text
        data = response.json()
        assert data['detail'] == 'Account does not exists'


