# -*- coding: utf-8 -*-

"""
takumi_http.protocol
~~~~~~~~~~~~~~~~~~~~

Http <=> Thrift

http:

GET /ping HTTP/1.1
Host: localhost
Connection: keep-alive
Content-Length: 13602
Pragma: no-cache
Cache-Control: no-cache
Origin: https://github.com
User-Agent: Mozilla/5.0
content-type: application/json

{
  "hello": 124
}


=>

meta:
{
  "method": "GET",
  "http_version": "HTTP/1.1",
  "user-agent": "Mozilla/5.0",
  ...
}
"""
import logging
import contextlib
from thriftpy.thrift import TMessageType, TApplicationException, \
    TDecodeException
from takumi import CloseConnectionError
from takumi_thrift import Metadata

from .http_handler import HttpHandler, HttpRequest
from ._json import struct_from_json, struct_to_json

try:
    import httplib as http_code
except ImportError:
    import http.client as http_code


logger = logging.getLogger('takumi.http')


class HTTPError(object):
    """Represents a http error
    """
    def __init__(self, code, message=''):
        self.code = code
        self.message = message

    def to_dict(self):
        return {'code': self.code, 'message': self.message}


class THttpProtocol(object):
    """Http protocol adapted for thrift

    :param trans: client socket
    """
    def __init__(self, trans):
        self.trans = trans
        self.http = HttpHandler(trans.sock, None, None)
        self._is_meta_read = False
        self._write_exception = False
        self._written_meta = {}
        self._req = None

    def skip(self, ttype):
        pass

    def read_message_begin(self):
        if self._req is None:
            self._req = self.http.get_request()
            if not isinstance(self._req, HttpRequest):
                self.http.write_response(self._req.meta, self._req.body)
                raise CloseConnectionError

        api = self._req.api if self._is_meta_read else Metadata.META_API_NAME
        return api, TMessageType.CALL, 0

    def read_message_end(self):
        if not self._is_meta_read:
            self._is_meta_read = True
        else:
            self._is_meta_read = False
            self._req = None

    def write_message_begin(self, name, ttype, seqid):
        if ttype == TMessageType.EXCEPTION:
            self._write_exception = True

    def write_message_end(self):
        pass

    def read_struct(self, obj):
        assert self._req is not None

        data = self._req.body or {} if \
            self._is_meta_read else {'data': self._req.meta}

        # Close connection when exception happened
        with self._decode_exception(http_code.BAD_REQUEST):
            struct_from_json(data, obj)

    @contextlib.contextmanager
    def _decode_exception(self, code):
        try:
            yield
        except TDecodeException as e:
            logger.warning(e, exc_info=True)
            self._write_app_error(
                TApplicationException.INTERNAL_ERROR, str(e), code)
            raise CloseConnectionError

    def _write_response(self, data):
        try:
            self.http.write_response(self._written_meta, data)
            if self.http.close_connection:
                raise CloseConnectionError
        finally:
            self._written_meta = {}

    def _write_error(self, error_type, data,
                     code=http_code.INTERNAL_SERVER_ERROR):
        self._written_meta.setdefault('status_code', code)
        self._write_response({'type': error_type, 'data': data})

    def _write_app_error(self, tp, msg, code=http_code.INTERNAL_SERVER_ERROR):
        e = TApplicationException(tp, message=msg)
        return self._write_error(e.__class__.__name__, self._to_json(e),
                                 code=code)

    def _write_result(self, obj):
        if hasattr(obj, 'success'):
            res = obj.success
            if isinstance(res, HTTPError):
                return self._write_error('HTTPError', res.to_dict(), res.code)
            is_void = 0 not in obj.thrift_spec or \
                obj.thrift_spec[0][1] != 'success'
            if is_void or res is not None:
                # Check void result
                data = '' if is_void else self._to_json(obj)['success']
                return self._write_response(data)
        # Throws
        for item in obj.thrift_spec.values():
            attr = getattr(obj, item[1], None)
            if not attr:
                continue
            return self._write_error(attr.__class__.__name__,
                                     self._to_json(obj)[item[1]],
                                     http_code.BAD_REQUEST)
        # Missing result
        return self._write_app_error(
            TApplicationException.MISSING_RESULT, 'Missing result')

    def _to_json(self, obj):
        # Close connection when exception happened
        with self._decode_exception(http_code.INTERNAL_SERVER_ERROR):
            return struct_to_json(obj)

    def write_struct(self, obj):
        if self._write_exception:
            self._write_exception = False
            if isinstance(obj, TApplicationException) and not obj.message:
                obj.message = str(obj)
            return self._write_error(
                obj.__class__.__name__, self._to_json(obj))

        if isinstance(obj, Metadata):
            # write meta
            self._written_meta = obj.data
        else:
            self._write_result(obj)


class HttpProtocol(object):
    """Http protocol getter for takumi service runner

    :param sock: client socket
    """
    def __init__(self, sock):
        self.sock = sock

    def get_proto(self):
        """Create a THttpProtocol instance
        """
        return THttpProtocol(self.sock)

    def close(self):
        self.sock.close()
