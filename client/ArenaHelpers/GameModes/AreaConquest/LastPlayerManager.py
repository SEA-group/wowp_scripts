# Embedded file name: scripts/client/ArenaHelpers/GameModes/AreaConquest/LastPlayerManager.py
import BigWorld
import GameEnvironment
import GameModeSettings.ACSettings as SETTINGS
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from ArenaHelpers.GameModes.AreaConquest.ACClientArenaHelper import countAliveOrRespawnablePlayersByTeam
from ArenaHelpers.GameModes.AreaConquest.AvatarComponents.TacticalRespawnAvatar import ConditionsBarrier
from EntityHelpers import EntityStates
from Event import EventManager, Event
from consts import TEAM_ID
from debug_utils import LOG_DEBUG

class LOADING_CONDITION:
    GAME_MODE_READY_FLAG = 'game_mode_ready_flag'
    ARENA_READY_FLAG = 'ARENA_READY_FLAG'
    ALL = (GAME_MODE_READY_FLAG, ARENA_READY_FLAG)


class LastPlayerManager(object):

    def __init__(self, gameMode):
        self._gameMode = gameMode
        self._clientArena = GameEnvironment.getClientArena()
        self._eManager = EventManager()
        self.eUpdateLastPlayer = Event(self._eManager)
        self.__disableRespawns = False
        self.__lastPlayerReported = False
        self.__lastEnemyReported = False
        self.__loadingBarrier = ConditionsBarrier(LOADING_CONDITION.ALL, self.__onLoadAllData)
        if self._gameMode.isReady:
            self.__onGameModeReady()
        else:
            self._gameMode.eGameModeReady += self.__onGameModeReady
        if self._clientArena.isAllServerDataReceived():
            self.__onAvatarInfo(None)
        else:
            self._clientArena.onNewAvatarsInfo += self.__onAvatarInfo
        return

    def __onGameModeReady(self, *args, **kwargs):
        self.__loadingBarrier.fireCondition(LOADING_CONDITION.GAME_MODE_READY_FLAG)

    def __onAvatarInfo(self, newInfos):
        self.__loadingBarrier.fireCondition(LOADING_CONDITION.ARENA_READY_FLAG)

    def __onLoadAllData(self):
        self._gameMode.addEventHandler(AC_EVENTS.BATTLE_EVENT, self._onBattleEvent)
        self._clientArena.onVehicleKilled += self.__onVehicleKilled
        self.__checkLastInTeam()

    def __onVehicleKilled(self, *args, **kwargs):
        self.__checkLastInTeam()

    def _onBattleEvent(self, batleEventID):
        if batleEventID == SETTINGS.BATTLE_EVENT_TYPE.RESPAWN_DISABLE:
            self.__disableRespawns = True

    def __checkLastInTeam(self):
        if BigWorld.player().state != EntityStates.GAME_CONTROLLED or not self.__disableRespawns:
            return
        allLastInTeamReported = self.__lastEnemyReported and self.__lastPlayerReported
        if allLastInTeamReported:
            return
        aliveOrRespawnableByTeam = countAliveOrRespawnablePlayersByTeam(self._clientArena)
        allyTeam = BigWorld.player().teamIndex
        enemyTeam = TEAM_ID.TEAM_0 if allyTeam == TEAM_ID.TEAM_1 else TEAM_ID.TEAM_1
        if aliveOrRespawnableByTeam[allyTeam] == 1 and not self.__lastPlayerReported:
            self.__reportLastPlayer()
            self.__lastPlayerReported = True
        if aliveOrRespawnableByTeam[enemyTeam] == 1 and not self.__lastEnemyReported:
            self.__reportLastPlayer(True)
            self.__lastEnemyReported = True

    def __reportLastPlayer(self, isEnemy = False):
        self.eUpdateLastPlayer(isEnemy)

    def destroy(self):
        self._gameMode.removeEventHandler(AC_EVENTS.BATTLE_EVENT, self._onBattleEvent)
        self._gameMode.eGameModeReady -= self.__onGameModeReady
        self._clientArena.onNewAvatarsInfo -= self.__onAvatarInfo
        self._clientArena.onVehicleKilled -= self.__onVehicleKilled
        self._gameMode = None
        self._clientArena = None
        return