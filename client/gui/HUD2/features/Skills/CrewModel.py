# Embedded file name: scripts/client/gui/HUD2/features/Skills/CrewModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, StringT, BoolT, List, UnicodeT
from gui.HUD2.features.Skills.CrewSource import CrewSource

class CrewModel(AutoFilledDataModel):
    DATA_SOURCE = CrewSource
    PenaltyData = Structure(tagName=StringT, tagType=IntT, isTooltip=BoolT)
    Skill = Structure(id=IntT, iconPath=StringT, isActive=BoolT, title=StringT, description=StringT)
    Crew = Structure(specialization=IntT, specializationResearchPercent=IntT, skills=List(Skill), firstName=UnicodeT, lastName=UnicodeT, ranks=UnicodeT, planeSpecializedID=IntT, currentPlaneID=IntT, skillPenaltyPrc=IntT, penaltyPrc=IntT, propsList=List(PenaltyData))
    SCHEME = Structure(crews=List(Crew))