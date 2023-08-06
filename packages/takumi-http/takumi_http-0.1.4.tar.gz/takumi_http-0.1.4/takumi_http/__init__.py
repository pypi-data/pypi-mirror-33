# -*- coding: utf-8 -*-

"""
takumi-http
===========

Write http service as a thrift service.

This package implements a protocol transformer from http to thrift. Just write
the service as a normal Takumi thrift service, then serve the service as a http
service. The developers don't have to care about the details of the protocol
transformation, only add the config ``thrift_protocol_class`` to app.yaml and
your service can be served as a http service.

Config
------

.. code:: yaml

    thrift_protocol_class: takumi_http.HttpProtocol


Settings
--------

Session related settings:

* ``SECRET_KEY`` (required) secret key for encrypting cookies.
* ``PERMANENT_SESSION_LIFETIME`` timedelta of session lifetime, default 31 day.
* ``SESSION_COOKIE_DOMAIN`` cookie domain.
* ``SESSION_COOKIE_PATH`` cookie path, default '/'.

The attributes ``session_cookie_domain`` and ``session_cookie_path`` can be
setted to api context to override default settings.

Example
-------

.. code:: python

    from takumi import Takumi

    app = Takumi('PingService')
    app.use(save_session)

    @app.api_with_ctx
    @pass_request
    def say_hello(request, name):
        request.session['user_id'] = 90
        return 'Hello ' + name

Serve the App
-------------

Using `takumi-cli <https://github.com/elemepi/takumi-cli>`_ to the serve the
app.

.. code:: bash

    $ takumi serve


Invoke Api
----------

The http method is not very important. If the api has arguments use ``POST``,
if not use ``GET``.

Use a http client to invoke api:

.. code:: bash

    $ curl -XPOST http://localhost:1993/say_hello -d '{"name":"world"}'

API URL has this format:

..code:: text

    http://<domain>:<port>/<arbitrary>/<api_name>
"""

from .protocol import HttpProtocol
from .session import save_session
from .utils import HttpMeta, pass_request
from .__version__ import __version__


__all__ = ['HttpProtocol', 'HttpMeta', 'save_session', 'pass_request',
           '__version__']
