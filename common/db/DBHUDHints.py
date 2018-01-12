# Embedded file name: scripts/common/db/DBHUDHints.py
from DBHelpers import readValue, findSection
from debug_utils import LOG_ERROR, LOG_DEBUG

class _HudHint(object):
    pass


class HudHints(object):

    def __init__(self, data = None):
        self._hints = dict()
        if data is not None:
            self.readData(data)
        return

    def getHint(self, id):
        return self._hints.get(id, None)

    def getAllHints(self):
        return self._hints


class BattleAlerts(HudHints):

    def readData(self, rootSection):
        for name, data in rootSection.items():
            hint = _HudHint()
            readValue(hint, data, 'id', 0)
            if hint.id:
                readValue(hint, data, 'type', -1)
                readValue(hint, data, 'title', '')
                readValue(hint, data, 'icon', '')
                readValue(hint, data, 'lifeTime', -1)
                readValue(hint, data, 'priority', -1)
                readValue(hint, data, 'description', '')
                readValue(hint, data, 'coolDown', 0)
                self._readSubItemList(hint, data, 'consumableDependency', 'section')
                self._readSubItemList(hint, data, 'validPlanes', 'section')
                self._hints[hint.id] = hint
                LOG_DEBUG('readData - added battle alert:', hint.id, hint.__dict__)
            else:
                LOG_ERROR('readData - battle alert without ID. Check it!')

    @staticmethod
    def _readSubItemList(storage, data, sectionsName, subItemName):
        dataList = findSection(data, sectionsName).readStrings(subItemName)
        setattr(storage, sectionsName, list(dataList))


class BattleNotifications(HudHints):

    def readData(self, rootSection):
        for name, data in rootSection.items():
            hint = _HudHint()
            readValue(hint, data, 'id', 0)
            if hint.id:
                readValue(hint, data, 'type', -1)
                readValue(hint, data, 'title', '')
                readValue(hint, data, 'icon', '')
                readValue(hint, data, 'lifeTime', -1)
                readValue(hint, data, 'priority', -1)
                readValue(hint, data, 'description', '')
                readValue(hint, data, 'coolDown', 0)
                readValue(hint, data, 'timer', -1)
                readValue(hint, data, 'addValue', -1)
                self._hints[hint.id] = hint
                LOG_DEBUG('readData - added battle notification:', hint.id, hint.__dict__)
            else:
                LOG_ERROR('readData - battle notification without ID. Check it!')