from datetime import datetime
from sanic.response import *

from longitude.utils import dict_recursive_mapper, datetime_to_utc

_sanic_json = json
_sanic_json_dumps = json_dumps


def json_dumps(body, **kwargs):

    body = dict_recursive_mapper(
        body,
        lambda x:
            x if not isinstance(x, datetime)
            else str(datetime_to_utc(x))
        ,
        copy=False
    )

    return _sanic_json_dumps(body, **kwargs)


def json(*args, **kwargs):

    return _sanic_json(*args, dumps=json_dumps, **kwargs)
