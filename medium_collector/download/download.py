import logging
from pathlib import Path

from decouple import config

from medium_collector.csv_configs import EMAILS_ARTICLES_HEADERS, EMAILS_FILE_HEADERS
from medium_collector.download.reader import read_from_mail
from medium_collector.download.writer import write_emails

logger = logging.getLogger(__name__)


def write_headers(file, headers):
    with open(file, "w") as writable:
        writable.write(",".join(headers))
        writable.write("\n")


def read_checkpoint(data_path):
    try:
        with open(data_path / "checkpoint.txt") as readable:
            return int(readable.read())
    except:
        return 0


def write_checkpoint(data_path, checkpoint):
    with open(data_path / "checkpoint.txt", "w") as writable:
        writable.write(str(checkpoint))
        writable.write("\n")


def download_from_mail(data_path, dry_run=False):
    emails_csv = Path(data_path, "mails.csv")
    email_articles_csv = Path(data_path, "articles_mails.csv")

    if not emails_csv.exists():
        write_headers(emails_csv, EMAILS_FILE_HEADERS)
    if not email_articles_csv.exists():
        write_headers(email_articles_csv, EMAILS_ARTICLES_HEADERS)

    checkpoint = read_checkpoint(data_path)
    logger.info("starting to pull messages from %d" % checkpoint)

    messages = read_from_mail(
        config("IMAP_SERVER"),
        config("EMAIL_ACCOUNT"),
        config("EMAIL_PASS"),
        "INBOX.Daily Digests",
        checkpoint=checkpoint,
    )
    if dry_run:
        logger.info("this is a dry run")
        new_checkpoint = checkpoint
    else:
        new_checkpoint = write_emails(emails_csv, email_articles_csv, messages)
        new_checkpoint = max(checkpoint, new_checkpoint)

    write_checkpoint(data_path, new_checkpoint)
    logger.info("done pulling messages, the new checkpoint is %d" % new_checkpoint)
