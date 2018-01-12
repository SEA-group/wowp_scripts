# Embedded file name: scripts/client/gui/HUD2/features/Sectors/CurretntSectorSource.py
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class CurrentSectorSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).domination.currentSector
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameMode = self._clientArena.gameMode
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._playerAvatar.eCurrentSectorChanged += self._onChangeSector
        self._gameMode.addEventHandler(AC_EVENTS.SECTOR_ACTION, self._onSectorAction)

    @property
    def gameMode(self):
        """Game mode instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        return self._gameMode

    def _onSectorAction(self, sectorId, teamIndex, settings):
        sectorID = self._model.sectorID.get()
        if sectorId == sectorID and settings['points'] != 0:
            sectorData = {}
            sectorData['title'] = settings['hudLocalId']
            sectorData['value'] = settings['points']
            sectorData['teamIndex'] = teamIndex
            self._model.sectorLog = sectorData
            LOG_DEBUG(' SECTORS _onChangeSectorEvent ', sectorData)

    def _onChangeSector(self, avatar, oldSector, newSector):
        self._model.sectorID = newSector
        LOG_DEBUG(' SECTORS _onChangeSector: ', newSector)

    def dispose(self):
        self._playerAvatar.eCurrentSectorChanged -= self._onChangeSector
        self._gameMode.removeEventHandler(AC_EVENTS.SECTOR_ACTION, self._onSectorAction)
        self._gameMode = None
        self._playerAvatar = None
        self._model = None
        return