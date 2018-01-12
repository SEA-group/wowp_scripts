# Embedded file name: scripts/client/GameEvents/model.py
from Helpers.i18n import localizeLobby, localizeAchievements

class LocalizedObject:

    def __init__(self, obj, localeFunc):
        self.obj = obj
        self.localeFunc = localeFunc or localizeLobby

    def _getLocalizedField(self, name, raw = False):
        name = getattr(getattr(getattr(self.obj, 'client', None), name, None), 'locale', '')
        old = name
        name = localizeAchievements(name) if name and not raw else name
        if old == name:
            try:
                name = self.localeFunc(old) if old and not raw else old
            except KeyError:
                pass

        return name

    @property
    def name(self):
        return self._getLocalizedField('name')

    @property
    def description(self):
        return self._getLocalizedField('description')

    @property
    def countDescription(self):
        return self._getLocalizedField('countDescription')

    @property
    def tooltip(self):
        return self._getLocalizedField('tooltip')

    @property
    def history(self):
        return self._getLocalizedField('history')

    @property
    def descriptionWithProcessorData(self):
        """From localized string '{0} something' using count processor with
        sorted ids returns '123 something'
        """
        localized = self.description
        values = [ processor['value'] for processor in sorted(self._yieldCountProcessorsForLocales(), key=lambda p: p['id']) ]
        if values:
            localized = localized.format(*values)
        return localized

    @property
    def rawName(self):
        return self._getLocalizedField('name', raw=True)

    @property
    def rawDescription(self):
        return self._getLocalizedField('description', raw=True)

    @property
    def rawTooltip(self):
        return self._getLocalizedField('tooltip', raw=True)

    @staticmethod
    def _prepareCountProcessorForLocale(processor):
        value = getattr(processor, 'value_', -1)
        id_ = getattr(processor, 'id', -1)
        if id_ == -1 or value == -1:
            return None
        else:
            return {'id': int(id_),
             'value': value}

    def _yieldCountProcessorsForLocales(self):
        for processor in getattr(self.obj, 'count', []):
            value = self._prepareCountProcessorForLocale(processor)
            if value is None:
                continue
            else:
                yield value

        for event in getattr(self.obj, 'event', []):
            for processor in getattr(event, 'count', []):
                value = self._prepareCountProcessorForLocale(processor)
                if value is None:
                    continue
                else:
                    yield value

        return


class GameEventObject(object):

    def __init__(self, attrs, context = None, model = None, localeFunc = None):
        self._attrs = attrs
        self.localized = LocalizedObject(attrs, localeFunc)

    @property
    def id(self):
        return self._attrs.id

    @property
    def name(self):
        return self._attrs.name

    @property
    def group(self):
        return self._attrs.group

    @property
    def type(self):
        return getattr(self._attrs, 'type', '')

    @property
    def parent(self):
        return getattr(self._attrs, 'parent', None)

    @property
    def client(self):
        return getattr(self._attrs, 'client', None)

    @property
    def params(self):
        """Object properties specific for type and group used in client"""
        return {}

    def __repr__(self):
        return '<{0}: name = {1}, type = {2}, group = {3}>'.format(self.__class__.__name__, self.name, self.type, self.group)