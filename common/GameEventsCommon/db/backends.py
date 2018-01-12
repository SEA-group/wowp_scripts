# Embedded file name: scripts/common/GameEventsCommon/db/backends.py
from BWLogging import getLogger
import msgpack
from .mapper import BundledDatabase
from .helpers import NO_CACHED_VALUE

class ModelBackend(object):
    REQUIRED = ()
    ADAPTERS = ()

    def __init__(self, **settings):
        self.logger = getLogger('Backend:{}'.format(self.__class__.__name__))
        self._settings = settings
        self._cache = {}
        notProvided = set(self.__class__.REQUIRED) - set(settings.keys())
        if notProvided:
            raise ValueError('Not all settings passed to backend. Missed [{}]'.format(list(notProvided)))
        self.prepare()

    def prepare(self):
        """Used as hook after init, custom imports or other things"""
        pass

    def reload(self):
        """Implement this method if you need reload
        something to get latest data"""
        pass

    def all(self, type_ = None):
        return NotImplementedError

    def get(self, **attrs):
        return NotImplementedError

    def has(self, *attrs):
        return NotImplementedError

    def filter(self, **attrs):
        return NotImplementedError


class BundledBackend(ModelBackend):
    REQUIRED = ('modules',)

    def prepare(self):
        self._databases = {}
        for module in self._settings['modules']:
            if isinstance(module, str):
                module = __import__(module, globals(), locals(), ['object'], -1)
            self._databases[module.__name__] = BundledDatabase.fromModule(module, self._settings.get('applyMerge', True))

        self._updateCache()

    def reload(self):
        for path, module in self._databases.iteritems():
            self._databases[path] = __import__(path, globals(), locals(), ['object'], -1)

    def all(self, type_ = None, includeNested = False):
        key = (type_, includeNested)
        result = self._cache.get(key, NO_CACHED_VALUE)
        if result != NO_CACHED_VALUE:
            return result
        items = []
        for db in self._databases.itervalues():
            items.extend(db.all(type_, includeNested))

        self._cache[key] = items
        return items

    def get(self, id = None, type = None, group = None, name = None, parent = None):
        attrs = ('get',
         id,
         type,
         group,
         name,
         parent)
        result = self._cache.get(attrs, NO_CACHED_VALUE)
        if result != NO_CACHED_VALUE:
            return result
        else:
            items = []
            params = {}
            if id is not None:
                params['id'] = id
            if type is not None:
                params['type'] = type
            if group is not None:
                params['group'] = group
            if name is not None:
                params['name'] = name
            if parent is not None:
                params['parent'] = parent
            for db in self._databases.itervalues():
                item = db.get(**params)
                if item:
                    items.append(item)

            if len(items) > 1:
                raise ValueError('Returned more than one object = ({}) items = {} for given attributes {}'.format(len(items), [ vars(i) for i in items ], attrs))
            elif items:
                items = items[0]
            else:
                items = None
            self._cache[attrs] = items
            return items

    def has(self, *attrs):
        cacheKey = 'has_{}'.format(msgpack.packb(attrs or ''))
        result = self._cache.get(cacheKey, NO_CACHED_VALUE)
        if result != NO_CACHED_VALUE:
            return result
        items = []
        for db in self._databases.itervalues():
            items.extend(db.has(*attrs))

        self._cache[cacheKey] = items
        return items

    def filter(self, id = None, type = None, group = None, name = None, parent = None):
        attrs = ('filter',
         id,
         type,
         group,
         name,
         parent)
        itmes = self._cache.get(attrs, NO_CACHED_VALUE)
        if itmes != NO_CACHED_VALUE:
            return itmes
        else:
            items = []
            params = {}
            if id is not None:
                params['id'] = id
            if type is not None:
                params['type'] = type
            if group is not None:
                params['group'] = group
            if name is not None:
                params['name'] = name
            if parent is not None:
                params['parent'] = parent
            for db in self._databases.itervalues():
                items.extend(db.filter(**params))

            self._cache[attrs] = items
            return items

    def _updateCache(self):
        self._cache = {}
        allItems = self.all(type_=None, includeNested=True)
        for item in allItems:
            self.get(id=item.id)
            try:
                self.get(type=item.type, name=item.name, group=item.group)
            except (AttributeError, ValueError):
                pass

            try:
                self.get(type=item.type, group=item.group)
            except (AttributeError, ValueError):
                pass

            try:
                self.get(name=item.name, group=item.group)
            except (AttributeError, ValueError):
                pass

            try:
                self.filter(name=item.name)
            except AttributeError:
                pass

            try:
                self.filter(parent=item.id)
            except AttributeError:
                pass

            try:
                self.filter(type=item.type)
            except AttributeError:
                pass

            try:
                self.filter(group=item.group)
            except AttributeError:
                pass

        self.filter()
        return

    def updateDynamic(self, databases):
        pass


class DynamicBundledBackend(BundledBackend):

    def __init__(self, **settings):
        self._dynDatabases = {}
        super(DynamicBundledBackend, self).__init__(**settings)

    def updateDynamic(self, databases):
        """
        Update dynamic data and rebuild cache
        :param databases: dict[<db name>, <bundled db>]
        :type databases: dict[str, BundledDatabase]
        
        If we have :type:None in bundled db => database not changed
        """
        if not databases and not self._dynDatabases:
            return
        else:
            dbsToRemove = set(self._dynDatabases.keys()) - set(databases.keys())
            if dbsToRemove:
                self.logger.info('Backend databases removed {}'.format(list(dbsToRemove)))
                for key in dbsToRemove:
                    self._dynDatabases.pop(key)

            for name, db in databases.iteritems():
                if db is None:
                    self.logger.info('Do not changed database "{}" skipping'.format(name))
                else:
                    self.logger.info('Linking new database "{}"'.format(name))
                    self._dynDatabases[name] = db

            self._databases = {name:self._databases[name] for name in self._settings['modules']}
            self._updateCache()
            return

    def _updateCache(self):
        self._databases.update(self._dynDatabases)
        super(DynamicBundledBackend, self)._updateCache()