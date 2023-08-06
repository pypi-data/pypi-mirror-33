# -*- coding: utf-8 -*-

"""
takumi_http.session
~~~~~~~~~~~~~~~~~~~

Implements cookie based HTTP session.
"""

import datetime
import hashlib

try:
    from http import cookies
except ImportError:
    import Cookie as cookies

from collections import MutableMapping
from itsdangerous import URLSafeTimedSerializer, BadSignature
from takumi import define_hook
from takumi_config import config


def _get_session_lifetime():
    return config.settings.get('PERMANENT_SESSION_LIFETIME',
                               datetime.timedelta(days=31))


def _get_cookie_serializer():
    secret_key = config.settings.get('SECRET_KEY')
    if not secret_key:
        return

    return URLSafeTimedSerializer(
        'secret', 'takumi-http-cookie-session',
        signer_kwargs={
            'key_derivation': 'hmac',
            'digest_method': hashlib.sha256,
        })


class Session(MutableMapping):
    """Cookie based session.

    :param data: A dict store session values
    :param ctx: app context
    """
    def __init__(self, data, ctx):
        self.data = data
        self.ctx = ctx

    @classmethod
    def from_cookie(cls, ctx, cookie):
        """Create session from the cookie http header.

        :param ctx: app context
        :param cookie: the cookie http header
        """
        session = cookies.SimpleCookie(cookie).get('session', '')
        serializer = _get_cookie_serializer()
        data = {}
        if not serializer:
            data = None
        elif session:
            try:
                data = serializer.loads(
                    session.value,
                    max_age=_get_session_lifetime().total_seconds())
            except BadSignature:
                pass
        ctx._takumi_http_session = data
        ctx._takumi_http_session_updated = False
        return cls(data, ctx)

    def _assert_data(self):
        if self.data is None:
            raise RuntimeError('The session is unavailable because no secret '
                               'key was set.  Set the secret key using config '
                               'SECRET_KEY.')

    def __getitem__(self, key):
        self._assert_data()
        return self.data[key]

    def __setitem__(self, key, value):
        self._assert_data()
        self.ctx._takumi_http_session_updated = True
        self.data[key] = value

    def __delitem__(self, key):
        self._assert_data()
        self.ctx._takumi_http_session_updated = True
        self.data.pop(key, None)

    def __iter__(self):
        self._assert_data()
        return iter(self.data)

    def __len__(self):
        self._assert_data()
        return len(self.data)


@define_hook(event='api_called')
def save_session(ctx):
    if not ctx.get('_takumi_http_session_updated'):
        return

    domain = ctx.get('session_cookie_domain',
                     config.settings.get('SESSION_COOKIE_DOMAIN', ''))
    path = ctx.get('session_cookie_path',
                   config.settings.get('SESSION_COOKIE_PATH', '/'))
    lifetime = _get_session_lifetime()

    expires = ''
    if ctx.get('session_permanent'):
        expires = datetime.datetime.utcnow() + lifetime

    session = ctx.get('_takumi_http_session', {})
    cookie = cookies.SimpleCookie()
    cookie['session'] = ''
    cookie['session'].update({'httponly': True, 'path': path,
                              'domain': domain, 'expires': expires})
    if not session:
        cookie['session'].update({'expires': 0, 'max-age': 0})
    else:
        cookie['session'] = _get_cookie_serializer().dumps(session)
    ctx.response_meta['Set-Cookie'] = cookie.output(header='').strip()
