# Embedded file name: scripts/client/gui/HUD2/features/PlaneTypeObjectives/PlaneTypeObjectivesModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, List, IntT, StringT
from gui.HUD2.features.PlaneTypeObjectives.PlaneTypeObjectivesDataSource import PlaneTypeObjectivesDataSource

class PlaneTypeObjectivesModel(AutoFilledDataModel):
    DATA_SOURCE = PlaneTypeObjectivesDataSource
    ObjectiveItem = Structure(id=IntT, title=StringT, countDescription=StringT, description=StringT, maxProgress=IntT, progress=IntT, value=IntT, requiredValue=IntT)
    SCHEME = Structure(classTasks=List(ObjectiveItem))