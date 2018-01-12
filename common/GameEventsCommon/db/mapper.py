# Embedded file name: scripts/common/GameEventsCommon/db/mapper.py
from __future__ import absolute_import
import functools
import msgpack
from .helpers import findInindex, findHasAttrs, filterByAttrsAndValues, addToDummyInstance, setInDummyInstance, NO_CACHED_VALUE
from .generator import generateMappingAsDict
from ..helpers.core import dictToObj

class BundledDatabase(object):
    """
    mapping = {
        'db': DB,
        'indexes': {
            'subscriber':
                'id': {
                    1: DB.subscriber[0],
                    2: DB.subscriber[1]
                },
                'hash': {
                    23232: DB.subscriber[0],
                }
            }
        },
        'rename': {
            'id': 'hash',
            'raw_id': 'id'
        },
        'type': {
            'default': 'subscriber',
            'all': ['quest', 'blah']
        },
    }
    """

    def __init__(self, mapping, applyMerge = True):
        self._db = mapping['db']
        self._cache = {}
        applyMerge = getattr(self._db, '_applyMerge', applyMerge)
        if hasattr(self._db, 'header') and applyMerge:
            for item in getattr(self._db, mapping['type']['default'], []):
                setInDummyInstance(item, self._db.header)

        if hasattr(self._db, 'include') and applyMerge:
            for item in getattr(self._db, mapping['type']['default'], []):
                addToDummyInstance(item, self._db.include, mapping['type']['default'])

        if applyMerge:
            setattr(self._db, '_applyMerge', False)
        self._settings = mapping

    @classmethod
    def fromModule(cls, module, applyMerge = True):
        return cls(module.mapping, applyMerge=applyMerge)

    @classmethod
    def fromDict(cls, dict_):
        from GameEvents.eps.db.helpers import generateIdForSubscriber, DB_TYPE, generateParentForSubscriber, generateIdForEvents
        object_ = dictToObj(dict_)
        return cls(generateMappingAsDict(object_, 'DB', 'subscriber', indexes={'subscriber': ('id', 'name', 'type', 'group', 'eventIds', 'parent')}, attributes={'subscriber': {'id': functools.partial(generateIdForSubscriber, DB_TYPE.SERVER, {DB_TYPE.SERVER: {}}, {DB_TYPE.SERVER: {}}),
                        'parent': generateParentForSubscriber,
                        'eventIds': generateIdForEvents}}, nested=('subscriber.nested',)))

    @property
    def _indexes(self):
        return self._settings.get('indexes', {})

    def all(self, type_ = None, includeNested = False):
        key = (type_, includeNested)
        result = self._cache.get(key, NO_CACHED_VALUE)
        if result != NO_CACHED_VALUE:
            return result
        type_ = self._settings['type']['default']
        nested = self._settings.get('nested', [])
        result = []
        for path in nested:
            if type_ in path:
                nested = path.split('.')
                break

        for item in getattr(self._db, type_, []):
            result.append(item)

            def processNested(item, includeNested, nested, result):
                if includeNested and nested:
                    nestedItems = getattr(getattr(item, nested[1], None), nested[0], [])
                    for nestedItem in nestedItems:
                        result.append(nestedItem)
                        processNested(nestedItem, includeNested, nested, result)

                return

            processNested(item, includeNested, nested, result)

        self._cache[key] = result
        return result

    def get(self, **attrs):
        cacheKey = 'get_{}'.format(msgpack.packb(attrs))
        result = self._cache.get(cacheKey, NO_CACHED_VALUE)
        if result != NO_CACHED_VALUE:
            return result
        else:
            objects = self.filter(**attrs)
            if len(objects) > 1:
                raise ValueError('Returned more than one object = ({}) for given attributes {}'.format(len(objects), attrs))
            elif objects:
                result = objects[0]
            else:
                result = None
            self._cache[cacheKey] = result
            return result

    def has(self, *attrs):
        cacheKey = 'has_{}'.format(msgpack.packb(attrs))
        result = self._cache.get(cacheKey, NO_CACHED_VALUE)
        if result != NO_CACHED_VALUE:
            return result
        type_ = self._settings['type']['default']
        indexes = self._indexes.get(type_, {})
        items = getattr(self._db, type_, [])
        result = list(findHasAttrs(indexes, items, attrs))
        self._cache[cacheKey] = result
        return result

    def filter(self, **attrs):
        cacheKey = 'filter_{}'.format(msgpack.packb(attrs))
        result = self._cache.get(cacheKey, NO_CACHED_VALUE)
        if result != NO_CACHED_VALUE:
            return result
        type_ = self._settings['type']['default']
        indexes = self._indexes.get(type_, {})
        items = getattr(self._db, type_, [])
        objects = list(findInindex(indexes, attrs))
        objects = list(filterByAttrsAndValues(objects or items, attrs))
        self._cache[cacheKey] = objects
        return objects