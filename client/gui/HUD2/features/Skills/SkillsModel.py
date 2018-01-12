# Embedded file name: scripts/client/gui/HUD2/features/Skills/SkillsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, StringT, BoolT, IntT, List
from gui.HUD2.features.Skills.SkillsSource import SkillsSource

class SkillsModel(AutoFilledDataModel):
    DATA_SOURCE = SkillsSource
    Skill = Structure(id=IntT, iconPath=StringT, isActive=BoolT, title=StringT, description=StringT)
    SCHEME = Structure(skills=List(Skill))