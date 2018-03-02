# Embedded file name: scripts/client/gui/HUD2/features/resourcePoints/ResourcePointsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, StringT, IntT, FloatT
from gui.HUD2.features.resourcePoints.ResourcePointsSource import ResourcePointsSource

class ResourcePointsModel(AutoFilledDataModel):
    DATA_SOURCE = ResourcePointsSource
    SCHEME = Structure(victimID=IntT, killerID=IntT, killPoints=IntT, enemyPoints=IntT, allyPoints=IntT, enemyMaxPoints=IntT, allyMaxPoints=IntT, allyMultiply=FloatT, enemyMultiply=FloatT)