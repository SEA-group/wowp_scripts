# Embedded file name: scripts/client/gui/HUD2/features/arena/ArenaSource.py
import BigWorld
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class ArenaSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).arena
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        arenaData = self._clientArena.arenaData
        if arenaData:
            self._onApplyArenaData(arenaData)
        else:
            self._clientArena.onApplyArenaData += self._onApplyArenaData

    def _onApplyArenaData(self, arenaData):
        self._model.bounds = self._makeBoundsObject(arenaData['bounds'])
        from db.DBLogic import g_instance as db
        self._arenaTypeData = db.getArenaData(BigWorld.player().arenaType)
        self._model.arenaName = self._arenaTypeData.name
        self._model.arenaSecondName = self._arenaTypeData.secondName
        self._model.arenaId = BigWorld.player().arenaType
        self._model.arenaDescription = self._arenaTypeData.description
        self._model.trainingRoomDescription = self._arenaTypeData.trainingRoomDescription
        gameType = self._arenaTypeData.gameType.upper()
        self._model.gameTypeName = 'HUD_GAME_TYPE_NAME_' + gameType
        self._model.gameTypeDescription = 'HUD_GAME_TYPE_DESCRIPTION_' + gameType
        self._model.battleType = self._clientArena.battleType
        self._setSectorsData()

    def _makeBoundsObject(self, bounds):
        left = 0
        right = 0
        top = 0
        bottom = 0
        for point in bounds:
            left = min(left, point.x)
            right = max(right, point.x)
            top = min(top, point.z)
            bottom = max(bottom, point.z)

        return {'left': left,
         'right': right,
         'top': top,
         'bottom': bottom}

    def _setSectorsData(self):
        self._model.arenaMapPath = self._arenaTypeData.hudSector.mapPath
        self._model.arenaMiniMapPath = self._arenaTypeData.hudSector.arenaMiniMapPath
        self._model.radarPath = self._arenaTypeData.hudSector.radarPath
        self._model.radarOutlandPath = self._arenaTypeData.hudSector.radarOutlandPath
        self._model.arenaMapPathF1 = self._arenaTypeData.hudSector.mapPathF1
        for sectorData in self._arenaTypeData.hudSector.sectors:
            self._addSectorInfo(sectorData)

    def _addSectorInfo(self, sectorData):
        LOG_DEBUG('ARENA : _addSectorInfo ', vars(sectorData))
        self._model.arenaAllSectors.append(sectorId=sectorData.id, sectorPosX=sectorData.posX, sectorPosY=sectorData.posY, sectorLineHeight=int(sectorData.lineHeight))

    def dispose(self):
        self._model = None
        return