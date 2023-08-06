# -*- coding: utf-8 -*-

"""
takumi_http.http_handler
~~~~~~~~~~~~~~~~~~~~~~~~

Implemented a http handler for parsing http requests.
"""

import logging
import json
import os.path

try:
    from http.server import BaseHTTPRequestHandler
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs

from takumi import CloseConnectionError
from .utils import Headers, Qs
from .__version__ import __version__

CONTENT_TYPE = 'application/json;charset=utf-8'
NON_HEADERS = ('status_code', 'message')

logger = logging.getLogger('takumi.http')


class HttpErrorRequest(object):
    """Represents http errors

    :param code: http code
    :param message: http message
    :param explain: explanation of this error
    """
    def __init__(self, code, message, explain):
        self.code = code
        self.message = message
        self.explain = explain

    @property
    def meta(self):
        return {
            'status_code': str(self.code),
            'message': self.message,
            'content-length': str(len(json.dumps(self.body))),
            'connection': 'close',
            'content-type': CONTENT_TYPE
        }

    @property
    def body(self):
        return {'message': self.explain}


class HttpRequest(object):
    """Represents http requests
    """
    def __init__(self):
        self.method = None
        self.http_version = None
        self.headers = {}
        self.qs = {}
        self.body = None
        self.api = None

    @property
    def meta(self):
        m = {
            'method': self.method,
            'http_version': self.http_version,
        }
        # Store headers
        headers = Headers(m)
        headers.from_dict(self.headers)

        # Store query string
        Qs(m).from_dict({k: v[0] for k, v in self.qs.items()})

        try:
            user_agent = headers.get('user-agent', '-/-').split(' ')[0]
            name, version = user_agent.split('/')
        except Exception:
            name, version = '-', '-'
        m.update({'client_name': name, 'client_version': version})
        return m


class HttpHandler(BaseHTTPRequestHandler):
    """Http handler for parsing http requests and sending responses
    """
    protocol_version = 'HTTP/1.1'
    server_version = 'takumi_http/' + __version__

    def __init__(self, *args, **kwargs):
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
        self._error = None
        self._request = None

    def do_GET(self):
        pass

    def do_POST(self):
        length = self.headers.get('content-length')
        if not length:
            self.send_error(204)
            return
        body = self.rfile.read(int(length))
        try:
            body = body.decode('utf-8')
            self._request.body = json.loads(body)
        except (UnicodeDecodeError, ValueError):
            self.send_error(400)

    do_PUT = do_POST
    do_PATCH = do_POST

    def send_error(self, code, message=None, explain=None):
        try:
            shortmsg, longmsg = self.responses[code]
        except KeyError:
            shortmsg, longmsg = '???', '???'
        if message is None:
            message = shortmsg
        if explain is None:
            explain = longmsg
        self._error = HttpErrorRequest(code, message, explain)

    def handle(self):
        pass

    def finish(self):
        pass

    def address_string(self):
        return '-'

    def log_message(self, *args, **kwargs):
        pass

    def log_request(self, *args, **kwargs):
        pass

    def handle_one_request(self):
        self.raw_requestline = self.rfile.readline(65537)
        if not self.raw_requestline:
            raise CloseConnectionError

        if len(self.raw_requestline) > 65536:
            self.requestline = ''
            self.request_version = ''
            self.command = ''
            self.send_error(414)
            return

        if not self.parse_request():
            return

        mname = 'do_' + self.command
        if not hasattr(self, mname):
            self.send_error(501, "Unsupported method (%r)" % self.command)
            return
        getattr(self, mname)()

    def get_request(self):
        """Get a HttpRequest or HttpErrorRequest instance
        """
        self.close_connection = 1
        ret = None
        try:
            self._request = HttpRequest()
            self.handle_one_request()
            if self._error is not None:
                ret = self._error
            else:
                self._request.method = self.command
                self._request.http_version = self.request_version
                self._request.headers = self.headers

                parts = urlparse(self.path)
                self._request.api = os.path.basename(parts.path)
                self._request.qs = parse_qs(parts.query)
                ret = self._request
        finally:
            self._request = None
            self._error = None
        return ret

    def write_response(self, meta, data):
        """Write response to client

        :param meta: http metadata
        :param data: http payload
        """
        code = int(meta.get('status_code', '200'))
        message = meta.get('message') or self.responses[code][0]
        self.send_response(code, message)

        data = json.dumps(data).encode('utf-8') if data else b''
        meta['content-length'] = str(len(data))
        meta['content-type'] = CONTENT_TYPE

        for header in set(meta.keys()).difference(NON_HEADERS):
            self.send_header(header, meta[header])
        self.end_headers()
        self.wfile.write(data)
        self.wfile.flush()
