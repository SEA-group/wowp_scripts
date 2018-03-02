# Embedded file name: scripts/client/gui/HUD2/features/GameMode/OffenseDefenceUiSettingsSource.py
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from gui.HUD2.core.DataModel import IntT
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from debug_utils import LOG_DEBUG

class OffenseDefenceUiSettingsSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).domination.offenseDefenceUiSettings
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._gameMode = self._clientArena.gameMode
        self._setData()
        self._subscribe()

    def _setData(self):
        for uiData in self._gameMode.uiSettings:
            self._addData(uiData)

    def _subscribe(self):
        self._gameMode.addEventHandler(AC_EVENTS.SECTOR_PERMANENT_LOCK, self._onSectorpermanentLock)

    def _addData(self, uiData):
        self._model.settings.append(viewTeamIndex=uiData.teamIndex, isShowSetorsView=uiData.isShowSetorsView, isShowDominationView=uiData.isShowDominationView, isShowTeamRespawnsView=uiData.isShowTeamRespawnsView)
        if self._playerAvatar.teamIndex == uiData.teamIndex:
            self._model.title = uiData.title

    def _onSectorpermanentLock(self, sectorID, *args, **kwargs):
        LOG_DEBUG(' OffenseDefenceUiSettingsSource  ::: _onSectorpermanentLock : ', sectorID)

    @property
    def gameMode(self):
        """Game mode instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        return self._gameMode

    def dispose(self):
        self._clientArena = None
        self._playerAvatar = None
        self._gameMode = None
        return