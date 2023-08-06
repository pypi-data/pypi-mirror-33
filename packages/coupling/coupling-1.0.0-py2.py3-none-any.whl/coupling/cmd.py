# coding: utf-8

import typing
import subprocess

import logging
logger = logging.getLogger(__name__)


def run(cmd: typing.Union[str, typing.Sequence], wait: bool=True, **kwargs):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
    if wait:
        stdout, stderr = process.communicate()
        return process.returncode, stdout
    else:
        return process
