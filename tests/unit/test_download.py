from unittest.mock import patch, MagicMock

import pytest

from medium_collector.download import download


@pytest.mark.parametrize(
    ["starting_checkpoint", "returned_checkpoint", "expected_checkpoint"],
    [(3, -1, 3), (0, -1, 0), (0, 10, 10)],
)
@pytest.mark.parametrize("create", [True, False])
def test_download_from_mail(
    tmp_path,
    create_files,
    patch_env,
    create,
    starting_checkpoint,
    returned_checkpoint,
    expected_checkpoint,
):
    data_path = tmp_path
    create_files(create)
    messages = MagicMock()
    with patch(
        "medium_collector.download.download.read_from_mail", return_value=messages
    ) as read_from_mail_mock:
        with patch(
            "medium_collector.download.download.write_emails",
            return_value=returned_checkpoint,
        ):
            with patch(
                "medium_collector.download.download.read_checkpoint",
                return_value=starting_checkpoint,
            ):
                download.download_from_mail(data_path)

                read_from_mail_mock.assert_called_once_with(
                    "localhost",
                    "me@this.com",
                    "pa$$word",
                    "INBOX.Daily Digests",
                    checkpoint=starting_checkpoint,
                )

    assert open(data_path / "mails.csv").read() == "id,date,to,from,subject\n"
    assert (
        open(data_path / "articles_mails.csv").read()
        == "mail_id,post_url,post_title,post_subtitle,section_title,members_only,author_name,author_handle,site_name,site_slug\n"
    )
    assert open(data_path / "checkpoint.txt").read() == f"{expected_checkpoint}\n"
