# -*- coding: utf-8 -*-

import os
import stat
import errno
import sys
import typing
import shutil
import re

import logging
logger = logging.getLogger(__name__)

if sys.platform.startswith("linux"):
    import pwd #@UnresolvedImport


ExcludeType = typing.Union[str, re._pattern_type]


def find(path: str, bydepth: bool=True, exclude: ExcludeType=None,
         topdir: bool=True, topdown: bool=True) -> typing.Iterator[str]:
    """
    @:param bydepth: Reports the name of a directory only AFTER all its entries have been reported
    @:param exclude: a string or re pattern type, use this to exclude the path you don't want to find
    @:param topdir: whether include the topdir path
    @:param topdown: find the path with top->down or down->top
    """
    if not os.path.exists(path):
        raise OSError(errno.ENOENT, "No such file or directory: '%s'" % path)

    if exclude is not None and not isinstance(exclude, re._pattern_type):
        exclude = re.compile(exclude)

    def walkdir(dirpath, bydepth, exclude):
        names = os.listdir(dirpath)
        if not topdown:
            names.reverse()

        for name in names:
            found = os.path.join(dirpath, name)

            if exclude and exclude.search(found):
                logger.info("walk: skip %s", found)
                continue

            logger.log(logging.NOTSET, "walk: process %s", found)
            if not bydepth:
                yield found
            if os.path.isdir(found):
                for x in walkdir(found, bydepth, exclude):
                    yield x
            if bydepth:
                yield found

    if os.path.isdir(path):
        if topdir and not bydepth:
            yield path
        for x in walkdir(path, bydepth, exclude):
            yield x
        if topdir and bydepth:
            yield path
    else:
        yield path


def chmod(path: str, mode: int, recursive: bool=False, exclude: ExcludeType=None) -> None:
    logger.info("chmod: path=%s, mode=%s, recursive=%s, exclude=%s", path, mode, recursive, exclude)

    for subpath in find(path, False, exclude):
        os.chmod(subpath, mode)


def chown(path: str, user: str=None, group: str=None, recursive: bool=False, exclude: ExcludeType=None) -> None:
    logger.info("chown: path=%s, user=%s, group=%s, recursive=%s, exclude=%s", path, user, group, recursive, exclude)

    uid = pwd.getpwnam(user).pw_uid if user else -1
    gid = pwd.getpwnam(group).pw_gid if group else -1
    for subpath in find(path, False, exclude):
        os.chown(subpath, uid, gid)


def mkdirs(path: str, mode: int=0o755) -> None:
    if os.path.exists(path):
        if os.path.isdir(path):
            logger.log(logging.NOTSET, "mkdirs: exists '%s', type is dir, skip", path)
        else:
            raise OSError("mkdirs failed, path '%s' already exists, type is file" % path)
    else:
        logger.log(logging.NOTSET, "mkdirs: non-exists '%s' ", path)
        head, tail = os.path.split(path)
        if not tail:   # no tail when xxx/newdir
            head, tail = os.path.split(head)
        if head and tail:
            mkdirs(head, mode)
            if tail != os.path.curdir:   # xxx/newdir/. exists if xxx/newdir exists
                logger.info("mkdirs: path=[%s], mode=[%s]", path, mode)
                os.mkdir(path, mode)


def copy(src: str, dst: str, exclude: ExcludeType=None, symlinks: bool=False) -> typing.Tuple[int, int]:
    logger.info("copy: src=%s, dst=%s, exclude=%s", src, dst, exclude)

    num_of_dirs = 0
    num_of_files = 0

    def _copyfile(srcpath, dstpath):
        try:
            shutil.copy2(srcpath, dstpath)
        except IOError as ioerr:
            if ioerr.errno == errno.ENOENT:
                raise
            elif ioerr.errno == errno.EACCES:
                logger.warn("copy: dst %s is 'permission denied', remove it and retry", dstpath)
                os.remove(dstpath)
                shutil.copy2(srcpath, dstpath)
                logger.log(logging.NOTSET, "copy: copy %s -> %s successfully ", srcpath, dstpath)
            else:
                pass

    if os.path.isdir(src):
        if not os.path.exists(dst):
            mkdirs(dst)
        for sub_path in find(src, False, exclude, topdir=False):
            rel_path = os.path.relpath(sub_path, src)
            abs_path = os.path.join(dst, rel_path)
            if os.path.isdir(sub_path):
                if not os.path.exists(abs_path):
                    os.mkdir(abs_path)
                num_of_dirs += 1
            else:
                if symlinks and os.path.islink(src):
                    os.symlink(os.readlink(src), dst)
                else:
                    logger.log(logging.NOTSET, "copy: %s -> %s", sub_path, abs_path)
                    _copyfile(sub_path, abs_path)
                num_of_files += 1
    else:
        if not os.path.exists(dst):
            if dst.endswith("\\") or dst.endswith("/"):
                mkdirs(dst)
            else:
                mkdirs(os.path.dirname(dst))
        logger.log(logging.NOTSET, "copy: %s -> %s", src, dst)
        _copyfile(src, dst)
        num_of_files += 1

    logger.info("copy %s files and %s dirs to %s", num_of_files, num_of_dirs, dst)
    return num_of_dirs, num_of_files


def remove(path: str, exclude: ExcludeType=None) -> typing.Tuple[int, int]:
    logger.info("remove: path=[%s], exclude=[%s]", path, exclude)

    num_of_dirs = 0
    num_of_files = 0

    for sub_path in find(path, True, exclude, True):
        if os.path.isdir(sub_path):
            os.rmdir(sub_path)
            num_of_dirs += 1
        else:
            try:
                os.remove(sub_path)
            except WindowsError as werr:
                if werr.errno == errno.EACCES:
                    logger.debug("remove: %s access is denied, chmod its mode to S_IWRITE and retry", sub_path)
                    os.chmod(sub_path, stat.S_IWRITE)
                    os.remove(sub_path)
                    logger.debug("remove: remove %s successfully", sub_path)
                else:
                    pass
            num_of_files += 1
    logger.info("removed %s files and %s dirs from %s", num_of_files, num_of_dirs, path)
    return num_of_dirs, num_of_files


# TODO:
def move(src: str, dst: str, exclude: ExcludeType=None) -> None:
    logger.info("move: src=[%s], dst=[%s], exclude=[%s]", src, dst, exclude)
    #    def _movefile(src, dst):
    #        try:
    #            real_dst = dst
    #            if os.path.isdir(dst):
    #                real_dst = os.path.join(dst, os.path.basename(src))
    #            os.rename(src, real_dst)
    #        except:
    #            copy(src, dst)
    #            remove(src)
    #
    copy(src, dst, exclude)
    remove(src, exclude)


def touch(path: str, time=None) -> None:
    logger.info("touch: path=%s, time=%s", path, time)
    if not os.path.exists(path):
        dirname = os.path.dirname(path)
        if os.path.isdir(dirname):
            with open(path, 'w'):
                pass
        else:
            mkdirs(os.path.dirname(path))
    os.utime(path, time)


def link(src, target):
    raise NotImplementedError


def symlink(src, target):
    raise NotImplementedError
