# Embedded file name: scripts/client/gui/HUD2/features/planeCharacteristics/PlaneCharacteristicsSource.py
import BWLogging
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from performanceCharacteristics import getPerformanceSpecs

class PlaneCharacteristicsSource(DataSource):

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).planeCharacteristics
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameEnvironment.eGetPlanesCharacteristics += self.__onGetPlanesCharacteristics
        self._playerAvatar.eTacticalRespawnEnd += self._onTacticalRespawnEnd

    def __onGetPlanesCharacteristics(self, planesList):
        for id in planesList:
            charStruct = self._model.planes.first(lambda e: e.id.get() == int(id))
            if not charStruct:
                avatarInfo = self._clientArena.getAvatarInfo(int(id))
                if not avatarInfo:
                    self._logger.debug("onGetPlanes : not avatar info= '{0}'".format(id))
                    continue
                hp = avatarInfo.get('planeHp', 0)
                dps = avatarInfo.get('planeDps', 0)
                speed = avatarInfo.get('planeSpeed', 0)
                maneuverability = avatarInfo.get('planeManeuverability', 0)
                altitude = avatarInfo.get('planeAltitude', 0)
                self._model.planes.append(id=int(id), hp=int(round(hp)), dps=int(round(dps)), speed=int(round(speed)), maneuverability=int(round(maneuverability)), altitude=int(round(altitude)))

    def _onTacticalRespawnEnd(self, *args, **kwargs):
        self._updatePlaneChar()

    def _updatePlaneChar(self):
        id = self._playerAvatar.id
        charStruct = self._model.planes.first(lambda e: e.id.get() == int(id))
        self._logger.debug("_updatePlaneChar : avatarId= '{0}'".format(id))
        if charStruct:
            self._logger.debug("_updatePlaneChar 2: avatarId= '{0}'".format(id))
            avatarInfo = self._clientArena.getAvatarInfo(int(id))
            hp = avatarInfo.get('planeHp', 0)
            dps = avatarInfo.get('planeDps', 0)
            speed = avatarInfo.get('planeSpeed', 0)
            maneuverability = avatarInfo.get('planeManeuverability', 0)
            altitude = avatarInfo.get('planeAltitude', 0)
            charStruct.hp = int(round(hp))
            charStruct.dps = int(round(dps))
            charStruct.speed = int(round(speed))
            charStruct.maneuverability = int(round(maneuverability))
            charStruct.altitude = int(round(altitude))
            self._logger.debug("_updateStruct : hp= '{0}'".format(hp))

    def dispose(self):
        self._gameEnvironment.eGetPlanesCharacteristics -= self.__onGetPlanesCharacteristics
        self._playerAvatar.eTacticalRespawnEnd -= self._onTacticalRespawnEnd
        self._gameEnvironment = None
        self._model = None
        self._playerAvatar = None
        return