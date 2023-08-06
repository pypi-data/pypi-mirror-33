# -*- coding: utf-8 -*-

from takumi import define_hook, StopHook
from .utils import HttpMeta
from .protocol import HTTPError


@define_hook(event='before_api_call')
def methods(ctx):
    """Check allowed HTTP methods

    Default: ['POST']
    """
    meta = HttpMeta(ctx.meta)
    allowed = ctx.conf.get('methods', ['POST'])
    if meta.method not in allowed:
        raise StopHook(
            value=HTTPError(
                code=405,
                message='Method {!r} not allowed'.format(meta.method)),
            meta={'status_code': 405})
