# Embedded file name: scripts/client/gui/HUD2/features/Radar/RadarSource.py
import BigWorld
import InputMapping
from consts import WORLD_SCALING
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from gui.Scaleform.UIHelper import getKeyLocalization
SIZE_S = 0
SIZE_M = 1
SIZE_L = 2
RADAR_SIZE = {SIZE_S: 0.667,
 SIZE_M: 0.834,
 SIZE_L: 1.0}

class RadarSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).radar
        self._model.source = self
        self._db = features.require(Feature.DB_LOGIC)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._inputProcessor = features.require(Feature.INPUT).commandProcessor
        self._dbLogic = features.require(Feature.DB_LOGIC)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._inputProcessor.addListeners(InputMapping.CMD_RADAR_ZOOM_IN, self.radarZoomIn)
        self._inputProcessor.addListeners(InputMapping.CMD_RADAR_ZOOM_OUT, self.radarZoomOut)
        self._inputProcessor.addListeners(InputMapping.CMD_MINIMAP_SIZE_INC, self.onIncreaseMap)
        self._inputProcessor.addListeners(InputMapping.CMD_MINIMAP_SIZE_DEC, self.onDecreaseMap)
        self._uiSettings = features.require(Feature.UI_SETTINGS)
        from db.DBLogic import g_instance as db
        self._arenaTypeData = db.getArenaData(BigWorld.player().arenaType)
        self._uiSettings.eShowDefendersChanged += self._updateShowDefenders
        self._uiSettings.eRadarLockChanged += self._updateRadarLock
        self._uiSettings.eRadarSizeChanged += self._updateRadarSize
        self._uiSettings.eRadarStateChanged += self._updateRadarState
        self._playerAvatar.eTacticalRespawnEnd += self._fillPlaneData
        self._planeLevel = 1
        self._fillRadar()
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        else:
            self._clientArena.onNewAvatarsInfo += self._setupModel
        return

    def _setupModel(self, newInfos):
        self._fillPlaneData()
        self._model.radarZoomInKey = getKeyLocalization(InputMapping.CMD_RADAR_ZOOM_IN)
        self._model.radarZoomOutKey = getKeyLocalization(InputMapping.CMD_RADAR_ZOOM_OUT)
        self._model.onIncreaseMapKey = getKeyLocalization(InputMapping.CMD_MINIMAP_SIZE_INC)
        self._model.onDecreaseMapKey = getKeyLocalization(InputMapping.CMD_MINIMAP_SIZE_DEC)

    def _fillPlaneData(self, *args, **kwargs):
        avatarInfo = self._clientArena.getAvatarInfo(self._playerAvatar.id)
        self._settings = avatarInfo['settings']
        self._planeLevel = self._settings.airplane.level
        self._fillRadarByState()
        self._fillRadarSize()
        self._model.radarSizeStateMax = -1

    def _fillRadar(self):
        self._radarState = 0
        self._radarSizeState = 0
        self._radarSizeState = self._uiSettings.gameUI['radarSize']
        self._radarState = self._uiSettings.gameUI['radarState']
        isRadarLockRotation = bool(self._uiSettings.gameUI['radarLockRotation'])
        self._model.isPlayerLocked = not isRadarLockRotation
        self._model.isShowDetectedDefenders = self._uiSettings.gameUI['showDefendersActive']
        mapData = self._arenaTypeData.hudSector.mapInfo
        mapInfoData = {}
        mapInfoData['posX'] = mapData.posX
        mapInfoData['posY'] = mapData.posY
        mapInfoData['width'] = mapData.mapWidth
        mapInfoData['height'] = mapData.mapHeight
        self._model.backgroundMapInfo = mapInfoData
        self._model.arenaMiniMapPath = self._arenaTypeData.hudSector.arenaMiniMapPath
        self._model.radarPath = self._arenaTypeData.hudSector.radarPath

    def _fillRadarSize(self):
        self._model.radarSizeState = self._radarSizeState
        self._uiSettings.radarSize = self._radarSizeState

    def _fillRadarByState(self):
        radarSettings = self._dbLogic.getACRadarSettings().getSettingsByLevel(self._radarState, self._planeLevel)
        self._updateVisibilityDistance(radarSettings)
        self._model.radarState = self._radarState
        self._model.radarRadius = radarSettings.radius * WORLD_SCALING
        self._model.radarRadiusInformationCoefficient = radarSettings.selectTargetDistanceKoef * 1.0
        self._uiSettings.radarState = self._radarState

    def _updateVisibilityDistance(self, radarSettings):
        self._model.visibilityDistance = radarSettings.visibilityDistanceKoef * 0.5 * self._planeVision

    def radarZoomIn(self):
        self._changeRadarState(1)

    def radarZoomOut(self):
        self._changeRadarState(-1)

    def onIncreaseMap(self):
        self._changeMinimapSize(1, True)

    def onDecreaseMap(self):
        self._changeMinimapSize(-1, True)

    def onSetMapMaxSize(self, size):
        currentSize = self._radarSizeState
        if self._model.radarSizeStateMax.get() != size:
            self._model.radarSizeStateMax = size
        if size < currentSize:
            self._changeMinimapSize(size - currentSize, False)

    def _changeMinimapSize(self, value, saveToSettings):
        self._radarSizeState += value
        maxSize = self._model.radarSizeStateMax.get()
        if self._radarSizeState > maxSize:
            self._radarSizeState = maxSize
        if self._radarSizeState < 0:
            self._radarSizeState = 0
        if self._model.radarSizeState.get() != self._radarSizeState:
            self._fillRadarSize()
        if saveToSettings:
            self._uiSettings.gameUI['radarSize'] = self._radarSizeState

    def _changeRadarState(self, value):
        self._radarState += value
        if self._radarState > 2:
            self._radarState = 2
        if self._radarState < 0:
            self._radarState = 0
        if self._model.radarState.get() != self._radarState:
            self._fillRadarByState()
        self._uiSettings.gameUI['radarState'] = self._radarState

    def _updateRadarLock(self, *args, **kwargs):
        isRadarLockRotation = bool(self._uiSettings.gameUI['radarLockRotation'])
        self._model.isPlayerLocked = not isRadarLockRotation

    def _updateShowDefenders(self, *args, **kwargs):
        self._model.isShowDetectedDefenders = self._uiSettings.gameUI['showDefendersActive']

    def _updateRadarState(self, *args, **kwargs):
        self._radarState = self._uiSettings.gameUI['radarState']
        radarSettings = self._dbLogic.getACRadarSettings().getSettingsByLevel(self._radarState, self._planeLevel)
        self._updateVisibilityDistance(radarSettings)
        self._model.radarState = self._radarState

    def _updateRadarSize(self, *args, **kwargs):
        self._radarSizeState = self._uiSettings.gameUI['radarSize']
        self._model.radarSizeState = self._radarSizeState

    @property
    def _planeVision(self):
        if self._settings is None:
            avatarInfo = self._clientArena.getAvatarInfo(self._playerAvatar.id)
            self._settings = avatarInfo['settings']
        try:
            value = getattr(self._settings.airplane.flightModel.visibilitySettings, 'PlaneVision')
        except AttributeError:
            planeType = self._settings.airplane.planeType
            visibilitySettings = self._db.getAircraftClassDescription(planeType).visibilitySettings
            classSettings = visibilitySettings.levelVisibility[self._settings.airplane.level - 1]
            value = getattr(classSettings, 'PlaneVision')

        value *= WORLD_SCALING
        return value

    def dispose(self):
        self._playerAvatar.eTacticalRespawnEnd -= self._fillPlaneData
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._uiSettings.eShowDefendersChanged -= self._updateShowDefenders
        self._uiSettings.eRadarLockChanged -= self._updateRadarLock
        self._uiSettings.eRadarSizeChanged -= self._updateRadarSize
        self._uiSettings.eRadarStateChanged -= self._updateRadarState
        self._arenaTypeData = None
        self._db = None
        self._playerAvatar = None
        self._clientArena = None
        self._model = None
        self._uiSettings = None
        return