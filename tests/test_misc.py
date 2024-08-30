from app import app, create_dirs


def test_create_dirs_already_exist(monkeypatch, temp_dirs):
    monkeypatch.setattr(app.dir_config, "ATTACHMENTS_DIR", temp_dirs["attachments_dir"])
    monkeypatch.setattr(app.dir_config, "CLEAN_EMAIL_DIR", temp_dirs["clean_email_dir"])
    monkeypatch.setattr(app.dir_config, "RAW_EMAIL_DIR", temp_dirs["raw_email_dir"])
    create_dirs(app.dir_config)
    assert True

def test_create_dirs_not_exist(monkeypatch, tmp_path):
    attachments_dir = tmp_path / "attachments"
    clean_email_dir = tmp_path / "cleaned_emails"
    raw_email_dir = tmp_path / "raw_emails"

    assert not attachments_dir.exists()
    assert not clean_email_dir.exists()
    assert not raw_email_dir.exists()

    monkeypatch.setattr(app.dir_config, "ATTACHMENTS_DIR", attachments_dir)
    monkeypatch.setattr(app.dir_config, "CLEAN_EMAIL_DIR", clean_email_dir)
    monkeypatch.setattr(app.dir_config, "RAW_EMAIL_DIR", raw_email_dir)
    
    create_dirs(app.dir_config)

    assert attachments_dir.exists()
    assert clean_email_dir.exists()
    assert raw_email_dir.exists()
