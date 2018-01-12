# Embedded file name: scripts/client/gui/HUD2/features/SectorItems/SectorItemsSource.py
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class SectorItemsSource(DataSource):

    def __init__(self, features):
        self._LOG_TAG = '  SECTOR_OBJECTS : '
        self._model = features.require(Feature.GAME_MODEL).sectorItems
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._dbLogic = features.require(Feature.DB_LOGIC)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameMode = self._clientArena.gameMode
        self._clientArena.onNewAvatarsInfo += self._setupModel
        if self._clientArena.isAllServerDataReceived:
            self._setupModel(None)
        return

    def _setupModel(self, newInfos):
        self.itemsDict = self._dbLogic.getACHudHints().getSectorItemsDict
        for key in self.itemsDict:
            self._addItems(self.itemsDict[key])

    def _getItemsById(self, id):
        if id in self.itemsDict:
            return self.itemsDict[id]
        else:
            return None

    def _addItems(self, sectorItemData):
        if sectorItemData:
            LOG_DEBUG(self._LOG_TAG, 'sectorItemData ', vars(sectorItemData))
            self._model.sectorItems.append(id=sectorItemData.id, nameLocalID=sectorItemData.nameLocalID, itemType=sectorItemData.typeLocalID, iconPath=sectorItemData.iconPath)

    def dispose(self):
        self._model = None
        self._gameMode = None
        self._dbLogic = None
        self._playerAvatar = None
        return