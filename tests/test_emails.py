import os
import pytest

from email import policy
from email.parser import BytesParser

from app import app
from emails import (
    build_email_content,
    # clean_body,
    clean_email,
    format_subject,
    get_attachments,
    get_body,
    set_date,
)

import ipdb


@pytest.fixture()
def no_attachments():
    """
    Read and yield a raw email file with no attachments.
    """
    filename = "no_attachments.eml"
    raw_email_path = os.path.join(os.path.dirname(__file__), "raw_emails", filename)

    with open(raw_email_path, "rb") as raw_email:
        message = BytesParser(policy=policy.default).parse(raw_email)
        message_id = 'test_id_01'
        yield message, filename, raw_email_path, message_id


@pytest.fixture()
def one_attachment():
    """
    Read and yield a raw email file with one attachment.
    """

    filename = "one_attachment.eml"
    raw_email_path = os.path.join(os.path.dirname(__file__), "raw_emails", filename)

    with open(raw_email_path, "rb") as raw_email:
        message = BytesParser(policy=policy.default).parse(raw_email)
        message_id = 'test_id_10'
        yield message, filename, raw_email_path, message_id


@pytest.fixture()
def many_attachments():
    """
    Read and yield a raw email file with many attachments.
    """
    filename = "many_attachments.eml"
    raw_email_path = os.path.join(os.path.dirname(__file__), "raw_emails", filename)

    with open(raw_email_path, "rb") as raw_email:
        message = BytesParser(policy=policy.default).parse(raw_email)
        message_id = 'test_id_11'
        yield message, filename, raw_email_path, message_id


def test_set_date_no_attachments(no_attachments):
    message = no_attachments[0]
    raw_date = message["Date"]
    result = set_date(raw_date)
    expected = "2013-07-05"

    assert result == expected


def test_format_subject_re_only(no_attachments):
    message = no_attachments[0]
    subject = message["Subject"]
    result = format_subject(subject)
    expected = "re"

    assert result == expected


def test_format_subject_normal_text_no_caps(one_attachment):
    message = one_attachment[0]
    subject = message["Subject"]
    result = format_subject(subject)
    expected = "beautifulandstunning"

    assert result == expected


def test_get_attachments_no_attachments(no_attachments, temp_dirs):
    message = no_attachments[0]
    attachments_dir = temp_dirs["attachments_dir"]
    result = get_attachments(message, attachments_dir)
    expected = []

    assert result == expected
    assert not os.listdir(attachments_dir)


def test_get_attachments_one_attachment(one_attachment, temp_dirs):
    message = one_attachment[0]
    attachments_dir = temp_dirs["attachments_dir"]
    result = get_attachments(message, attachments_dir)
    expected = ["beautifulandstunning.png"]

    assert result == expected
    assert len(result) == 1
    assert len(os.listdir(attachments_dir)) == 1
    for file in result:
        assert file in os.listdir(attachments_dir)
    for file in os.listdir(attachments_dir):
        assert file in expected


def test_get_attachments_many_attachments(many_attachments, temp_dirs):
    message = many_attachments[0]
    attachments_dir = temp_dirs["attachments_dir"]
    result = get_attachments(message, attachments_dir)
    expected = [
        "ADVICE TO NEW TEACHERS.pdf",
        "CREDULOUDLY RAPT.pdf",
        "HOW TO GRADE IMPERSONALLY.pdf",
        "I'D RATHER SPEND NEW YEAR'S IN A BARN.pdf",
        "THE DISASTER ODDS.pdf",
        "TRESSPASSING AT THE PUMPING STATION.pdf",
    ]

    assert result == expected
    assert len(result) == 6
    assert len(os.listdir(attachments_dir)) == 6
    for file in result:
        assert file in os.listdir(attachments_dir)
    for file in os.listdir(attachments_dir):
        assert file in expected


def test_get_body_happy(no_attachments):
    message = no_attachments[0]
    result = get_body(message)
    expected = "Hey Will,\n\nJust wanted to confirm our plans for later.\n\nLet me know,\nStu\n\n"
    assert result == expected

def test_get_body_nested(many_attachments):
    message = many_attachments[0]
    result = get_body(message)
    expected = 'Just some drafts.\n'

    assert result == expected


# def test_clean_body(no_attachments):
#     message = no_attachments[0]
#     body = get_body(message)
#     result = clean_body(body)
#     expected = "Hey Will,\n\nJust wanted to confirm our plans for later.\n\nLet me know,\nStu\n\n"

#     assert result == expected


def test_build_email_content_no_attachments(no_attachments, temp_dirs):
    message, raw_file = no_attachments[0], no_attachments[1]
    date = set_date(message["Date"])
    subject = message["Subject"]
    to = message["To"]
    from_ = message["From"]
    attachments = get_attachments(message, temp_dirs["attachments_dir"])
    body = get_body(message)

    result = build_email_content(raw_file, date, subject, to, from_, attachments, body)
    expected = "***no_attachments.eml***\nDATE: 2013-07-05\nSUBJECT: Re:\nTO: Will Jakobson <will@jmail.com>\nFROM: Stu Bettler <stu@bmail.com>\n\nHey Will,\n\nJust wanted to confirm our plans for later.\n\nLet me know,\nStu\n\n"

    assert result == expected


def test_build_email_content_one_attachment(one_attachment, temp_dirs):
    message, raw_file = one_attachment[0], one_attachment[1]
    date = set_date(message["Date"])
    subject = message["Subject"]
    to = message["To"]
    from_ = message["From"]
    attachments = get_attachments(message, temp_dirs["attachments_dir"])
    body = get_body(message)

    result = build_email_content(raw_file, date, subject, to, from_, attachments, body)
    expected = "***one_attachment.eml***\nDATE: 2011-07-10\nSUBJECT: beautiful and stunning\nTO: stu bettler <stu@bmail.com>\nFROM: Will Jakobson <will@jmail.com>\nATTACHMENTS:\n- beautifulandstunning.png\n\ni just saw this.  made me chuckle, and reminded me of writing alone.\n"

    assert result == expected

def test_build_email_content_many_attachments(many_attachments, temp_dirs):
    message, raw_file = many_attachments[0], many_attachments[1]
    date = set_date(message["Date"])
    subject = message["Subject"]
    to = message["To"]
    from_ = message["From"]
    attachments = get_attachments(message, temp_dirs["attachments_dir"])
    body = get_body(message)

    result = build_email_content(raw_file, date, subject, to, from_, attachments, body)
    expected = "***many_attachments.eml***\nDATE: 2015-06-19\nSUBJECT: Revisions\nTO: Stu Bettler <stu@bmail.com>, Will Jakobson <will@jmail.com>\nFROM: Stu Bettler <stu@bmail.com>\nATTACHMENTS:\n- ADVICE TO NEW TEACHERS.pdf\n- CREDULOUDLY RAPT.pdf\n- HOW TO GRADE IMPERSONALLY.pdf\n- I'D RATHER SPEND NEW YEAR'S IN A BARN.pdf\n- THE DISASTER ODDS.pdf\n- TRESSPASSING AT THE PUMPING STATION.pdf\n\nJust some drafts.\n"

    assert result == expected

def test_clean_email_no_attachments(monkeypatch, no_attachments, temp_dirs):
    attachments_dir = temp_dirs["attachments_dir"]
    clean_dir = temp_dirs["clean_email_dir"]

    monkeypatch.setattr(app.dir_config, "ATTACHMENTS_DIR", attachments_dir)
    monkeypatch.setattr(app.dir_config, "CLEAN_EMAIL_DIR", clean_dir)
    filepath = no_attachments[2]
    message_id = no_attachments[3]
    expected_filename = '2013-07-05__re__test_id_01.txt'
    
    assert not os.listdir(clean_dir) # Make sure the target directory is empty for comparison
    
    clean_email(filepath, app.dir_config, message_id)

    assert len(os.listdir(clean_dir)) == 1
    assert expected_filename in os.listdir(clean_dir)
    assert not os.listdir(attachments_dir)

def test_clean_email_one_attachment(monkeypatch, one_attachment, temp_dirs):
    attachments_dir = temp_dirs["attachments_dir"]
    clean_dir = temp_dirs["clean_email_dir"]

    monkeypatch.setattr(app.dir_config, "ATTACHMENTS_DIR", attachments_dir)
    monkeypatch.setattr(app.dir_config, "CLEAN_EMAIL_DIR", clean_dir)
    filepath = one_attachment[2]
    message_id = one_attachment[3]
    expected_email_filename = '2011-07-10__beautifulandstunning__test_id_10.txt'
    expected_attachment_filename = 'beautifulandstunning.png'
    
    assert not os.listdir(clean_dir) # Make sure the target directories are empty for comparison
    assert not os.listdir(attachments_dir)

    clean_email(filepath, app.dir_config, message_id)

    assert len(os.listdir(clean_dir)) == 1
    assert len(os.listdir(attachments_dir)) == 1
    assert expected_email_filename in os.listdir(clean_dir)
    assert expected_attachment_filename in os.listdir(attachments_dir)

def test_clean_email_many_attachments(monkeypatch, many_attachments, temp_dirs):
    attachments_dir = temp_dirs["attachments_dir"]
    clean_dir = temp_dirs["clean_email_dir"]

    monkeypatch.setattr(app.dir_config, "ATTACHMENTS_DIR", attachments_dir)
    monkeypatch.setattr(app.dir_config, "CLEAN_EMAIL_DIR", clean_dir)
    filepath = many_attachments[2]
    message_id = many_attachments[3]
    expected_email_filename = '2015-06-19__revisions__test_id_11.txt'
    expected_attachment_filenames = [
        "ADVICE TO NEW TEACHERS.pdf",
        "CREDULOUDLY RAPT.pdf",
        "HOW TO GRADE IMPERSONALLY.pdf",
        "I'D RATHER SPEND NEW YEAR'S IN A BARN.pdf",
        "THE DISASTER ODDS.pdf",
        "TRESSPASSING AT THE PUMPING STATION.pdf",
    ]

    assert not os.listdir(clean_dir) # Make sure the target directories are empty for comparison
    assert not os.listdir(attachments_dir)

    clean_email(filepath, app.dir_config, message_id)

    assert len(os.listdir(clean_dir)) == 1
    assert len(os.listdir(attachments_dir)) == 6
    assert expected_email_filename in os.listdir(clean_dir)
    for filename in expected_attachment_filenames:
        assert filename in os.listdir(attachments_dir)