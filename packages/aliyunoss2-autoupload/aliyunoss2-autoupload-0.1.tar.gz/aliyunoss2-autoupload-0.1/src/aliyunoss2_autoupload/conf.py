# -*- coding: utf-8 -*-

"""
Config file loader
"""

from __future__ import absolute_import, unicode_literals, print_function

import logging.config
import os
import sys

import yaml
from marshmallow import Schema, fields
from pkg_resources import Requirement, resource_string

from . import glb
from . import version
from .utils.strhelper import to_str

try:
    from yaml import CSafeLoader as YamlLoader
except ImportError:
    from yaml import SafeLoader as YamlLoader

__all__ = ['load_program_config', 'load_logging_config']

DEFAULT_PROGRAM_CONFIG_PATH = 'conf/{0}.yml'.format(version.NAME)
ENVIRON_PROGRAM_CONFIG_PATH = '{0}_CONF'.format(version.NAME.upper().replace('-', '_'))

DEFAULT_LOGGING_CONFIG_PATH = 'conf/{0}.log.yml'.format(version.NAME)
ENVIRON_LOGGING_CONFIG_PATH = '{0}_LOG_CONF'.format(version.NAME.upper().replace('-', '_'))


class OssSchema(Schema):
    """Aliyun OSS configuration schema"""

    name = fields.String(required=True)
    """Name of your Aliyun OSS bucket"""

    endpoint = fields.String(required=True)
    """Endpoint URL of Aliyun OSS bucket"""

    cname = fields.String(missing='')
    """cname of the domain of Aliyun OSS bucket. Empty if no cname."""

    access_key_id = fields.String(required=True)
    """Access Key ID of Aliyun OSS bucket"""

    access_key_secret = fields.String(required=True)
    """Access Key Secret of Aliyun OSS bucket"""


class DirSchema(Schema):
    """Directory name configuration schema"""

    rel_dir = fields.String(missing='')
    """Calculate uploading file relative name by this local directory"""

    oss_dir = fields.String(missing='')
    """Upload files to OSS in this dir"""

    bak_dir = fields.String(missing='')
    """Move uploaded file the the directory. It MUST be a different dir from where the files are. If not, the file will be uploaded again and again.
    """


class WatcherSchema(Schema):
    interval = fields.Integer(missing=30)
    """The time interval(seconds) this program scan the directory"""

    write_complete_time = fields.Integer(missing=30)
    """If the interval between the current time and the file\'s modification time is greater than this value, the write is considered complete.
    """

    patterns = fields.String(required=True)
    """Pattern of the files to watch and upload"""

    recursive = fields.Boolean(missing=False)
    """If find patterns recursively"""

    max_workers = fields.Integer(allow_none=True, missing=None)
    """pool of at most max_workers threads to execute upload/backup tasks. If max_workers is None or not given, it will default to the number of processors on the machine, multiplied by 5.
    """


class ConfSchema(Schema):
    oss = fields.Nested(OssSchema, required=True)
    dir = fields.Nested(DirSchema)
    watcher = fields.Nested(WatcherSchema, required=True)


conf_scheme = ConfSchema()


def load_yml(obj):
    if isinstance(obj, str):
        with open(obj) as f:
            data = f.read()
    else:
        try:
            read_meth = getattr(obj, 'read')
        except AttributeError:
            raise
        else:
            data = read_meth()
    return yaml.load(data, YamlLoader)


def load_program_config(obj=None):
    """加载配置文件

    :return: 配置字典
    :rtype: dict

    * 如果设置了环境变量 ``ALIYUNOSS2_AUTOUPLOAD_CONF`` ，以该环境变量的值作为配置文件路径。
    * 否则以相对路径 ``conf/aliyunoss2-autoupload.yml`` 作为配置文件路径。
    """
    # load
    if not obj:
        obj = os.environ.get(ENVIRON_PROGRAM_CONFIG_PATH)
        if not obj:
            obj = DEFAULT_PROGRAM_CONFIG_PATH
    data = load_yml(obj)
    # validate!
    config = conf_scheme.load(data)  # type: dict
    glb.config = config
    return config


def load_logging_config(obj=None):
    """加载 logging 配置文件

    * 如果设置了环境变量 ``ALIYUNOSS2_AUTOUPLOAD_LOG_CONF`` ，以该环境变量的值作为配置文件路径。
    * 否则以相对路径 ``conf/aliyunoss2-autoupload.log.yml`` 作为配置文件路径。
    """
    if not obj:
        obj = os.environ.get(ENVIRON_LOGGING_CONFIG_PATH)
        if not obj:
            obj = DEFAULT_LOGGING_CONFIG_PATH
    try:
        data = load_yml(obj)
        logging.config.dictConfig(data)
    except Exception as err:
        err_msg = 'Load logging config file {0!r} failed: {1}'.format(obj, err)
        print('-' * 60, file=sys.stderr)
        print(err_msg, file=sys.stderr)
        print('-' * 60, file=sys.stderr)
        logging.warning(err_msg)
        logging.basicConfig()


def print_config(cfg, print_file=sys.stdout):
    paths = version.NAMESPACE.split('.')
    paths.extend([
        'data',
        'config-samples',
        '{0}.yml'.format(cfg)
    ])
    resource_name = os.path.join(*paths)
    txt = resource_string(Requirement.parse(version.NAME), resource_name)
    print('{0}{1}{0}'.format(os.linesep, to_str(txt)), file=print_file)
