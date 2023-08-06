# -*- coding: utf-8 -*-

"""
version infomations
"""

from __future__ import absolute_import, unicode_literals

from pkg_resources import get_distribution

__all__ = ['NAME', 'NAMESPACE', '__version__']

NAME = 'aliyunoss2-autoupload'
NAMESPACE = '.'.join(__name__.split('.')[:-1])  # name of the package

# pylint: disable=C0103
__version__ = get_distribution(NAME).version  # type: str
