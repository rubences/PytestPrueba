import hashlib
import logging
from ast import literal_eval
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from decouple import config

logger = logging.getLogger(__name__)

FILES_TO_UPLOAD = ["articles_mails.csv", "mails.csv"]


def upload_files(data_path):
    bucket = config("BUCKET")

    file_hashes = get_file_hashes(data_path)

    client = boto3.client(
        "s3",
        aws_access_key_id=config("ACCESS_KEY"),
        aws_secret_access_key=config("SECRET_KEY"),
        region_name="eu-west-2",
    )

    for file, hash in file_hashes.items():
        try:
            head = client.head_object(Bucket=bucket, Key=file.name)
            if "ETag" in head and literal_eval(head["ETag"]) == hash:
                logger.info("skipping %s" % str(file))
                continue
        except ClientError:
            pass
        client.upload_file(str(file), bucket, file.name)
        logger.info("uploaded %s" % str(file))


def get_file_hashes(data_path):
    file_hashes = {}
    for file in FILES_TO_UPLOAD:
        file_path = Path(data_path, file)
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        file_hashes[file_path] = hash_md5.hexdigest()
    return file_hashes
