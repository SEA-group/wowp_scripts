# Embedded file name: scripts/client/gui/HUD2/features/PlaneData/BasePlaneDataSource.py
from gui.HUD2.core.DataPrims import DataSource
from Helpers.i18n import localizeAirplane
from clientConsts import PLANE_TYPE_ICO_PATH
from consts import PLANE_CLASS
from debug_utils import LOG_DEBUG
from gui.HUD2.hudFeatures import Feature

class BasePlaneDataSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).planes
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._db = features.require(Feature.DB_LOGIC)
        self._gameEnvironment.eGetHudPlaneData += self._requestPlaneData

    def _requestPlaneData(self, planeID):
        data = self._db.getAircraftData(planeID).airplane
        isPremium = self._db.isPlanePremium(planeID)
        isElite = planeID in self._playerAvatar.elitePlanes
        planeStatus = PLANE_CLASS.PREMIUM if isPremium else isElite * PLANE_CLASS.ELITE or PLANE_CLASS.REGULAR
        self._model.planes.append(planeID=planeID, planeNameShort=localizeAirplane(data.name), planeLevel=data.level, prevIconPath=data.iconPath, planeType=data.planeType, nation=self._db.getNationIDbyName(data.country), planeStatus=planeStatus, typeIconPath=PLANE_TYPE_ICO_PATH.iconHud(data.planeType, planeStatus))
        LOG_DEBUG(' TEST PLANE DATA:  _requestPlaneData: ', planeID, localizeAirplane(data.name))

    def dispose(self):
        self._gameEnvironment.eGetHudPlaneData -= self._requestPlaneData
        self._model = None
        self._gameEnvironment = None
        self._db = None
        return