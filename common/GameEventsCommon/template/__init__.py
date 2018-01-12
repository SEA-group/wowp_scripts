# Embedded file name: scripts/common/GameEventsCommon/template/__init__.py
"""
Used from wheezy.template http://pythonhosted.org/wheezy.template/

# TODO: remove unused code, thread locks, rename to camelcase
"""
from __future__ import absolute_import
from .engine import Engine
from .ext.code import CodeExtension
from .ext.core import CoreExtension
from .loader import DictLoader, FileLoader, PreprocessLoader
__version__ = '0.1'