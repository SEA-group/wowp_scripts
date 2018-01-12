# Embedded file name: scripts/client/gui/HUD2/features/Sectors/SectorsGameEffectsController.py
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature

class SectorsGameEffectsController(DataController):

    def __init__(self, features):
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)

    @message('sectorsGameEffects.clickOnMap')
    def clickOnMap(self, positionX, positionY):
        LOG_DEBUG('test ping minimap : clickOnMap', positionX, positionY)
        self._playerAvatar.cell.sendMarkerMessage(int(positionX), int(positionY), 0)