# Embedded file name: scripts/common/GameEventsCommon/db/generator.py
from __future__ import absolute_import
import zlib
from collections import OrderedDict
from ..template.engine import Engine
from ..template.ext.core import CoreExtension
from ..template.loader import DictLoader
from .helpers import setInDummyInstance, addToDummyInstance
mappingEpilog = '\n@require(name, indexes, rename, type, attributes, nested)\n\n@if attributes:\n# additional calculated attributes\n@for type_, fields in indexes.iteritems():\n    @for field, data in fields.iteritems():\n        @if field in attributes[type_]:\n            @for key, value in data.iteritems():\n                @for item in value:\n@{item}.@{field} = @{str(key) if not isinstance(key, str) else "\'" + key + "\'"}\n                @end\n            @end\n        @end\n    @end\n@end\n\n@end\n\n# indexes\nmapping = {\n    \'db\': @name,\n    @if indexes:\n    \'indexes\': {\n    @for type_, fields in indexes.iteritems():\n        \'@type_\': {\n        @for field, data in fields.iteritems():\n            \'@field\': {\n                @for key, path in data.iteritems():\n                @{str(key) if not isinstance(key, str) else "\'" + key + "\'"}: (\n                    @for item in path:\n                    @item,\n                    @end\n                ),\n                @end\n            },\n        @end\n        }\n    @end\n    },\n    @end\n\n    @if rename:\n    \'rename\': {\n    @for fromField, toField in rename.iteritems():\n        \'@fromField\': \'@toField\',\n    @end\n    },\n    @end\n\n    @if nested:\n    \'nested\': @{repr(nested)},\n    @end\n\n    \'type\': {\n        \'default\': \'@{type[\'default\']}\',\n        \'all\': [\n        @for type in type[\'all\']:\n            \'@type\',\n        @end\n        ]\n    },\n}\n'

def collectItemsToIndex(name, db, type_, field, storage, nested, attributes, parents = (), itemParents = ()):
    for index, item in enumerate(getattr(db, type_, [])):
        key = getattr(item, field, None)
        if key is None:
            wrapper = attributes.get(type_, {}).get(field, None)
            if wrapper is not None:
                key = wrapper(db, item, itemParents)
        if key is not None:
            path = '{}.{}'.format(name, type_)
            for index_, include_ in parents:
                path = '{}[{}].{}.{}'.format(path, index_, include_, type_)

            path = '{}[{}]'.format(path, index)
            storage.setdefault(key, []).append(path)
        for include in nested:
            db = getattr(item, include, None)
            if db is not None:
                collectItemsToIndex(name, db, type_, field, storage, nested, attributes, parents + ((index, include),), itemParents + (item,))

    return


def collectItemsToIndexWithoutStringPath(name, db, type_, field, storage, nested, attributes, parents = (), itemParents = ()):
    for index, item in enumerate(getattr(db, type_, [])):
        key = getattr(item, field, None)
        if key is None:
            wrapper = attributes.get(type_, {}).get(field, None)
            if wrapper is not None:
                key = wrapper(db, item, itemParents)
                if key is not None:
                    setattr(item, field, key)
        if key is not None:
            storage.setdefault(key, []).append(item)
        for include in nested:
            db = getattr(item, include, None)
            if db is not None:
                collectItemsToIndexWithoutStringPath(name, db, type_, field, storage, nested, attributes, parents + ((index, include),), itemParents + (item,))

    return


def generateIndexFromSettings(name, db, indexes, nested, attributes, asStringLinks = True):
    defaultDict = OrderedDict if asStringLinks else dict
    result = defaultDict()
    for type_, fields in indexes.iteritems():
        resultType = result.setdefault(type_, defaultDict())
        currentNested = [ include.lstrip('{}.'.format(type_)) for include in nested if type_ in include ]
        for field in fields:
            storage = resultType.setdefault(field, defaultDict())
            if asStringLinks:
                collectItemsToIndex(name, db, type_, field, storage, currentNested, attributes)
            else:
                collectItemsToIndexWithoutStringPath(name, db, type_, field, storage, currentNested, attributes)

    return result


def generateMappingAsDict(db, name, defaultType, additionalTypes = (), indexes = None, attributes = None, nested = ()):
    if hasattr(db, 'header'):
        for item in getattr(db, defaultType, []):
            setInDummyInstance(item, db.header)

    if hasattr(db, 'include'):
        for item in getattr(db, defaultType, []):
            addToDummyInstance(item, db.include, defaultType)

    result = generateIndexFromSettings(name, db, indexes, nested, attributes, asStringLinks=False)
    return {'db': db,
     'name': name,
     'indexes': result,
     'type': {'default': defaultType,
              'all': (defaultType,) + additionalTypes},
     'nested': nested,
     'attributes': attributes}


def generateMapping(db, name, defaultType, additionalTypes = (), rename = None, indexes = None, attributes = None, nested = ()):
    if hasattr(db, 'header'):
        for item in getattr(db, defaultType, []):
            setInDummyInstance(item, db.header)

    if hasattr(db, 'include'):
        for item in getattr(db, defaultType, []):
            addToDummyInstance(item, db.include, defaultType)

    engine = Engine(loader=DictLoader({'mapping': mappingEpilog}), extensions=[CoreExtension()])
    template = engine.get_template('mapping')
    result = generateIndexFromSettings(name, db, indexes, nested, attributes)
    return template.render({'name': name,
     'indexes': result,
     'rename': rename,
     'type': {'default': defaultType,
              'all': (defaultType,) + additionalTypes},
     'nested': nested,
     'attributes': attributes})