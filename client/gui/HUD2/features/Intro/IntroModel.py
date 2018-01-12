# Embedded file name: scripts/client/gui/HUD2/features/Intro/IntroModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, FloatT
from gui.HUD2.features.Intro.IntroSource import IntroSource

class IntroModel(AutoFilledDataModel):
    DATA_SOURCE = IntroSource
    SCHEME = Structure(EndTime=FloatT)