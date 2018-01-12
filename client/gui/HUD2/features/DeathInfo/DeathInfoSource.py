# Embedded file name: scripts/client/gui/HUD2/features/DeathInfo/DeathInfoSource.py
import BigWorld
from EntityHelpers import *
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class LOG_DEATH_REASON:
    SURVIVE = 0
    TERRAIN = 1
    TREES = 2
    WATER = 3
    ENEMY_MAIN_ARMAMENT = 4
    ENEMY_BOMB = 5
    ENEMY_ROCKET = 6
    FRIENDLY_MAIN_ARMAMENT = 7
    FRIENDLY_BOMB = 8
    FRIENDLY_ROCKET = 9
    ENEMY_RAMMING = 10
    FRIENDLY_RAMMING = 11
    TURRET = 12
    GUNNER = 13
    AUTOPILOT = 14
    CLIENT_DEATH = 15
    CLIENT_LEAVE = 16
    SELF_BOMB = 17
    SELF_ROCKET = 18
    FIRING = 19
    UNKNOWN = 20
    FAILED_TO_RECONNECT = 21
    FAILED_TO_LOAD = 22
    AC_V2_ROCKET_EXPLOSION = 23
    AC_SECTOR_CAPTURE_SUICIDE = 24
    DEFENDER = 25
    BOMBER = 26


class HUD_DEATH_REASON:
    ENEMY_MAIN_ARMAMENT = 1
    GUNNER = 2
    ENEMY_BOMB = 3
    ENEMY_ROCKET = 4
    RAMMING = 5
    TERRAIN = 6
    TURRET = 7
    FIRING = 8
    DEFENDER = 9
    BOMBER = 10


class DeathInfoSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).deathInfo
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._playerAvatar.eReportDestruction += self.eReportDestruction
        self._setDeathReasonMap()

    def _setDeathReasonMap(self):
        self._reasonsDict = {}
        self._reasonsDict[LOG_DEATH_REASON.TERRAIN] = HUD_DEATH_REASON.TERRAIN
        self._reasonsDict[LOG_DEATH_REASON.TREES] = HUD_DEATH_REASON.TERRAIN
        self._reasonsDict[LOG_DEATH_REASON.WATER] = HUD_DEATH_REASON.TERRAIN
        self._reasonsDict[LOG_DEATH_REASON.ENEMY_MAIN_ARMAMENT] = HUD_DEATH_REASON.ENEMY_MAIN_ARMAMENT
        self._reasonsDict[LOG_DEATH_REASON.ENEMY_BOMB] = HUD_DEATH_REASON.ENEMY_BOMB
        self._reasonsDict[LOG_DEATH_REASON.ENEMY_ROCKET] = HUD_DEATH_REASON.ENEMY_ROCKET
        self._reasonsDict[LOG_DEATH_REASON.ENEMY_RAMMING] = HUD_DEATH_REASON.RAMMING
        self._reasonsDict[LOG_DEATH_REASON.FRIENDLY_RAMMING] = HUD_DEATH_REASON.RAMMING
        self._reasonsDict[LOG_DEATH_REASON.TURRET] = HUD_DEATH_REASON.TURRET
        self._reasonsDict[LOG_DEATH_REASON.GUNNER] = HUD_DEATH_REASON.GUNNER
        self._reasonsDict[LOG_DEATH_REASON.FIRING] = HUD_DEATH_REASON.FIRING
        self._reasonsDict[LOG_DEATH_REASON.DEFENDER] = HUD_DEATH_REASON.DEFENDER
        self._reasonsDict[LOG_DEATH_REASON.BOMBER] = HUD_DEATH_REASON.BOMBER

    @staticmethod
    def checkNPCType(killerID, deathReason):
        killer = BigWorld.entities.get(killerID)
        if not isAvatarBot(killer):
            return deathReason
        if killer.isDefender and (deathReason == HUD_DEATH_REASON.ENEMY_MAIN_ARMAMENT or deathReason == HUD_DEATH_REASON.RAMMING):
            return HUD_DEATH_REASON.DEFENDER
        if isAirStrikeBomber(killer) and (deathReason == HUD_DEATH_REASON.GUNNER or deathReason == HUD_DEATH_REASON.RAMMING):
            return HUD_DEATH_REASON.BOMBER
        return deathReason

    def eReportDestruction(self, killInfo):
        victimID = killInfo.get('victimID')
        if victimID == self._playerAvatar.id:
            deathReason = self._reasonsDict.get(killInfo.get('deathReason'), HUD_DEATH_REASON.TERRAIN)
            deathReason = self.checkNPCType(killInfo.get('killerID'), deathReason)
            LOG_DEBUG(' killInfo :::', killInfo.get('killerID'), killInfo.get('deathReason'), deathReason)
            self._model.killerID = killInfo.get('killerID')
            self._model.deathReason = deathReason

    def dispose(self):
        self._playerAvatar.eReportDestruction -= self.eReportDestruction
        self._playerAvatar = None
        self._model = None
        return