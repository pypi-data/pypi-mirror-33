import requests

from dli.client.context import Context
from dli.client.dataset_functions import DatasetFunctions
from dli.client.package_functions import PackageFunctions


class AuthenticationFailure(Exception):
    """
    An exception wrapping an authentication failure response. If the response
    had a payload, that payload is reported as the exception message, otherwise
    a generic error message is returned.
    """
    GENERIC_ERROR_MESSAGE = (
        'Please verify that your API key is correct and has not expired'
    )

    def __init__(self, response):
        self.response = response

    def __str__(self):
        if self.response.text:
            return self.response.text
        return AuthenticationFailure.GENERIC_ERROR_MESSAGE


class DliClient(PackageFunctions, DatasetFunctions):
    """
    Definition of a client. This client mixes in utility functions for
    manipulating packages and datasets.
    """
    def __init__(self, api_key, api_root):
        self.api_key = api_key
        self.api_root = api_root
        self._ctx = self._init_ctx()

    def _init_ctx(self):
        auth_key = _get_auth_key(
            self.api_key,
            self.api_root
        )

        return Context(
            self.api_key,
            self.api_root,
            auth_key
        )

    @property
    def ctx(self):
        # if the session expired, then reauth
        # and create a new context
        if self._ctx.session_expired:
            self._ctx = self._init_ctx()

        return self._ctx

    def get_root_siren(self):
        return self.ctx.get_root_siren()


def _get_auth_key(api_key, api_root):
    key = api_key
    auth_header = "Bearer {}".format(key)
    start_session_url = "{}/start-session".format(api_root)  # TODO: Siren
    r = requests.post(start_session_url, headers={"Authorization": auth_header})
    if r.status_code != 200:
        raise AuthenticationFailure(r)
    return r.text
