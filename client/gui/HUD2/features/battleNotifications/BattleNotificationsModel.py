# Embedded file name: scripts/client/gui/HUD2/features/battleNotifications/BattleNotificationsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, DictT, StringT
from gui.HUD2.features.battleNotifications.BattleNotificationsSource import BattleNotificationsSource

class BattleNotificationsModel(AutoFilledDataModel):
    DATA_SOURCE = BattleNotificationsSource
    SCHEME = Structure(battleNotification=DictT)