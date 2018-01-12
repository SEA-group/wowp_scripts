# Embedded file name: scripts/client/gui/HUD2/features/planeCharacteristics/PlaneCharacteristicsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, List
from gui.HUD2.features.planeCharacteristics.PlaneCharacteristicsController import PlaneCharacteristicsController
from gui.HUD2.features.planeCharacteristics.PlaneCharacteristicsSource import PlaneCharacteristicsSource

class PlaneCharacteristicsModel(AutoFilledDataModel):
    DATA_SOURCE = PlaneCharacteristicsSource
    CONTROLLER = PlaneCharacteristicsController
    Characteristic = Structure(id=IntT, hp=IntT, dps=IntT, speed=IntT, maneuverability=IntT, altitude=IntT)
    SCHEME = Structure(planes=List(Characteristic))