from dli.client.dli_client import DliClient

import urllib3
import requests

urllib3.disable_warnings()


def start_session(api_key, root_url="https://catalogue.datalake.ihsmarkit.com/__api"):
    """
    Entry point for the Data Lake SDK, returns a client instance that
    can be used to consume or register datasets.

    :param str api_key: Your API key, can be retrieved from your dashboard in
                        the Catalogue UI.
    :param str root_url: The environment you want to point to, by default it
                        points to Production.

    """
    client = DliClient(api_key, root_url)
    return client
