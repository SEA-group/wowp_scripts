# Embedded file name: scripts/client/gui/HUD2/features/resourcePoints/ResourcePointsSource.py
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
import GameModeSettings.ACSettings as SETTINGS

class ResourcePointsSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).resourcePoints
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameMode = self._clientArena.gameMode
        self.__subscribe()
        self._updateMultiply()
        self._model.enemyMaxPoints = int(self.gameMode.arenaTypeData._gameModeSettings.resourcePointsStart)
        self._model.allyMaxPoints = int(self.gameMode.arenaTypeData._gameModeSettings.resourcePointsStart)

    @property
    def gameMode(self):
        """Game mode instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        return self._gameMode

    def __subscribe(self):
        self._gameMode.addEventHandler(AC_EVENTS.RESOURCE_POINTS_UPDATED, self._onUpdateResPoints)
        self._gameMode.addEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorStateChanged)

    def _onSectorStateChanged(self, sectorId, oldState, oldTeamIndex, state, teamIndex, nextStateTimestamp, *args, **kwargs):
        self._updateMultiply()

    def _updateMultiply(self):
        playerSectors = self.gameMode.capturedSectors(self._playerAvatar.teamIndex)
        enemySectors = self.gameMode.capturedSectors(1 - self._playerAvatar.teamIndex)
        self._model.allyMultiply = SETTINGS.ATTRITION_WARFARE_SETTINGS.MULTIPLY[playerSectors]
        self._model.enemyMultiply = SETTINGS.ATTRITION_WARFARE_SETTINGS.MULTIPLY[enemySectors]

    def _onUpdateResPoints(self, totalPoints, killerID, victimID, pointsInc):
        enemyTeamIndex = 1 - self._playerAvatar.teamIndex
        self._model.victimID = int(victimID)
        self._model.killerID = int(killerID)
        self._model.killPoints = int(pointsInc)
        self._model.enemyPoints = max(0, int(totalPoints[enemyTeamIndex]))
        self._model.allyPoints = max(0, int(totalPoints[self._playerAvatar.teamIndex]))

    def __unsubscribe(self):
        self._gameMode.removeEventHandler(AC_EVENTS.RESOURCE_POINTS_UPDATED, self._onUpdateResPoints)
        self._gameMode.removeEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorStateChanged)

    def dispose(self):
        self.__unsubscribe()
        self._playerAvatar = None
        self._clientArena = None
        self._gameMode = None
        self._model = None
        return