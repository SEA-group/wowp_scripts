# Embedded file name: scripts/client/gui/HUD2/features/CombatLog/CombatLogSource.py
import BigWorld
import InputMapping
from EntityHelpers import *
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from BWLogging import getLogger
from CombatLogHelper import COMBAT_EVENT_ID, COMBAT_EVENTS_MAP, FilterManager
from CombatLogSettings import COMBAT_LOG_SETTINGS as SETTINGS

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


SELF_DESTROYED = [LOG_DEATH_REASON.TERRAIN,
 LOG_DEATH_REASON.TREES,
 LOG_DEATH_REASON.WATER,
 LOG_DEATH_REASON.AUTOPILOT,
 LOG_DEATH_REASON.SELF_BOMB,
 LOG_DEATH_REASON.SELF_ROCKET]
DESTROYED_BY_NPC = [LOG_DEATH_REASON.ENEMY_MAIN_ARMAMENT, LOG_DEATH_REASON.ENEMY_RAMMING, LOG_DEATH_REASON.GUNNER]

class CombatLogSource(DataSource):

    def __init__(self, features):
        self.regicToExecutionManager()
        self._logger = getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).combatLog
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._economics = features.require(Feature.CLIENT_ECONOMICS)
        self._input = features.require(Feature.INPUT)
        self._processor = self._input.commandProcessor
        self._economics.assignModelView(self)
        self._filterManager = FilterManager()
        self._processor.addListeners(InputMapping.CMD_SHOW_CURSOR, None, None, self.activateCombatLog)
        self._clientArena.onVehicleKilled += self.onAvatarDestroyed
        self._model.planeModelFlag = SETTINGS.flags[SETTINGS.PLANE_MODEL]
        self._model.clanFlag = SETTINGS.flags[SETTINGS.PLAYER_CLAN]
        self._model.isActive = False
        return

    def activateCombatLog(self, value):
        self._model.isActive = bool(value)

    def onAvatarDestroyed(self, killingInfo):
        typeId, victimId, killerId = self.__getCombatData(killingInfo)
        if typeId is not COMBAT_EVENT_ID.UNDEFINED:
            combatEvent = {'typeId': typeId,
             'killerId': killerId,
             'victimId': victimId,
             'points': 0}
            self._model.combatEvent = {}
            self._model.combatEvent = combatEvent
            self._logger.debug('onAvatarDestroyed typeId = {0}, killerID = {1}, victimId = {2}, points = {3}'.format(typeId, killerId, victimId, 0))

    def refresh(self, totalPoints, totalExp, combatEvents):
        """
        @param totalPoints: int
        @param totalExp: int
        @param combatEvents: list()
        look ClientEconomics.onCombatEvents() for parameters of each event
        """
        if not combatEvents:
            return
        else:
            for combatData in combatEvents:
                playerInfo = self._clientArena.getAvatarInfo(BigWorld.player().id)
                killerInfo = self._clientArena.getAvatarInfo(int(combatData['killerId']))
                if not self._filterManager.useFilter(combatData['eventId'], playerInfo, killerInfo):
                    return
                typeId = next((key for key, types in COMBAT_EVENTS_MAP.iteritems() if combatData['eventId'] in types), None)
                if typeId is None:
                    continue
                points = combatData['points'] if SETTINGS.flags[SETTINGS.GAINED_POINTS] else 0
                combatEvent = {'typeId': typeId,
                 'killerId': combatData['killerId'],
                 'victimId': combatData['victimId'],
                 'points': points}
                self._model.combatEvent = {}
                self._model.combatEvent = combatEvent
                self._logger.debug('refresh typeId = {0}, killerID = {1}, victimId = {2}, points = {3}'.format(typeId, combatData['killerId'], combatData['victimId'], points))

            return

    def __getCombatData(self, killingInfo):
        deathReason = killingInfo.get('deathReason')
        victimId = killingInfo.get('victimID')
        killerId = killingInfo.get('killerID')
        killerInfo = self._clientArena.getAvatarInfo(killerId)
        killerIsNPC = False
        if killerInfo is not None:
            killerIsNPC = killerInfo['isNPC']
        typeId = COMBAT_EVENT_ID.UNDEFINED
        if deathReason in SELF_DESTROYED:
            if not killerIsNPC or SETTINGS.flags[SETTINGS.KILL_DEFENDER]:
                typeId = COMBAT_EVENT_ID.DESTRUCTION
        elif killerIsNPC and deathReason in DESTROYED_BY_NPC:
            if not victimId == killerId:
                typeId = COMBAT_EVENT_ID.KILL
        elif deathReason is LOG_DEATH_REASON.TURRET:
            typeId = COMBAT_EVENT_ID.TURRET
            killerId = victimId
        return (typeId, victimId, killerId)

    def dispose(self):
        self._clientArena.onVehicleKilled -= self.onAvatarDestroyed
        self.unregicFromExecutionManager()
        self._model = None
        self._playerAvatar = None
        self._gameEnvironment = None
        self._clientArena = None
        self._economics = None
        self._input = None
        self._processor = None
        return