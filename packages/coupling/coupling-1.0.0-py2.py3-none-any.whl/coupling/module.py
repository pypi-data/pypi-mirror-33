# coding: utf-8

import re
import types
import typing
import inspect
import pkgutil
import importlib

import logging
logger = logging.getLogger(__name__)


def reload(module: types.ModuleType, pattern: str, recursive: bool=True) -> None:
    logger.debug("reload %s", module)
    importlib.reload(module)

    if recursive:
        imp_loader = pkgutil.get_loader(module)
        if imp_loader.is_package(module.__name__):
            for module_loader, sub_module_name, is_pkg in pkgutil.iter_modules(path=module.__path__):
                if is_pkg or (not is_pkg and re.match(pattern, sub_module_name)):
                    sub_module = importlib.import_module(module.__name__ + "." + sub_module_name)
                    reload(sub_module, pattern, recursive)
        else:
            logger.debug("reload %s", module)
            importlib.reload(module)


def is_package(module: types.ModuleType) -> bool:
    if inspect.ismodule(module):
        try:
            imp_loader = pkgutil.get_loader(module)
            return imp_loader.is_package(module.__name__)
        except ImportError:
            return False
    return False


def walk_module(module: types.ModuleType) -> typing.Iterator:
    for attr_name in dir(module):
        obj = getattr(module, attr_name)
        yield obj

    if is_package(module):
        for module_loader, sub_module_name, is_pkg in pkgutil.iter_modules(path=module.__path__):
            try:
                sub_module = importlib.import_module(module.__name__ + "." + sub_module_name)
                yield sub_module
            except ImportError:
                pass
