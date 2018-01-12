# Embedded file name: scripts/client/gui/HUD2/features/battleAlerts/BattleAlertsSource.py
from EntityHelpers import EntityStates
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from debug_utils import *

class BattleAlertsSource(DataSource):
    """
    @type _model: gui.HUD2.features.battleAlerts.BattleAlertsModel.BattleAlertsModel
    """

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).battleAlerts
        self._avatarPlayer = features.require(Feature.PLAYER_AVATAR)
        self._messenger = features.require(Feature.BATTLE_HINTS).battleNotification
        self._messenger.assignModelView(self)
        self._alertCounter = 1

    def pushMessage(self, data):
        if EntityStates.inState(self._avatarPlayer, EntityStates.OUTRO):
            return
        LOG_DEBUG(' BattleAlertsSource: pushMessage ', vars(data))
        self._alertCounter += 1
        battleAlertData = dict(type=data.type, title=data.title, icon=data.icon, lifetime=data.lifeTime, priority=data.priority, alertCounter=self._alertCounter)
        battleAlertData = self._checkOnAddValue(data, self._checkOnTimer(data, battleAlertData))
        self._model.battleAlert = battleAlertData

    @staticmethod
    def _checkOnTimer(data, resDict):
        if data.timer > 0:
            resDict['timer'] = data.timer
        else:
            resDict['description'] = data.description
        return resDict

    @staticmethod
    def _checkOnAddValue(data, resDict):
        if data.addValue >= 0:
            resDict['addValue'] = data.addValue
        return resDict

    def dispose(self):
        self._messenger.assignModelView(None)
        self._messenger = None
        self._model = None
        self._avatarPlayer = None
        return