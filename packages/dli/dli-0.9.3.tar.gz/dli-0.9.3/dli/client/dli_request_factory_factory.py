import requests

from urllib.parse import urlparse, urljoin
from dli import __version__
import json as json_lib
import time
from dli.client.exceptions import InvalidPayloadException, UnAuthorisedAccessException, InsufficientPrivilegeException, DatalakeException

# Python 2.7 / 3.x differences
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


def make_hook(root, get_header):
    def _make_request(loc):
        parsed_root = urlparse(root)
        api_root = "{}://{}".format(parsed_root.scheme, parsed_root.netloc)
        loc = urljoin(str(api_root), str(loc))  # python 2/3 nonsense
        res = requests.get(loc, headers=get_header())

        return res

    def _make_empty_response(r):
        import copy
        response = copy.deepcopy(r)
        response._content = b'{"class": ["none"]}'
        return response

    def _extract_error_response_message(r):
        try:
            return r.json()['errorText']
        except (JSONDecodeError, KeyError):
            return r.text

    def _response_hook(r, *args, **kwargs):

        if r.status_code in [201, 202, 404]:  # for now. or (300 <= r.status_code <= 399):
            loc = None

            if 'Content-Location' in r.headers:
                loc = r.headers['Content-Location']
            elif 'Location' in r.headers:
                loc = r.headers['Location']
            else:
                return _make_empty_response(r)

            if loc == root:
                return _make_empty_response(r)

            remaining = 3
            delay = 1

            while remaining > 0:
                res = _make_request(loc)
                if res.status_code == 200:
                    return res
                remaining = remaining - 1
                time.sleep(delay)

            return res
        elif r.status_code == 204:
            return _make_empty_response(r)
        elif r.status_code in [400, 422]:
            raise InvalidPayloadException(_extract_error_response_message(r))
        elif r.status_code == 401:
            raise UnAuthorisedAccessException(_extract_error_response_message(r))
        elif r.status_code == 403:
            raise InsufficientPrivilegeException(_extract_error_response_message(r))
        elif r.status_code > 400:
            raise DatalakeException(_extract_error_response_message(r))
    return _response_hook


class DliRequestFactoryFactory(object):
    def __init__(self, root, auth_header=lambda: {}):
        self.root = root
        self.auth_header = auth_header

    def request_factory(self, method=None, url=None, headers=None, files=None, data=None,
                        params=None, auth=None, cookies=None, hooks=None, json=None):

        # relative uri? make it absolute.
        if not urlparse(url).netloc:
            url = urljoin(str(self.root), str(url))     # python 2/3 nonsense

        # uri template substitution.
        pars = params if method == "GET" else data

        to_remove = []

        if pars:
            if '__json' in pars:
                js = json_lib.loads(pars['__json'])
                pars.update(js)
                del pars['__json']

            for key in pars:
                if key in url:
                    url = url.replace("__{}__".format(key), pars[key])
                    to_remove.append(key)

            for k in to_remove:
                del pars[k]

        if pars and method == "GET":
            params = pars
        else:
            json = pars
            data = None

        if not headers:
            headers = {}
        headers['Content-Type'] = "application/vnd.siren+json"
        headers["X-Data-Lake-SDK-Version"] = str(__version__)
        headers.update(self.auth_header())

        if not hooks:
            hooks = {}
        if 'response' not in hooks:
            hooks['response'] = []
        hooks['response'] = make_hook(self.root, self.auth_header)

        return requests.Request(method=method, url=url, headers=headers, files=files, data=data, params=params,
                                auth=auth, cookies=cookies, hooks=hooks, json=json)
