#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, with_statement, print_function

import concurrent.futures
import os
import sys
from glob import iglob
from multiprocessing import cpu_count
from shutil import move
from time import time

import oss2
from oss2.exceptions import OssError

try:
    import crcmod._crcfunext
except ImportError as err:
    ENABLE_CRC = False
    print('{0}. CRC DISABLED'.format(err), file=sys.stderr)
else:
    ENABLE_CRC = True

from . import glb
from .utils.loggermixin import LoggerMixin

__all__ = ['Performer']

_PYTHON_VERSION_MAYOR_MINOR = '{0[0]}.{0[1]}'.format(sys.version_info)


class Performer(LoggerMixin):
    _executor = None  # type: concurrent.futures.Executor

    @classmethod
    def initial(cls):
        max_workers = glb.config['watcher']['max_workers']
        if max_workers is not None:
            max_workers = int(max_workers)
        else:
            if _PYTHON_VERSION_MAYOR_MINOR < '3.5':
                # Changed in version 3.5:
                # If max_workers is None or not given,
                # it will default to the number of processors on the machine, multiplied by 5
                max_workers = cpu_count() * 5
        cls._executor = concurrent.futures.ThreadPoolExecutor(max_workers)

    @classmethod
    def release(cls):
        if cls._executor:
            cls._executor.shutdown()

    @classmethod
    def run_once(cls):
        logger = cls.get_logger()

        now_ts = time()
        fs = []  # type: List[concurrent.futures.Future]
        patterns = glb.config['watcher']['patterns']

        if _PYTHON_VERSION_MAYOR_MINOR >= '3.5':
            iterator = iglob(patterns, recursive=bool(glb.config['watcher']['recursive']))
        else:
            iterator = iglob(patterns)

        for path in iterator:
            # is file write completed? (According to last modify time)
            mod_ts = os.path.getmtime(path)
            if now_ts - mod_ts > glb.config['watcher']['write_complete_time']:
                task = Task(path)
                cls.get_logger().info('submit task: %r', task)
                fut = cls._executor.submit(cls._execute_task, task)
                fs.append(fut)

        if fs:
            logger.debug('%d task(s) pending ...', len(fs))
            done, not_done = concurrent.futures.wait(fs)
            logger.debug(
                '%d task(s) completed. count_of_done=%s, count_of_not_done=%s. duration=%s',
                len(fs), len(done), len(not_done), time() - now_ts
            )

    @classmethod
    def _execute_task(cls, task):  # type: (Task) -> bool
        begin_ts = time()

        logger = cls.get_logger()
        logger.debug('execute_task(%r) >>>', task)

        try:
            bucket = cls._get_oss_bucket()
            try:
                logger.info(
                    'execute_task(): upload %s => %s',
                    task.path, task.oss_key
                )
                bucket.put_object_from_file(task.oss_key, task.path)
            except FileNotFoundError as e:
                logger.error(
                    'upload %s => %s. FileNotFoundError: %s',
                    task.path, task.oss_key, e
                )
                return False
            except OssError as e:
                logger.error(
                    'upload %s => %s. OssError: %s',
                    task.path, task.oss_key, e
                )
                return False

            try:
                if task.bak_dir:
                    logger.info(
                        'backup %s => %s',
                        task.path, task.bak_dir
                    )
                    bak_dir = os.path.dirname(task.bak_dir)
                    os.makedirs(bak_dir, exist_ok=True)
                    move(task.path, task.bak_dir)
                else:
                    logger.info(
                        'remove %s',
                        task.path
                    )
                    os.remove(task.path)
            except FileNotFoundError as e:
                logger.error(
                    'backup %s => %s. FileNotFoundError: %s',
                    task.path, task.oss_key, e
                )
                return False
            except OSError as e:
                logger.error(
                    'backup %s => %s. OSError: %s',
                    task.path, task.oss_key, e
                )
                return False

        except Exception:
            logger.exception('execute_task({!r})'.format(task))
            raise

        finally:
            logger.debug('execute_task(%r) <<< duration=%s', task, time() - begin_ts)

        return True

    @classmethod
    def _get_oss_bucket(cls):
        cfg = glb.config['oss']
        endpoint = cfg['endpoint'].strip()  # type: str
        bucket_name = cfg['name'].strip()  # type: str
        auth = oss2.Auth(cfg['access_key_id'].strip(), cfg['access_key_secret'].strip())
        cname = cfg.get('cname', '')  # type: str
        cname = '' if cname is None else cname.strip()
        bucket = oss2.Bucket(
            auth, endpoint, bucket_name, is_cname=bool(cname), enable_crc=ENABLE_CRC
        )
        return bucket


class Task(object):

    def __init__(self, path):
        self._path = path
        self._oss_key = ''
        self._bak_dir = ''

        rel_dir = glb.config['dir']['rel_dir']
        if rel_dir:
            rel_path = os.path.relpath(path, rel_dir)
        else:
            rel_path = os.path.relpath(path)
        bak_dir = glb.config['dir'].get('bak_dir')
        if bak_dir:
            self._bak_dir = os.path.realpath(os.path.join(glb.config['dir']['bak_dir'], rel_path))
        else:
            self._bak_dir = None
        upload_path = os.path.normpath(rel_path)
        upload_dir = glb.config['dir']['oss_dir']
        if upload_dir:
            self._oss_key = '/'.join((upload_dir, upload_path))
        else:
            self._oss_key = upload_path

    @property
    def path(self):
        return self._path

    @property
    def oss_key(self):
        return self._oss_key

    @property
    def bak_dir(self):
        return self._bak_dir

    def __repr__(self):
        rep = super(Task, self).__repr__()
        return '{0}(path={1}, oss_key={2}, bak_path={3})'.format(
            rep, self.path, self.oss_key, self.bak_dir)
