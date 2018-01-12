# Embedded file name: scripts/client/gui/HUD2/features/Outro/OutroModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, StringT, IntT, UnicodeT, List
from gui.HUD2.features.Outro.OutroSource import OutroSource

class OutroModel(AutoFilledDataModel):
    DATA_SOURCE = OutroSource
    ObjectiveItem = Structure(id=IntT, title=StringT, description=StringT, maxProgress=IntT, progress=IntT, value=IntT, requiredValue=IntT)
    SCHEME = Structure(winnerTeamIndex=IntT, reason=StringT, goToHangarTime=IntT, battleTime=IntT, allyPoints=IntT, enemyPoints=IntT, battlePoints=IntT, masteryPoints=IntT, playerLevel=IntT, bestPlane=UnicodeT, bestClass=UnicodeT, bestPlaneType=IntT, bestRank=IntT, bestTasks=List(ObjectiveItem))