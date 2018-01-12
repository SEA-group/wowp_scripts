# Embedded file name: scripts/client/gui/HUD2/features/Entities/TempVisibleObjectsSource.py
import BigWorld
from EntityHelpers import EntitySupportedClasses
from debug_utils import LOG_DEBUG
from gui.HUD2.hudFeatures import Feature

class TempVisibleObjectsSource:

    def __init__(self, model, features):
        self._model = model
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._gameEnvironment.eTemporaryVisibleObjectsUpdate += self._onUpdateSharedData
        self._sharedData = BigWorld.RoutesSharedData('TemporaryVisibleObjects')

    def _onUpdateSharedData(self, obj):
        """Update shared Temporary Visible objects data
        :param obj: MapEntry object (look at AlwaysVisibleObjects.updateTemporaryVisibleObjectData(...)
        """
        objID = obj.id
        if not EntitySupportedClasses.isAvatarClassID(obj.classID) or objID == BigWorld.player().id:
            return
        if self._sharedData.isTVObjectShared(objID):
            if obj.isClientInAOI or not obj.isAlive:
                self._sharedData.removeTVObject(objID)
                self._model.removeTVObject = -1
                self._model.removeTVObject = objID
            else:
                self._sharedData.shareTVObjectData(objID, obj.position, obj.yaw)
        elif not obj.isClientInAOI and obj.isAlive:
            self._sharedData.shareTVObjectData(objID, obj.position, obj.yaw)
            self._model.addTVObject = -1
            self._model.addTVObject = objID

    def isAbovePlayer(self, obj):
        return obj.position.y > self._player.position.y

    def _makePos(self, position):
        return {'x': position.x,
         'y': position.z}

    def dispose(self):
        self._gameEnvironment.eTemporaryVisibleObjectsUpdate -= self._onUpdateSharedData
        self._sharedData = None
        return