import pytest

from app import app

@pytest.fixture(scope="session")
def test_client():
    """The Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="session")
def temp_dirs(tmp_path_factory):
    """
    Create temporary directories to delete files from.
    """
    attachments_dir = tmp_path_factory.mktemp("attachments")
    cleaned_email_dir = tmp_path_factory.mktemp("cleaned_emails")
    raw_email_dir = tmp_path_factory.mktemp("raw_emails")


    return {
        "attachments_dir": attachments_dir,
        "cleaned_email_dir": cleaned_email_dir,
        "raw_email_dir": raw_email_dir
    }

@pytest.fixture
def temp_files_all(temp_dirs):
    """
    Create fake email and attachment files in the temp directories.
    """
    (temp_dirs["attachments_dir"] / "file1.pdf").touch()
    (temp_dirs["attachments_dir"] / "file2.docx").touch()

    (temp_dirs["cleaned_email_dir"] / "email1.txt").touch()
    (temp_dirs["cleaned_email_dir"] / "email2.txt").touch()

    (temp_dirs["raw_email_dir"] / "email1.eml").touch()
    (temp_dirs["raw_email_dir"] / "email2.eml").touch()

    return temp_dirs

@pytest.fixture
def temp_files_no_attachments(temp_dirs):
    """
    Create fake email and attachment files in the temp directories.
    """
    (temp_dirs["cleaned_email_dir"] / "email1.txt").touch()
    (temp_dirs["cleaned_email_dir"] / "email2.txt").touch()

    (temp_dirs["raw_email_dir"] / "email1.eml").touch()
    (temp_dirs["raw_email_dir"] / "email2.eml").touch()

    return temp_dirs

@pytest.fixture
def temp_files_no_clean(temp_dirs):
    """
    Create fake email and attachment files in the temp directories.
    """
    (temp_dirs["attachments_dir"] / "file1.pdf").touch()
    (temp_dirs["attachments_dir"] / "file2.docx").touch()

    (temp_dirs["raw_email_dir"] / "email1.eml").touch()
    (temp_dirs["raw_email_dir"] / "email2.eml").touch()

    return temp_dirs

@pytest.fixture
def temp_files_no_raw(temp_dirs):
    """
    Create fake email and attachment files in the temp directories.
    """
    (temp_dirs["attachments_dir"] / "file1.pdf").touch()
    (temp_dirs["attachments_dir"] / "file2.docx").touch()

    (temp_dirs["cleaned_email_dir"] / "email1.txt").touch()
    (temp_dirs["cleaned_email_dir"] / "email2.txt").touch()

    return temp_dirs