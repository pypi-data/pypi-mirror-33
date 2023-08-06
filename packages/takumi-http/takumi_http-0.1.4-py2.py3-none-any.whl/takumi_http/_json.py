# -*- coding: utf-8 -*-

"""
takumi_http._json
~~~~~~~~~~~~~~~~~

thrift to json, json to thrift converter.

        struct <=> {"field_name": field_value}
        map    <=> {"key": value}
        list   <=> [val, val]
        bool   <=> true/false
        int, double, string
"""

from thriftpy.thrift import TType, TDecodeException, TPayload
from ._compat import integer_types, string_types


class _InvalidType(Exception):
    pass


INTEGER = (TType.BYTE, TType.I16, TType.I32, TType.I64)
FLOAT = (TType.DOUBLE,)


def _is_type_right(val, ttype, struct_class=dict):
    types = None
    if ttype in INTEGER:
        types = integer_types
    elif ttype in FLOAT:
        types = (float,) + integer_types
    elif ttype == TType.STRING:
        types = string_types
    elif ttype == TType.BOOL:
        types = bool
    elif ttype in (TType.SET, TType.LIST):
        types = list, tuple, set
    elif ttype == TType.MAP:
        types = dict
    elif ttype == TType.STRUCT:
        types = struct_class
    return types is not None and isinstance(val, types)


# Two kinds of specs:
#   field:     (ttype, field_name, type_spec, requirement)
#   type_spec: (ttype, type_spec)
#
# Nested type_spec may missing.
def _parse_spec(spec, field=False):
    if field:
        if not isinstance(spec, (list, tuple)):
            ttype, type_spec = spec, None
        else:
            ttype, type_spec = spec
        return ttype, type_spec

    ttype, name = spec[:2]
    type_spec = None if len(spec) <= 3 else spec[2]
    return ttype, name, type_spec, spec[-1]


def _to_json(ttype, val, spec=None):
    if not _is_type_right(val, ttype, struct_class=TPayload):
        raise _InvalidType

    if ttype in INTEGER or ttype in FLOAT or ttype == TType.STRING:
        return val

    if ttype == TType.BOOL:
        return True if val else False

    if ttype == TType.STRUCT:
        return struct_to_json(val)

    if ttype in (TType.SET, TType.LIST):
        return _list_to_json(val, spec)

    if ttype == TType.MAP:
        return _map_to_json(val, spec)


def _map_to_json(val, spec):
    key_type, key_spec = _parse_spec(spec[0], True)
    value_type, value_spec = _parse_spec(spec[1], True)
    return {str(_to_json(key_type, k, key_spec)): _to_json(
        value_type, v, value_spec) for k, v in val.items()}


def _list_to_json(val, spec):
    elem_type, type_spec = _parse_spec(spec, True)
    return [_to_json(elem_type, i, type_spec) for i in val]


def struct_to_json(val):
    """Convert python class instance to json dict

    :param val: python class instance
    """
    outobj = {}
    for fid, field_spec in val.thrift_spec.items():
        ttype, field_name, field_type_spec, req = _parse_spec(field_spec)

        v = getattr(val, field_name)
        if v is None and req:
            raise TDecodeException(val.__class__.__name__, fid,
                                   field_name, None, ttype,
                                   field_type_spec)
        if v is None:
            continue
        try:
            outobj[field_name] = _to_json(ttype, v, field_type_spec)
        except _InvalidType:
            raise TDecodeException(val.__class__.__name__, fid,
                                   field_name, v, ttype, field_type_spec)
    return outobj


def _from_json(ttype, val, spec=None):
    if not _is_type_right(val, ttype):
        raise _InvalidType

    if ttype in INTEGER:
        return int(val)

    if ttype in FLOAT:
        return float(val)

    if ttype in (TType.STRING, TType.BOOL):
        return val

    if ttype == TType.STRUCT:
        return struct_from_json(val, spec())

    if ttype in (TType.SET, TType.LIST):
        return _list_from_json(val, spec)

    if ttype == TType.MAP:
        return _map_from_json(val, spec)


def _map_from_json(val, spec):
    key_type, key_spec = _parse_spec(spec[0], True)
    value_type, value_spec = _parse_spec(spec[1], True)
    return {
        _from_json(key_type, k, key_spec): _from_json(value_type, v,
                                                      value_spec)
        for k, v in val.items()
    }


def _list_from_json(val, spec):
    elem_type, type_spec = _parse_spec(spec, True)
    return [_from_json(elem_type, i, type_spec) for i in val]


def struct_from_json(val, obj):
    """Convert json dict to struct

    :param val: json value
    :param obj: python class instance
    """
    for fid, field_spec in obj.thrift_spec.items():
        ttype, field_name, field_type_spec, req = _parse_spec(field_spec)

        if req and field_name not in val:
            raise TDecodeException(obj.__class__.__name__, fid,
                                   field_name, None, ttype,
                                   field_type_spec)

        raw_val = val.get(field_name)
        if raw_val is None:
            continue

        try:
            v = _from_json(ttype, raw_val, field_type_spec)
        except (TypeError, ValueError, AttributeError, _InvalidType):
            raise TDecodeException(obj.__class__.__name__, fid, field_name,
                                   raw_val, ttype, field_type_spec)
        setattr(obj, field_name, v)
    return obj
