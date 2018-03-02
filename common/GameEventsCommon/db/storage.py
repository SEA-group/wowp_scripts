# Embedded file name: scripts/common/GameEventsCommon/db/storage.py
from __future__ import absolute_import
from .mapper import BundledDatabase

class LinkedDatabase(object):
    """Used for autolinking from compiled xmls in bundler"""
    __slots__ = ('_storage', '_bundled', '_adapters', '_related', '_cache', '_adapter_instances', '_dynamic', '_precached')

    def __init__(self, items, adapters = (), related = None):
        self._storage = {}
        self._bundled = {}
        self._adapters = {}
        self._adapter_instances = []
        self._cache = {}
        self._related = related
        self._dynamic = {}
        self._precached = False
        for adapter in adapters:
            adapter = adapter(self, self._bundled, self._related)
            self._adapter_instances.append(adapter)
            self._adapters.update(adapter.mapping)

        for item in items:
            self._storage.setdefault(item, {})

    def set(self, name, key, value, valueFrom = None):
        if valueFrom is not None:
            value = valueFrom.get(key, None)
        self._storage[name][key] = value
        self._cache.pop((name, key), None)
        self._cache.pop(('all', name), None)
        return

    def append(self, name, key, value):
        items = self._storage[name].get(key, [])
        items.append(value)
        self.set(name, key, items)

    def has(self, name, key):
        return self.get(name, key, precache=False) is not None

    def get(self, name, key, default = None, precache = True):
        cacheKey = (name, key)
        if cacheKey in self._cache:
            return self._cache[cacheKey]
        else:
            value = self._storage[name].get(key, default)
            if name == 'subscribersForEvent':
                value = value or []
            if not value or name == 'subscribersForEvent':
                adapter = self._adapters.get(name)
                if adapter:
                    adapterValue = adapter(key)
                    if adapterValue is None and value is None:
                        value = default
                    else:
                        if name == 'subscribersForEvent':
                            value = list(set(value + adapterValue))
                        if not value:
                            value = adapterValue
            if precache:
                self._cache[cacheKey] = value
            return value

    def all(self, name, default = None):
        cacheKey = ('all', name)
        if cacheKey in self._cache:
            return self._cache[cacheKey]
        else:
            default = default or []
            value = self._storage.get(name, default)
            resultValue = value
            adapter = self._adapters.get(name)
            if adapter:
                adValue = adapter(None, isAll=True)
                if adValue:
                    if isinstance(adValue, dict):
                        resultValue = resultValue.copy()
                        resultValue.update(adValue)
                    else:
                        resultValue = value + adValue
            self._cache[cacheKey] = resultValue
            return resultValue

    def link(self, module):
        if module.__name__ in self._bundled:
            return
        if isinstance(module, str):
            module = __import__(module, globals(), locals(), ['object'], -1)
        self._bundled[module.__name__] = BundledDatabase.fromModule(module)
        for adapter in self._adapter_instances:
            adapter.onLinked()

    def unlink(self, module):
        self._bundled.pop(module, None)
        return

    def linkModel(self, model):
        for name, bundled in model._backend._databases.iteritems():
            if name not in self._bundled:
                self._bundled[name] = bundled

        for adapter in self._adapter_instances:
            adapter.modules = self._bundled
            adapter.onLinked()

    @property
    def linkedDynamicDatabases(self):
        return self._dynamic

    def linkDBs(self, databases):
        if not databases and not self._dynamic:
            return
        self._bundled = {name:db for name, db in self._bundled.iteritems() if name not in self._dynamic}
        dbsToRemove = set(self._dynamic.keys()) - set(databases.keys())
        if dbsToRemove:
            self._related.logger.info('Manager databases removed {}'.format(list(dbsToRemove)))
            for key in dbsToRemove:
                self._dynamic.pop(key)

        for name, db in databases.iteritems():
            if name not in self._dynamic and db:
                self._dynamic[name] = db
                self._related.logger.info('Linking to manager "{}"'.format(name))

        self._bundled.update(self._dynamic)
        for adapter in self._adapter_instances:
            adapter.modules = self._bundled
            adapter.onLinked()

        self.precache(force=True)

    def precache(self, force = False):
        if self._precached and not force:
            return
        self._cache.clear()
        eventKeys = [self._related.hasher.event({'type': 'operation',
          'context': 'subscriber',
          'name': 'changed'}),
         self._related.hasher.event({'type': 'operation',
          'context': 'subscriber',
          'name': 'completed'}),
         self._related.hasher.event({'type': 'battle',
          'context': 'player',
          'name': 'win'}),
         self._related.hasher.event({'type': 'battle',
          'context': 'player',
          'name': 'lose'}),
         self._related.hasher.event({'type': 'battle',
          'context': 'player',
          'name': 'draw'}),
         self._related.hasher.event({'type': 'battle',
          'context': 'player',
          'name': 'result'}),
         self._related.hasher.event({'type': 'battle',
          'context': 'player',
          'name': 'part.destroy'}),
         self._related.hasher.event({'type': 'coach',
          'context': 'rank',
          'name': 'navy'}),
         self._related.hasher.event({'type': 'coach',
          'context': 'rank',
          'name': 'heavy.fighter'}),
         self._related.hasher.event({'type': 'coach',
          'context': 'rank',
          'name': 'fighter'}),
         self._related.hasher.event({'type': 'coach',
          'context': 'rank',
          'name': 'bomber'}),
         self._related.hasher.event({'type': 'coach',
          'context': 'rank',
          'name': 'assault'})] + list(self.all('event'))
        topNames = ('points.battle', 'points.mastery', 'kill.plane', 'kill.ground', 'kill.plane.defender', 'damage.ground', 'damage.plane', 'sector.capture')
        for top in (1, 3, 5):
            for name in topNames:
                eventKeys.append(self._related.hasher.event({'type': 'battle',
                 'context': 'player',
                 'name': 'top.{}.by.{}'.format(top, name)}))

        for key in eventKeys:
            self.get('event', key)
            self.get('subscribersForEvent', key)

        for key in self.all('subscriber'):
            self.get('settings', key)
            self.get('convertedSettings', key)
            self.get('subscriber', key)
            self.get('parentSubscriber', key)
            completed = self._related.hasher.event({'type': 'operation',
             'context': 'subscriber',
             'name': 'completed.{}'.format(key)})
            changed = self._related.hasher.event({'type': 'operation',
             'context': 'subscriber',
             'name': 'changed.{}'.format(key)})
            self.get('event', completed)
            self.get('subscribersForEvent', completed)
            self.get('event', changed)
            self.get('subscribersForEvent', changed)
            processors = self.get('processor', key)
            self.get('handler', key)
            for processor in processors:
                processor.metadata = {'subscriber': key}
                processor.precache()

        self._precached = True

    def unlinkModel(self, module):
        self._bundled.pop(module, None)
        return