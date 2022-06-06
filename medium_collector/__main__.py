import logging
from datetime import datetime
from pathlib import Path

import click

from medium_collector.download import download
from medium_collector.kaggle_datasets import upload_to_kaggle
from medium_collector.s3 import upload_files


@click.group()
@click.option("--debug", is_flag=True, default=False)
def cli(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@cli.command()
@click.option("--dry-run", is_flag=True, default=False)
def from_mail(dry_run):
    message = datetime.now().strftime("%A, %B %e, %Y")
    data_path = Path("data")
    if not data_path.exists():
        data_path.mkdir()

    download.download_from_mail(data_path, dry_run)
    if not dry_run:
        upload_files(data_path)
        upload_to_kaggle(data_path, message)


if __name__ == "__main__":
    cli()
