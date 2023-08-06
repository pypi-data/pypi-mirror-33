# coding: utf-8

import typing
from jsonpath_ng.ext import parse


_UNSET = object()


class NotFoundError(Exception):
    pass


def search(path: str, data: dict, default=_UNSET,
           smart_unique: bool=True) -> typing.Union[int, float, bool, str, list, dict, None]:
    """
    when not found:
    if raise_not_found is true, raise NotFoundError, else return default value.
    """
    expr = parse(path)
    resp = expr.find(data)

    if not resp:
        if default is _UNSET:
            raise NotFoundError("Can't find by path: {}".format(path))
        else:
            return default

    if len(resp) == 1 and smart_unique:
        return resp[0].value
    else:
        return [match.value for match in resp]


search.NotFoundError = NotFoundError
