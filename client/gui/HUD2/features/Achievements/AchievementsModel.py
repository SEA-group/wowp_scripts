# Embedded file name: scripts/client/gui/HUD2/features/Achievements/AchievementsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, List, IntT, StringT, UnicodeT
from gui.HUD2.features.Achievements.AchievementsDataSource import AchievementsDataSource

class AchievementsModel(AutoFilledDataModel):
    DATA_SOURCE = AchievementsDataSource
    AchievementItem = Structure(id=IntT, iconPath=StringT, title=UnicodeT, description=UnicodeT, direction=StringT, priority=IntT)
    SCHEME = Structure(achievements=List(AchievementItem))