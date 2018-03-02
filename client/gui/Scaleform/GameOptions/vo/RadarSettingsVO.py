# Embedded file name: scripts/client/gui/Scaleform/GameOptions/vo/RadarSettingsVO.py
from gui.Scaleform.GameOptions.utils import ArrayIndex

class RadarSettingsVO:

    def __init__(self):
        self.isLazy = False
        self.radarState = ArrayIndex()
        self.radarSize = ArrayIndex()
        self.radarLockRotation = ArrayIndex()
        self.showDefendersActive = True