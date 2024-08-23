import ipdb
import os
import pytest

from app import app

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