import ipdb
import os
import pytest

from app import app
from unittest.mock import patch

@pytest.fixture
def temp_dirs(tmp_path_factory):
    attachments_dir = tmp_path_factory.mktemp("attachments")
    cleaned_email_dir = tmp_path_factory.mktemp("cleaned_emails")
    raw_email_dir = tmp_path_factory.mktemp("raw_emails")


    return {
        "attachments_dir": attachments_dir,
        "cleaned_email_dir": cleaned_email_dir,
        "raw_email_dir": raw_email_dir
    }


def test_delete_files_empty_dirs(test_client, monkeypatch, temp_dirs):
    monkeypatch.setattr("app.ATTACHMENTS_DIR", temp_dirs["attachments_dir"])
    monkeypatch.setattr("app.CLEANED_EMAIL_DIR", temp_dirs["cleaned_email_dir"])
    monkeypatch.setattr("app.RAW_EMAIL_DIR", temp_dirs["raw_email_dir"])

    response = test_client.post("/delete/")

    assert response.status_code == 302
    with test_client.session_transaction() as session:
        messages = [message[1] for message in session["_flashes"] if message[0] == 'message']
        assert "No attachments found." in messages
        assert "No cleaned emails found." in messages
        assert "No raw emails found." in messages


