"""HTTP(S) storage broker."""

import logging
import os
import json
import shutil
import requests

from dtoolcore.utils import (
    get_config_value,
    mkdir_parents,
    generous_parse_uri,
)

logger = logging.getLogger(__name__)

HTTP_MANIFEST_KEY = 'http_manifest.json'


class HTTPError(RuntimeError):
    pass


class HTTPStorageBroker(object):
    """
    Storage broker to interact with datasets over HTTP in a read only fashion.
    """

    key = "http"

    def __init__(self, uri, admin_metadata, config_path=None):

        scheme, netloc, path, _, _, _ = generous_parse_uri(uri)

        self._uri = self._get_base_uri(uri)

        self.scheme = scheme
        self.netloc = netloc
        self.uuid = path[1:]

        http_manifest_url = self._uri + '/' + HTTP_MANIFEST_KEY

        self.http_manifest = self._get_json_from_url(
            http_manifest_url
        )

        self._cache_abspath = get_config_value(
            "DTOOL_HTTP_CACHE_DIRECTORY",
            config_path=config_path,
            default=os.path.expanduser("~/.cache/dtool/http")
        )

    # Helper functions

    def _get_base_uri(self, url):
        r = requests.get(url)
        if r.status_code != 301:
            logger.info("Dataset moved, redirecting to: {}".format(
                r.url))
        return r.url

    def _get_request(self, url, stream=False):
        r = requests.get(url, stream=stream)
        logger.info("Response status code: {}".format(r.status_code))

        if r.status_code != 200:
            raise(HTTPError(r.status_code))

        return r

    def _get_text_from_url(self, url):

        r = self._get_request(url)

        return r.text

    def _get_json_from_url(self, url):
        text = self._get_text_from_url(url)

        return json.loads(text)

    # Functions to allow dataset retrieval
    def get_admin_metadata(self):
        """Return administrative metadata as a dictionary."""
        return self.http_manifest["admin_metadata"]

    def get_manifest(self):
        """Return the manifest as a dictionary."""
        url = self.http_manifest["manifest_url"]
        return self._get_json_from_url(url)

    def get_readme_content(self):
        """Return content of the README file as a string."""
        url = self.http_manifest["readme_url"]
        return self._get_text_from_url(url)

    def has_admin_metadata(self):
        """Return True if the administrative metadata exists.

        This is the definition of being a "dataset".
        """
        return "admin_metadata" in self.http_manifest

    def get_item_abspath(self, identifier):
        """Return absolute path at which item content can be accessed.

        :param identifier: item identifier
        :returns: absolute path from which the item content can be accessed
        """

        dataset_cache_abspath = os.path.join(
            self._cache_abspath,
            self.uuid
        )
        mkdir_parents(dataset_cache_abspath)

        manifest = self.get_manifest()
        relpath = manifest['items'][identifier]['relpath']
        _, ext = os.path.splitext(relpath)

        local_item_abspath = os.path.join(
            dataset_cache_abspath,
            identifier + ext
        )

        if not os.path.isfile(local_item_abspath):

            url = self.http_manifest["item_urls"][identifier]

            r = self._get_request(url, stream=True)
            tmp_local_item_abspath = local_item_abspath + ".tmp"
            with open(tmp_local_item_abspath, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            os.rename(tmp_local_item_abspath, local_item_abspath)

        return local_item_abspath

    def get_overlay(self, overlay_name):
        """Return overlay as a dictionary.

        :param overlay_name: name of the overlay
        :returns: overlay as a dictionary
        """
        url = self.http_manifest["overlays"][overlay_name]
        return self._get_json_from_url(url)

    def list_overlay_names(self):
        """Return list of overlay names."""
        return self.http_manifest["overlays"].keys()

    def list_dataset_uris(self, base_uri, CONFIG_PATH):
        """Return list of datasets in base uri."""
        return []

    def http_enable(self):
        """Return the URI from which the dataset can be accessed via HTTP."""
        return self._uri


class HTTPSStorageBroker(HTTPStorageBroker):
    """
    Storage broker to interact with datasets over HTTPS in a read only fashion.
    """

    key = "https"
