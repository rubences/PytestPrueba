from kaggle import api


def upload_to_kaggle(path, message):
    api.dataset_create_version(str(path), message, quiet=True)
