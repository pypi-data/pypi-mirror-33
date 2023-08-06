# -*- coding: utf-8 -*-

"""
takumi_http.testing
~~~~~~~~~~~~~~~~~~~

This module is for testing. Nerver use the module in production environments.
"""

import json
from collections import Mapping
from takumi.testing import ClientBase, Socket, MemoryTransport

try:
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from .protocol import HttpProtocol


class _Headers(Mapping):
    def __init__(self, headers):
        self.headers = {k.lower(): v for k, v in headers}

    def __getitem__(self, key):
        return self.headers[key.lower()]

    def __iter__(self):
        return iter(self.headers)

    def __len__(self):
        return len(self.headers)


class _HttpResponse(object):
    def __init__(self, value, status, headers):
        self.value = json.loads(value)
        self.status = status
        self.headers = _Headers(headers)

    def __repr__(self):
        return repr(self.value)


class _HttpConnection(HTTPConnection):
    def connect(self):
        self.sock = Socket()


class HttpClient(ClientBase):
    def __init__(self, app):
        super(HttpClient, self).__init__(app)
        self._http = self._create_http()

    @staticmethod
    def _create_http():
        return _HttpConnection('localhost')

    def _call(self, api, qs=None, headers=None, **kwargs):
        http = self._http
        try:
            method, body = ('POST', json.dumps(kwargs)) \
                if kwargs else ('GET', None)

            query = '?{}'.format(urlencode(qs)) if qs else ''
            http.request(method, '/{}{}'.format(api, query), body=body,
                         headers=headers or {})
            http.sock.prepare_read()
            prot = HttpProtocol(MemoryTransport(http.sock)).get_proto()
            self._processor.process(prot, prot)
            http.sock.prepare_read()
            res = http.getresponse()
            return _HttpResponse(res.read().decode('utf-8'), res.status,
                                 res.getheaders())
        except Exception:
            self._http = self._create_http()
            raise
        finally:
            http.sock = None
