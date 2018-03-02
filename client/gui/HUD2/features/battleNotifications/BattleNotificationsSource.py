# Embedded file name: scripts/client/gui/HUD2/features/battleNotifications/BattleNotificationsSource.py
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from debug_utils import *

class BattleNotificationsSource(DataSource):
    """
    @type _model: gui.HUD2.features.battleNotifications.BattleNotificationsModel.BattleNotificationsModel
    """

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).battleNotifications
        self._dependency = features.require(Feature.GAME_MODEL).consumables
        self._messenger = features.require(Feature.BATTLE_HINTS).battleAlerts
        self._db = features.require(Feature.DB_LOGIC)
        self._notificationCounter = 1
        self._messenger.assignModelView(self)

    def dispose(self):
        self._messenger.assignModelView(None)
        self._dependency = None
        self._messenger = None
        self._model = None
        self._db = None
        return

    def _checkOnDependency(self, data):
        dependency = data.consumableDependency
        res = ('', data.description)
        for slot in self._dependency.consumables:
            consumableDB = self._db.getConsumableByID(slot.id.get())
            if consumableDB is not None and consumableDB.localizeTag in dependency:
                notAuto = not slot.isAuto.get()
                notEmpty = not slot.isEmpty.get()
                if notAuto and notEmpty:
                    res = (slot.key.get(), consumableDB.name)
                    break

        return res

    def pushMessage(self, data):
        self._notificationCounter += 1
        battleNotificationData = dict(type=data.type, title=data.title, icon=data.icon, lifetime=data.lifeTime, priority=data.priority, description=data.description, key='', notificationCounter=self._notificationCounter, data=data.data)
        key, description = self._checkOnDependency(data)
        battleNotificationData['key'] = key
        battleNotificationData['description'] = description
        self._model.battleNotification = battleNotificationData