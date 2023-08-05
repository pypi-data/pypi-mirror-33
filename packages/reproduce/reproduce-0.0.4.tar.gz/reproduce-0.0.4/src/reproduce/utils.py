"""utility functions that are useful for Reproduce."""
import re
import logging
import shutil

import urllib.request
import google.cloud.client
import google.cloud.storage

ALL_DIR_LIST = [
    ('DATA_DIR', 'data'),
    ('CACHE_DIR', 'cache'),
    ]

LOGGER = logging.getLogger(__name__)
def url_fetcher(url):
    """Closure for retrieving a url."""
    def _url_fetcher(path):
        """Download `url` to `path`."""
        LOGGER.info(f'fetching {path}')
        response = urllib.request.urlopen(url)
        with open(path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        response.close()
    return _url_fetcher


def google_bucket_fetcher(url, json_key_path):
    """Closure for a function to download a Google Blob to a given path.

    Parameters:
        url (string): url to blob, matches the form
            '^https://storage.cloud.google.com/([^/]*)/(.*)$'
        json_key_path (string): path to Google Cloud private key generated
            by https://cloud.google.com/iam/docs/creating-managing-service-account-keys

    Returns:
        a function with a single `path` argument to the target file. Invoking
            this function will download the Blob to `path`.

    """
    def _google_bucket_fetcher(path):
        """Fetch blob `url` to `path`."""
        url_matcher = re.match(
            r'^https://[^/]*\.com/([^/]*)/(.*)$', url)
        LOGGER.debug(url)
        client = google.cloud.storage.client.Client.from_service_account_json(
            json_key_path)
        bucket_id = url_matcher.group(1)
        LOGGER.debug(f'parsing bucket {bucket_id} from {url}')
        bucket = client.get_bucket(bucket_id)
        blob_id = url_matcher.group(2)
        LOGGER.debug(f'loading blob {blob_id} from {url}')
        blob = google.cloud.storage.Blob(blob_id, bucket)
        LOGGER.info(f'downloading blob {path} from {url}')
        blob.download_to_filename(path)
    return _google_bucket_fetcher
