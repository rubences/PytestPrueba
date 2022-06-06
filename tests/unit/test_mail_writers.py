from unittest.mock import patch, MagicMock

import pytest

from medium_collector.download.writer import write_articles, write_emails


@pytest.fixture
def sample_articles():
    return [
        {
            "post_url": "http://blogspot.com/nulla/",
            "post_title": "clonidine hydrochloride",
            "post_subtitle": "Sudden Death",
            "section_title": "Nanjing University of Chemical Technology",
            "members_only": True,
            "author_name": "Blanch Pordal",
            "author_handle": "bpordal0",
            "site_name": "Mazda",
            "site_slug": "Familia",
        },
        {
            "post_url": "https://lulu.com/velit.html",
            "post_title": "Cefprozil",
            "post_subtitle": "Life of Pi",
            "section_title": "University of Sydney",
            "members_only": False,
            "author_name": "Verene Sunman",
            "author_handle": "vsunman1",
            "site_name": "Dodge",
            "site_slug": "Caliber",
        },
        {
            "post_url": "https://cbc.ca/dictumst/",
            "post_title": "stavudine",
            "post_subtitle": "Used People",
            "section_title": "Université Hassan II - Mohammadia",
            "members_only": False,
            "author_name": "Marcus Redd",
            "author_handle": "mredd2",
            "site_name": None,
            "site_slug": None,
        },
    ]


@pytest.fixture
def sample_emails():
    return [
        {
            "id": "4c84ea2fa5088be3693308c805837e220c4897bf",
            "date": "2020-02-07T02:26:35Z",
            "to": "05911b05795fe3be24665eee3733da8a224b485f",
            "from": "candreolli0@youku.com",
            "subject": "Melastomataceae",
        },
        {
            "id": "31dc98cbd4006051d11db0336b95346521919fe2",
            "date": "2019-09-18T01:02:44Z",
            "to": "e932c2fce3ad0d7a313953e23d0a64da7528bf28",
            "from": "mjacquemard1@kickstarter.com",
            "subject": "Rubiaceae",
        },
        {
            "id": "3ce84d6f59bae3cc0c44ce1a7a2953e0e202d060",
            "date": "2019-06-17T01:59:59Z",
            "to": "a580c3aedc3a28b2ce94a4a716fdd381019d0fdb",
            "from": "gwellbank2@soup.io",
            "subject": "Apocynaceae",
        },
    ]


def test_write_articles(create_files, sample_articles):
    emails_csv, emails_articles_csv = create_files(True)

    expected = """\
id,date,to,from,subject
an_id,http://blogspot.com/nulla/,clonidine hydrochloride,Sudden Death,Nanjing University of Chemical Technology,True,Blanch Pordal,bpordal0,Mazda,Familia
an_id,https://lulu.com/velit.html,Cefprozil,Life of Pi,University of Sydney,False,Verene Sunman,vsunman1,Dodge,Caliber
an_id,https://cbc.ca/dictumst/,stavudine,Used People,Université Hassan II - Mohammadia,False,Marcus Redd,mredd2,,
"""

    write_articles(emails_csv, sample_articles, "an_id")

    assert open(emails_csv).read() == expected


@patch("medium_collector.download.writer.get_articles")
@patch("medium_collector.download.writer.write_articles")
@patch("medium_collector.download.writer.parse_mail")
def test_write_emails(
    parse_mail_mock, write_articles_mock, get_articles_mock, create_files, sample_emails
):
    emails_csv, emails_articles_csv = create_files(True)
    messages = [(idx, message) for idx, message in enumerate(sample_emails)]
    parse_mail_mock.side_effect = lambda message: (message, MagicMock())
    expected_checkpoint = 2
    expected_content = """\
id,date,to,from,subject
4c84ea2fa5088be3693308c805837e220c4897bf,2020-02-07T02:26:35Z,05911b05795fe3be24665eee3733da8a224b485f,candreolli0@youku.com,Melastomataceae
31dc98cbd4006051d11db0336b95346521919fe2,2019-09-18T01:02:44Z,e932c2fce3ad0d7a313953e23d0a64da7528bf28,mjacquemard1@kickstarter.com,Rubiaceae
3ce84d6f59bae3cc0c44ce1a7a2953e0e202d060,2019-06-17T01:59:59Z,a580c3aedc3a28b2ce94a4a716fdd381019d0fdb,gwellbank2@soup.io,Apocynaceae
"""

    actual_checkpoint = write_emails(emails_csv, emails_articles_csv, messages)

    assert expected_checkpoint == actual_checkpoint
    assert get_articles_mock.call_count == len(messages)
    assert parse_mail_mock.call_count == len(messages)
    assert write_articles_mock.call_count == len(messages)
    assert open(emails_csv).read() == expected_content
