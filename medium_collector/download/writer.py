import csv

from medium_collector.csv_configs import EMAILS_ARTICLES_HEADERS, EMAILS_FILE_HEADERS
from medium_collector.download.parser import get_articles, parse_mail


def write_articles(file, articles, mail_id):
    with open(file, "a") as mail_article_writable:
        mail_article_writer = csv.DictWriter(
            mail_article_writable, fieldnames=EMAILS_ARTICLES_HEADERS
        )

        for article in articles:
            article["mail_id"] = mail_id
            mail_article_writer.writerow(article)


def write_emails(emails_csv, email_articles_csv, messages):
    new_checkpoint = -1
    with open(emails_csv, "a") as writable:
        mails_writer = csv.DictWriter(writable, fieldnames=EMAILS_FILE_HEADERS)
        for msg_id, email in messages:
            mail_info, decoded_mail = parse_mail(email)

            articles = get_articles(decoded_mail)
            write_articles(email_articles_csv, articles, mail_info["id"])
            mails_writer.writerow(mail_info)

            new_checkpoint = msg_id
    return new_checkpoint
