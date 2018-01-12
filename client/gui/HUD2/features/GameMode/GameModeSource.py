# Embedded file name: scripts/client/gui/HUD2/features/GameMode/GameModeSource.py
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from consts import TEAM_ID
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.features.Sectors.SectorSource import SectorSource
from gui.HUD2.hudFeatures import Feature
import math
from debug_utils import *

class GameModeSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).domination
        self._sectorSource = SectorSource(features)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._gameMode = self._clientArena.gameMode
        self._model.pointsToWin = self.gameMode.arenaTypeData._gameModeSettings.pointsToWin
        self._isAllSectorsCapture = False
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        else:
            self._clientArena.onNewAvatarsInfo += self._setupModel
        return

    @property
    def gameMode(self):
        """Game mode instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        return self._gameMode

    def _setupModel(self, newInfos):
        self._subscribe()

    def _subscribe(self):
        self._gameMode.addEventHandler(AC_EVENTS.GLOBAL_SCORE_UPDATED, self._onGlobalScoreUpdate)
        self._gameMode.addEventHandler(AC_EVENTS.GAME_MODE_TICK, self._onGameModeTick)
        self._gameMode.addEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorStateChanged)

    def _onSectorStateChanged(self, sectorId, oldState, oldTeamIndex, state, teamIndex, nextStateTimestamp, *args, **kwargs):
        self._updateGameModeTick()

    def _onGlobalScoreUpdate(self, scoreGlobal, *args, **kwargs):
        enemyTeamIndex = 1 - self._playerAvatar.teamIndex
        self._model.globalScoreAlly = scoreGlobal[self._playerAvatar.teamIndex]
        self._model.globalScoreEnemy = scoreGlobal[enemyTeamIndex]
        isAllSectorsCapture = False
        if self.gameMode.teamSuperiority(TEAM_ID.TEAM_0) or self.gameMode.teamSuperiority(TEAM_ID.TEAM_1):
            isAllSectorsCapture = True
        if self._isAllSectorsCapture != isAllSectorsCapture:
            self._isAllSectorsCapture = isAllSectorsCapture
            self._model.isAllSectorsCapture = self._isAllSectorsCapture

    def _onGameModeTick(self, tickNumber, *args, **kwargs):
        self._updateGameModeTick()

    def _updateGameModeTick(self):
        tick = self.gameMode.currentTick
        enemyTeamIndex = 1 - self._playerAvatar.teamIndex
        score = self.gameMode.getPointsInTick(tick + 1)
        self._model.tickScoreAlly = score[self._playerAvatar.teamIndex]
        self._model.tickScoreEnemy = score[enemyTeamIndex]
        tickTime = BigWorld.serverTime() - BigWorld.player().arenaStartTime + self.gameMode.getTickPeriod()
        self._model.tickTime = int(round(tickTime))

    def dispose(self):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._gameMode.removeEventHandler(AC_EVENTS.GLOBAL_SCORE_UPDATED, self._onGlobalScoreUpdate)
        self._gameMode.removeEventHandler(AC_EVENTS.GAME_MODE_TICK, self._onGameModeTick)
        self._gameMode.removeEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorStateChanged)
        self._clientArena = None
        self._playerAvatar = None
        self._gameMode = None
        self._model = None
        self._sectorSource.dispose()
        self._sectorSource = None
        return