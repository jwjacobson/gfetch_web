import ipdb
import os
import pytest

from app import app
from unittest.mock import patch

@pytest.fixture
def test_client():
    # Flask provides a test client you can use to simulate requests
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def mock_os_listdir(path):
    if path == "test_attachments_dir":
        return ["file1.pdf", "file2.docx", "file.mp3"]
    elif path == "test_cleaned_email_dir":
        return ["email1.txt", "email2.txt", "email3.txt"]
    elif path == "test_raw_email_dir":
        return ["email1.eml", "email2.eml", "email3.eml"]
    return []

def mock_os_remove(path):
    print(f"Mock remove called for: {path}")

def test_delete_files(test_client, monkeypatch):
    monkeypatch.setattr(os, "listdir", mock_os_listdir)
    monkeypatch.setattr(os, "remove", mock_os_remove)
    
    response = test_client.post("/delete/")
    
    assert response.status_code == 302