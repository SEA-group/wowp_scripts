# Embedded file name: scripts/client/gui/HUD2/features/Radar/RadarModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, FloatT, StringT, BoolT, DictT
from gui.HUD2.features.Radar.RadarController import RadarController
from gui.HUD2.features.Radar.RadarSource import RadarSource

class RadarModel(AutoFilledDataModel):
    DATA_SOURCE = RadarSource
    CONTROLLER = RadarController
    SCHEME = Structure(radarState=IntT, visibilityDistance=FloatT, radarRadius=FloatT, radarRadiusInformationCoefficient=FloatT, radarScale=FloatT, radarSize=FloatT, radarSizeState=IntT, radarSizeStateMax=IntT, radarZoomInKey=StringT, radarZoomOutKey=StringT, onIncreaseMapKey=StringT, onDecreaseMapKey=StringT, isShowDetectedDefenders=BoolT, isPlayerLocked=BoolT, backgroundMapInfo=DictT)
    source = None