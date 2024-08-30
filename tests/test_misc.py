from app import app, create_dirs


def test_create_dirs_already_exist(monkeypatch, temp_dirs):
    monkeypatch.setattr(app.dir_config, "ATTACHMENTS_DIR", temp_dirs["attachments_dir"])
    monkeypatch.setattr(app.dir_config, "CLEAN_EMAIL_DIR", temp_dirs["clean_email_dir"])
    monkeypatch.setattr(app.dir_config, "RAW_EMAIL_DIR", temp_dirs["raw_email_dir"])
    create_dirs(app.dir_config)
    assert True