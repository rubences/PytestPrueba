import pytest
from pathlib import Path
from medium_collector.csv_configs import EMAILS_FILE_HEADERS, EMAILS_ARTICLES_HEADERS
import csv


@pytest.fixture
def create_files(tmp_path):
    data_path = tmp_path
    emails_csv = Path(data_path, "mails.csv")
    email_articles_csv = Path(data_path, "articles_mails.csv")

    def _create_files(create):
        if create:
            with open(emails_csv, "w") as writeable:
                writer = csv.DictWriter(writeable, fieldnames=EMAILS_FILE_HEADERS)
                writer.writeheader()
            with open(email_articles_csv, "w") as writeable:
                writer = csv.DictWriter(writeable, fieldnames=EMAILS_ARTICLES_HEADERS)
                writer.writeheader()

        return emails_csv, email_articles_csv

    return _create_files
