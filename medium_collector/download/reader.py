import email

from imapclient import IMAPClient


def read_from_mail(imap_server, account, password, folder, checkpoint=0):
    with IMAPClient(host=imap_server, use_uid=True) as client:
        client.login(account, password)
        client.select_folder(folder, readonly=True)
        messages = client.search(["NOT", "DELETED"])
        for message_id in messages[checkpoint:]:
            fetched = client.fetch(message_id, "RFC822")
            data = fetched[message_id]
            email_message = email.message_from_bytes(data[b"RFC822"])
            yield message_id, email_message
