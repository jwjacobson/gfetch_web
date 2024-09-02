import os
import pytest

from email import policy
from email.parser import BytesParser

from emails import set_date, format_subject, get_attachments

import ipdb

@pytest.fixture()
def raw_no_attachments():
    raw_email_path = 'tests/raw_no_attachments.eml'

    with open(raw_email_path, "rb") as raw_email:
        message = BytesParser(policy=policy.default).parse(raw_email)
        yield message

def test_set_date_no_attachments(raw_no_attachments):
    message = raw_no_attachments
    raw_date = message["Date"]
    result = set_date(raw_date)
    expected = '2013-07-05'

    assert result == expected

def test_format_subject_re_only(raw_no_attachments):
    message = raw_no_attachments
    subject = message["Subject"]
    result = format_subject(subject)
    expected = 're'

    assert result == expected

def test_get_attachments_no_attachments(raw_no_attachments, temp_dirs):
    message = raw_no_attachments
    result = get_attachments(message, temp_dirs["attachments_dir"])
    expected = []

    assert result == expected