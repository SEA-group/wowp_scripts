# Embedded file name: scripts/client/gui/HUD2/features/measurement/MeasurementModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, FloatT
from gui.HUD2.features.measurement.MeasurementSource import MeasurementSource

class MeasurementModel(AutoFilledDataModel):
    DATA_SOURCE = MeasurementSource
    SCHEME = Structure(measurementSystem=IntT, SI_TO_IMPERIAL_METER=FloatT, SI_TO_IMPERIAL_KMH=FloatT, WORLD_SCALING=FloatT)