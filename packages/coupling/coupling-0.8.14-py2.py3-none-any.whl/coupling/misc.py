# coding: utf-8

import inspect
import ctypes

import six
from abc import ABCMeta, abstractmethod
from .deprecated import deprecated

import logging
logger = logging.getLogger(__name__)


@six.add_metaclass(ABCMeta)
class ClosingContextManager(object):
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        if exc_info != (None, None, None):
            logger.exception("")
        self.close()

    @abstractmethod
    def close(self):
        pass


_STRING_BOOLEAN_MAPPING = {
    '1': True, 'yes': True, 'true': True, 'on': True,
    '0': False, 'no': False, 'false': False, 'off': False
}


@deprecated("use get_boolean instead")
def get_boolean_from_string(s):
    if s.lower() not in _STRING_BOOLEAN_MAPPING:
        raise ValueError('Not a boolean: %s' % s)
    return _STRING_BOOLEAN_MAPPING[s.lower()]


def get_boolean(x):
    if isinstance(x, str):
        if x.lower() not in _STRING_BOOLEAN_MAPPING:
            raise ValueError('Not a boolean: %s' % x)
        return _STRING_BOOLEAN_MAPPING[x.lower()]
    else:
        return bool(x)


def is_inherited_from_base_classes(cls, method_name, ignore_abstract=False):
    inherited = False
    for mro in cls.__mro__[1:]:
        if ignore_abstract and inspect.isabstract(mro):
            continue

        if hasattr(mro, method_name):
            inherited = True
            break
    return inherited


def ctypes_structure_to_dict(obj, recursive=True):
    d = {}
    for field in getattr(obj, "_fields_"):
        name = field[0]
        value = getattr(obj, name)
        if isinstance(value, ctypes.Structure) and recursive:
            value = ctypes_structure_to_dict(value)
        d[name] = value
    return d


def evaluate(s, global_context=None, local_context=None):
    import re
    import pydoc
    context = local_context or locals()
    try:
        return eval(s, global_context or globals(), context)
    except NameError as err:
        message = str(err)
        logger.debug(message)
        match = re.search(r"name '(\w+)' is not defined", message)
        if match:
            name = match.group(1)
            value = pydoc.locate(name)
            context[name] = value
            logger.debug("add (%s, %s) into context and re-evaluate.", name, value)
            return evaluate(s, global_context, context)


def get_class_that_defined_method(method):
    if inspect.ismethod(method):
        for cls in inspect.getmro(method.__self__.__class__):
            if cls.__dict__.get(method.__name__) is method:
                return cls
        method = method.__func__  # fallback to __qualname__ parsing
    if inspect.isfunction(method):
        cls = getattr(inspect.getmodule(method),
                      method.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
        if isinstance(cls, type):
            return cls
    return getattr(method, '__objclass__', None)  # handle special descriptor objects
