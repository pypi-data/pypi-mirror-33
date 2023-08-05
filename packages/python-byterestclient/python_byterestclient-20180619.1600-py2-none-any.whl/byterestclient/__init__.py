"""
Speak to an API
"""
import json
import os
import re
import requests
import socket

try:
    from urllib.parse import urlsplit, urlunsplit
except ImportError:
    from urlparse import urlsplit, urlunsplit

HTTPError = requests.HTTPError  # introspection
ConnectionError = requests.ConnectionError


class ByteRESTClient(object):

    def __init__(self, token=None, endpoint=None, identifier='byterestclient', headers=None):
        try:
            self.key = token or os.environ['REST_CLIENT_TOKEN']
            self.endpoint = endpoint or os.environ['REST_CLIENT_ENDPOINT']
        except KeyError as e:
            raise RuntimeError('Environment variable %s is not properly configured for ByteRESTClient' % e)

        self.headers = {
            'Authorization': 'Token %s' % self.key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': '%s:%s' % (socket.getfqdn(), identifier)
        }
        if headers:
            self.headers.update(headers)

    def request(self, method, path, data=None, *args, **kwargs):
        url = self.format_absolute_url(path)
        request_method = getattr(requests, method)

        response = request_method(
            url,
            data=json.dumps(data or {}),
            headers=self.headers,
            allow_redirects=False,
            *args,
            **kwargs
        )

        response.raise_for_status()

        if 300 <= response.status_code < 400:
            # support 0.12.1 by setting response seperately
            exception = HTTPError('%s Encountered Redirect' % response.status_code)
            exception.response = response
            raise exception

        if response.status_code == 204:
            return None

        if not response.content:
            return response

        # support 0.12.1 that has json as property, newer requests has json as method
        if callable(response.json):
            return response.json()
        else:
            return response.json

    def format_absolute_url(self, path):
        def join_and_clean_paths(path1, path2):
            return re.sub(r'/+', '/', path1 + '/' + path2)

        urlparts = list(urlsplit(self.endpoint))  # cast to list, because resulting tuple is immutable
        urlparts[2] = join_and_clean_paths(urlparts[2], path)
        return urlunsplit(urlparts)

    def get(self, path, *args, **kwargs):
        return self.request("get", path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        return self.request("post", path, *args, **kwargs)

    def put(self, path, *args, **kwargs):
        return self.request("put", path, *args, **kwargs)

    def delete(self, path, *args, **kwargs):
        return self.request("delete", path, *args, **kwargs)

    def patch(self, path, *args, **kwargs):
        return self.request("patch", path, *args, **kwargs)
