# Embedded file name: scripts/common/GameEventsCommon/validation/schema/__init__.py
"""
    Extensible validation for Python dictionaries.

    :copyright: 2012-2016 by Nicola Iarocci.
    :license: ISC, see LICENSE for more details.

    Full documentation is available at http://python-.org/

"""
from __future__ import absolute_import
from .validator import Validator, DocumentError
from .schema import rules_set_registry, schema_registry, Registry, SchemaError
__version__ = '1.1'
__all__ = [DocumentError.__name__,
 Registry.__name__,
 SchemaError.__name__,
 Validator.__name__,
 'schema_registry',
 'rules_set_registry']