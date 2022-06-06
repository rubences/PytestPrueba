from contextlib import contextmanager
from unittest.mock import patch

import boto3
from decouple import UndefinedValueError
from moto import mock_s3
from ast import literal_eval
import pytest


from medium_collector.s3 import get_file_hashes, upload_files
from pathlib import Path
import pytest


@pytest.fixture
def files_path(pytestconfig):
    return Path(pytestconfig.rootdir, "tests", "fixtures", "files")


@pytest.fixture
def expected_hashes(files_path):
    return {
        Path(files_path, "articles_mails.csv"): "0f1627a2ee3c9ca01c1942c3312f43e4",
        Path(files_path, "mails.csv"): "23bf16661902e7cb9c89e9172fe17abb",
    }


@pytest.fixture
def bucket():
    return "dummy"


@pytest.fixture
def environment(environment, bucket):
    return {"BUCKET": bucket, "ACCESS_KEY": "akey", "SECRET_KEY": "secret"}


@pytest.fixture
def mock_storage(files_path, bucket):
    @contextmanager
    def inner(create_files=True, create_bucket=True):
        with mock_s3():
            if create_bucket:
                conn = boto3.client("s3", region_name="eu-east-1")
                conn.create_bucket(Bucket=bucket)
                if create_files:
                    conn.upload_file(str(files_path / "mails.csv"), bucket, "mails.csv")
                    conn.upload_file(
                        str(files_path / "articles_mails.csv"),
                        bucket,
                        "articles_mails.csv",
                    )
            yield

    return inner


def test_get_file_hashes(files_path, expected_hashes):
    actual = get_file_hashes(files_path)
    assert actual == expected_hashes


def test_upload_files_without_key(files_path, mock_storage):
    with mock_storage(create_bucket=False):
        with pytest.raises(UndefinedValueError):
            upload_files(files_path)


@pytest.mark.parametrize("create_files", [True, False])
def test_upload_files(
    create_files, files_path, patch_env, bucket, mock_storage, expected_hashes
):
    expected_content = {key.name: value for key, value in expected_hashes.items()}
    with mock_storage(create_files):
        upload_files(files_path)
        client = boto3.client("s3", region_name="eu-east-1")
        contents = client.list_objects(Bucket=bucket)["Contents"]
    actual = {obj["Key"]: literal_eval(obj["ETag"]) for obj in contents}

    assert expected_content == actual
