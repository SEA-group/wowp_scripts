# Embedded file name: scripts/client/gui/HUD2/features/Respawn/RespawnController.py
import BigWorld
import BWLogging
import InputMapping
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.hudFeatures import Feature
from gui.HUD2.core.MessageRouter import message

class RespawnController(DataController):

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).respawn
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameMode = self._clientArena.gameMode
        self._inputProcessor = features.require(Feature.INPUT).commandProcessor
        self._inputProcessor.addListeners(InputMapping.CMD_GO_TO_BATTLE, self._eGoToBattle)

    def _eGoToBattle(self):
        endTime = int(round(BigWorld.serverTime() - self._playerAvatar.arenaStartTime))
        timeToRespawnPossibility = self._model.timeToRespawnPossibility.get()
        if endTime >= timeToRespawnPossibility:
            self.gotoBattle()

    @message('respawn.gotoBattle')
    def gotoBattle(self):
        self._playerAvatar.cell.requestRespawn(self._model.spawnSectorID.get())
        LOG_DEBUG(' respawn.requestRespawn ', self._model.spawnSectorID.get())

    @message('respawn.changeVehicle')
    def changeVehicle(self):
        self._playerAvatar.switchObservee()

    @message('respawn.selectPlane')
    def selectPlane(self, planeID):
        self._model.selectedPlaneID = int(planeID)
        LOG_DEBUG(' respawn.selectPlane ', planeID)
        self._playerAvatar.cell.selectPlaneToRespawn(int(planeID))

    @message('respawn.selectSector')
    def selectSector(self, sectorID):
        self._model.spawnSectorID = str(sectorID)
        self._playerAvatar.cell.selectSpawnSector(str(sectorID))
        LOG_DEBUG(' respawn.selectSector ', self._model.spawnSectorID.get())

    @message('respawn.requestPlaneBattleTooltipData')
    def requestPlaneBattleTooltipData(self, planeID):
        self._playerAvatar.base.requestPlaneBattleTooltipData(int(planeID))
        self._logger.debug("requestPlaneBattleTooltipData: needPlaneId = '{0}'".format(planeID))

    @property
    def gameMode(self):
        """Game mode instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        return self._gameMode