import ipdb
import os
import pytest

from app import app
from unittest.mock import patch


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


def test_delete_files(test_client, monkeypatch, temp_dirs, temp_files):
    monkeypatch.setattr("app.ATTACHMENTS_DIR", temp_files["attachments_dir"])
    monkeypatch.setattr("app.CLEANED_EMAIL_DIR", temp_files["cleaned_email_dir"])
    monkeypatch.setattr("app.RAW_EMAIL_DIR", temp_files["raw_email_dir"])

    response = test_client.post("/delete/")

    assert response.status_code == 302

    assert not os.listdir(temp_files["attachments_dir"])
    assert not os.listdir(temp_files["cleaned_email_dir"])
    assert not os.listdir(temp_files["raw_email_dir"])

    with test_client.session_transaction() as session:
        messages = [message[1] for message in session["_flashes"] if message[0] == 'message']
        assert "Deleted 2 emails and 2 attachments." in messages