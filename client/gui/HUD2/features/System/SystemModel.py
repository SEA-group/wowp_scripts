# Embedded file name: scripts/client/gui/HUD2/features/System/SystemModel.py
from gui.HUD2.core.DataModel import DataModel, FloatT, IntT, Structure

class SystemModel(DataModel):
    SCHEME = Structure(FPS=IntT, Ping=IntT, PacketLost=IntT)