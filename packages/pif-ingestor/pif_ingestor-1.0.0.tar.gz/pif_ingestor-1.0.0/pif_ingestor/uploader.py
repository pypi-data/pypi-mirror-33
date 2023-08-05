from os import environ
import logging
from citrination_client import CitrinationClient


def upload(paths, dataset):
    """Recursively upload paths to a dataset"""
    client = _get_client()
    if isinstance(paths, list):
        for p in paths:
            _upload_single(p, dataset, client)
    else:
        _upload_single(paths, dataset, client)
    return


def _get_client():
    """Get a client for the user defined by the environemtn"""
    if 'CITRINATION_SITE' not in environ:
        site = "https://citrination.com"
    else:
        site = environ['CITRINATION_SITE']
    client = CitrinationClient(environ['CITRINATION_API_KEY'], site)
    return client


def _upload_single(path, dataset, client):
    client.upload_file(path, dataset)
    logging.info("Uploaded {}".format(path))
    return
