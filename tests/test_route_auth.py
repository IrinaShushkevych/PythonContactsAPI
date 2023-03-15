from unittest.mock import MagicMock, patch
import pytest

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


def test_request_email_not_found(client, user, monkeypatch):
    mock_send_mail = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_mail_verify", mock_send_mail)
    response = client.post("/api/auth/request_email", json=user)
    assert response.status_code == 400, response.text
    data = response.json()
    assert data['detail'] == 'Verification error'


def test_signup(client, user, monkeypatch):
    mock_send_mail = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_mail_verify", mock_send_mail)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_signup(client, user, monkeypatch):
    mock_send_mail = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_mail_verify", mock_send_mail)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == 'Account already exists'


def test_request_email(client, user, monkeypatch):
    mock_send_mail = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_mail_verify", mock_send_mail)
    response = client.post("/api/auth/request_email", json=user)
    assert response.status_code == 200, response.text


def test_login_not_found_email(client, user):
    response = client.post("/api/auth/login", data={"username": 'Guest', "password": user.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == 'Invalid email'


def test_login_not_confirmed(client, user):
    response = client.post("/api/auth/login", data={"username": user.get('email'), "password": user.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == 'Email not confirmed'


def test_login(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/api/auth/login", data={"username": user.get('email'), "password": user.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == 'bearer'


def test_login_not_found_password(client, user):
    response = client.post("/api/auth/login", data={"username": user.get('email'), "password": '123456'})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == 'Invalid password'


def test_logout(client, user, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get("/api/auth/logout", headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['detail'] == 'User successfully logout'
