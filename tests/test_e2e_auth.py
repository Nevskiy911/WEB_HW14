from unittest.mock import MagicMock

import pytest
from sqlalchemy import select

from src.database.models import Account
from tests.conftest import TestingSessionLocal
from src.conf import messages

acc_mock = {
    "username": "borisjhonsone",
    "email": "greatebritain@england.com",
    "password": "putinloh",
}


def test_create_acc(client, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    response = client.post("/auth/signup", json=acc_mock)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data.get("email") == acc_mock.get("email")
    assert data.get("username") == acc_mock.get("username")
    assert "avatar" in data


def test_repeat_create_acc(client, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    response = client.post("/auth/signup", json=acc_mock)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data.get("detail") == messages.ACCOUNT_EXISTS


def test_login_acc_not_confirmed(client, monkeypatch):
    response = client.post(
        "/auth/login",
        data={
            "username": acc_mock.get("email"),
            "password": acc_mock.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data.get("detail") == messages.EMAIL_NOT_CONFIRMED


@pytest.mark.asyncio
async def test_login_acc(client, monkeypatch):
    async with TestingSessionLocal() as session:
        current_acc = await session.execute(
            select(Account).filter(Account.email == acc_mock.get("email"))
        )
        current_acc = current_acc.scalar_one_or_none()
        current_acc.confirmed = True
        await session.commit()

        response = client.post(
            "/auth/login",
            data={
                "username": acc_mock.get("email"),
                "password": acc_mock.get("password"),
            },
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_acc(client, monkeypatch):
    response = client.post(
        "/auth/login",
        data={
            "username": acc_mock.get("email"),
            "password": "password",
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data.get("detail") == messages.INVALID_PASS


def test_login_wrong_email_acc(client, monkeypatch):
    response = client.post(
        "/auth/login",
        data={
            "username": "email@ex.com",
            "password": acc_mock.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data.get("detail") == messages.INVALID_EMAIL