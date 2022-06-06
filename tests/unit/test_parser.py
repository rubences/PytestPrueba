from datetime import datetime
from unittest.mock import ANY

import pytest

from medium_collector.download.parser import get_subject, parse_mail

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


@pytest.mark.parametrize(
    ["input_subject", "expected"],
    [
        (
            "=?UTF-8?B?V2hlbiBhICQxMDAsMDAwIFNhbGFyeSBJc27igJl0IEVub3VnaCB8IEFkYW0gUGFyc29ucyBpbiBNYWtpbmcgb2YgYSBNaWxsaW8=?= =?UTF-8?B?bmFpcmU=?=",
            "When a $100,000 Salary Isn’t Enough | Adam Parsons in Making of a Millionaire",
        ),
        ("=?UTF-8?B?VGhlcmXigJlz?= more to the story", "There’s more to the story"),
        (
            "7 Things Rich People Advise But Never Do | David O. in The Startup",
            "7 Things Rich People Advise But Never Do | David O. in The Startup",
        ),
    ],
)
def test_get_subject(input_subject, expected):
    actual = get_subject(input_subject)
    assert actual == expected


@pytest.fixture
def dummy_mail():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Link"
    msg["From"] = "you@this.com"
    msg["To"] = "me@that.com"
    msg["Message-ID"] = "123"
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000 (UTC)")

    text = "Hi!"
    html = f"<html><head></head><body><p>{text}<br></body></html>"

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    msg.attach(part1)
    msg.attach(part2)

    return msg


def test_parse_mail(dummy_mail):

    expected_mail_info = {
        "id": "ad841b37bd4b9b5403b575432f67f5ed2d68ed40",
        "to": "a4747a50dad63531704f5ab32509bb0c60b7350f",
        "from": "you@this.com",
        "subject": "Link",
        "date": ANY,
    }
    mail_info, decoded = parse_mail(dummy_mail)

    assert mail_info == expected_mail_info
    assert decoded == "<html><head></head><body><p>Hi!<br></body></html>"
