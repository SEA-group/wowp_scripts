# Embedded file name: scripts/client/gui/HUD2/features/Spectator/SpectatorModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT
from gui.HUD2.features.Spectator.SpectatorController import SpectatorController
from gui.HUD2.features.Spectator.SpectatorSource import SpectatorSource

class SpectatorModel(AutoFilledDataModel):
    DATA_SOURCE = SpectatorSource
    CONTROLLER = SpectatorController
    SCHEME = Structure(selectedPlayerId=IntT)