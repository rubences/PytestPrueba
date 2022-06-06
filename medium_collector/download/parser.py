import datetime
import email
import hashlib
import quopri

from bs4 import BeautifulSoup

MEDIUM_URL = "https://medium.com/"
URL_LEN = len(MEDIUM_URL)


def get_subject(subject):
    subject_parts = []
    subjects = email.header.decode_header(subject)
    for content, encoding in subjects:
        try:
            subject_parts.append(content.decode(encoding or "utf8"))
        except:
            subject_parts.append(content)
    return "".join(subject_parts)


def get_message_id(to, message_id):
    sh1 = hashlib.sha1()
    sh1.update(to.encode())
    sh1.update(message_id.encode())
    return sh1.hexdigest()


def mask_to(to):
    return hashlib.sha1(to.encode()).hexdigest()


def parse_mail(email_message):
    parts = {part.get_content_type(): part for part in email_message.get_payload()}
    decoded = quopri.decodestring(parts["text/html"].get_payload()).decode("utf8")
    to = email_message["To"]
    mail_info = {
        "id": get_message_id(to, email_message["Message-ID"]),
        "to": mask_to(to),
        "from": email_message.get("From"),
        "subject": get_subject(email_message.get("Subject")),
        "date": datetime.datetime.strptime(
            email_message.get("Date"), "%a, %d %b %Y %H:%M:%S +0000 (%Z)"
        ),
    }
    return mail_info, decoded


def get_articles(message):
    soup = BeautifulSoup(message, "lxml")
    main = soup.find("table", {"class": "email-fillWidth"})
    digest = main.find("table", {"class": "email-digest"})

    sections = digest.find_all("tr", recursive=False)

    for section in sections:
        [table_cell] = section.findChildren("td", recursive=False)
        section_title_div = table_cell.find("div")

        if section_title_div is None:
            continue

        section_title = section_title_div.text

        article_tables = table_cell.findChildren("table", recursive=False)

        for article in article_tables:
            post_title = article.find(
                "div", {"class": "email-digestPostTitle--hero"}
            ) or article.find("div", {"class": "email-digestPostTitle"})
            post_subtitle = article.find("div", {"class": "email-digestPostSubtitle"})

            post_url, _, _ = post_title.parent.find("a")["href"].partition("?")

            anchors = article.find_all("a")
            author = (None, None)
            site = (None, None)

            for anchor in anchors:
                url = anchor["href"][URL_LEN:]
                first, _, _ = url.partition("?")
                if first.startswith("@"):
                    author = (anchor.text, first)
                else:
                    site = (anchor.text, first)

            members_only = (
                article.find("img", {"class": "email-digestMemberOnlyStar"}) is not None
            )

            data = {
                "section_title": section_title,
                "post_title": post_title.text,
                "post_subtitle": post_subtitle.text if bool(post_subtitle) else None,
                "post_url": post_url,
                "author_name": author[0],
                "author_handle": author[1],
                "site_name": site[0],
                "site_slug": site[1],
                "members_only": members_only,
            }
            yield data
