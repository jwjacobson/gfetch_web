import os
import pytest

from email import policy
from email.parser import BytesParser

from emails import clean_body, format_subject, get_attachments, get_body, set_date 

import ipdb

@pytest.fixture()
def raw_no_attachments():
    raw_email_path = os.path.join(os.path.dirname(__file__), 'raw_no_attachments.eml')

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

def test_get_body(raw_no_attachments):
    message = raw_no_attachments
    result = get_body(message)
    expected = "Hey Will,\n\nJust wanted to confirm our plans for later.\n\nLet me know,\nStu\n\n\nOn Mon, Jul 1, 2013 at 5:09 AM, Will Jakobson <will@jmail.com>wrote:\n\n> hey that old link is broken, this one's better, check it\n> out quick\n> http://www.youtube.com/watch?v=r-xd4JQEbfE\n>\n"

    assert result == expected

def test_clean_body(raw_no_attachments):
    message = raw_no_attachments
    body = get_body(message)
    result = clean_body(body)
    expected = 'Hey Will,\n\nJust wanted to confirm our plans for later.\n\nLet me know,\nStu\n\n'

    assert result == expected