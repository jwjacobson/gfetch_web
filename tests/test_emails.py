import os
import pytest

from email import policy
from email.parser import BytesParser

from emails import set_date

import ipdb

@pytest.fixture()
def raw_no_attachments():
    raw_email_path = 'tests/raw_no_attachments.eml'

    with open(raw_email_path, "rb") as raw_email:
        message = BytesParser(policy=policy.default).parse(raw_email)
        yield message

def test_set_date(temp_dirs, raw_no_attachments):
    message = raw_no_attachments
    raw_date = message["Date"]
    result = set_date(raw_date)
    expected = '2013-07-05'

    assert result == expected
