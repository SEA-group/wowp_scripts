# Embedded file name: scripts/client/gui/HUD2/features/parameters/ParametersModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, FloatT, UnicodeT, IntT, BoolT, List
from gui.HUD2.features.parameters.ParametersSource import ParametersSource

class ParametersModel(AutoFilledDataModel):
    DATA_SOURCE = ParametersSource
    Range = Structure(start=FloatT, end=FloatT)
    SCHEME = Structure(speed=IntT, speedState=IntT, speedMetric=UnicodeT, speedMax=IntT, speedRanges=List(Range), stallSpeed=IntT, altitude=IntT, altitudeState=IntT, altitudeMetric=UnicodeT, altitudeMax=IntT, altitudeRanges=List(Range), force=FloatT, forceMax=FloatT, isForce=BoolT)