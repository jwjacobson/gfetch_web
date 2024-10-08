import pytest

from app import app, DirConfig
from unittest.mock import Mock, patch, create_autospec
from google.auth.credentials import Credentials


@pytest.fixture()
def mock_token(tmp_path):
    """Create a temporary mock token."""
    token = tmp_path / "token.json"
    return token


def test_get(test_client):
    response = test_client.get("/")

    assert response.status_code == 200


def test_post_empty_request(test_client):
    response = test_client.post("/")

    assert response.status_code == 400


def test_post_no_creds(test_client, monkeypatch, mock_token):
    mock_creds = None
    monkeypatch.setattr("auth.get_credentials", lambda: mock_creds)
    monkeypatch.setattr("auth.TOKEN", mock_token)

    response = test_client.post("/", data={"email_address": "biff@email.com"})

    assert response.status_code == 302

    with test_client.session_transaction() as session:
        messages = [
            message[1] for message in session["_flashes"] if message[0] == "message"
        ]
        assert "Failed to obtain credentials." in messages


@pytest.mark.skip(reason="Haven't gotten this working yet")
def test_post_no_build(test_client, monkeypatch, mock_token):
    mock_creds = create_autospec(Credentials)
    mock_creds.universe_domain = "googleapis.com"
    monkeypatch.setattr("auth.TOKEN", mock_token)

    monkeypatch.setattr("auth.get_credentials", lambda: mock_creds)

    response = test_client.post("/", data={"email_address": "biff@email.com"})

    assert response.status_code == 302

    with test_client.session_transaction() as session:
        messages = [
            message[1] for message in session["_flashes"] if message[0] == "message"
        ]
        assert "Error building Gmail service:" in messages
