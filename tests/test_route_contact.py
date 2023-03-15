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


def test_create_contact(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        contact = {
            "firstname": 'Test',
            "lastname": 'Test',
            "email": 'test@gmail.com',
            "phone": "099 789-58-87",
        }
        response = client.post("/api/contacts", json=contact,  headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["firstname"] == contact["firstname"]
        assert data["lastname"] == contact["lastname"]
        assert data["email"] == contact["email"]
        assert data["phone"] == contact["phone"]
        assert "id" in data


def test_get_contact(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get("/api/contacts/1", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["firstname"] == 'Test'
        assert data["lastname"] == 'Test'


def test_get_contact_not_found(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get("/api/contacts/2", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"


def test_get_contacts(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["firstname"] == 'Test'


def test_update_contact(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        contact = {
            "firstname": 'Guest',
            "lastname": 'Test',
            "email": 'test@gmail.com',
            "phone": "099 789-58-87",
        }
        response = client.put("/api/contacts/1", json=contact, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["firstname"] == contact["firstname"]
        assert data["lastname"] == contact["lastname"]
        assert data["email"] == contact["email"]
        assert data["phone"] == contact["phone"]


def test_update_contact_not_found(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        contact = {
            "firstname": 'Guest',
            "lastname": 'Test',
            "email": 'test@gmail.com',
            "phone": "099 789-58-87",
        }
        response = client.put("/api/contacts/3", json=contact, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"


def test_update_born_date_of_contact(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        contact = {"born_date": '1989-03-16'}
        response = client.patch("/api/contacts/birthday/1", json=contact, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["firstname"] == 'Guest'
        assert data["born_date"] == contact["born_date"]


def test_update_born_date_of_contact_not_found(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        contact = {"born_date": '1989-03-16'}
        response = client.patch("/api/contacts/birthday/3", json=contact, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"


def test_update_notes_of_contact(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        contact = {"notes": 'Hello! I am Guest.'}
        response = client.patch("/api/contacts/notes/1", json=contact, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["firstname"] == 'Guest'
        assert data["notes"] == contact["notes"]


def test_update_notes_of_contact_not_found(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        contact = {"notes": 'Hello! I am Guest.'}
        response = client.patch("/api/contacts/notes/2", json=contact, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"


def test_get_birthdays(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get("/api/contacts/birthdays/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) == list

def test_remove_contact_not_found(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.delete("/api/contacts/2", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"


def test_remove_contact(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.delete("/api/contacts/1", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 204, response.text

