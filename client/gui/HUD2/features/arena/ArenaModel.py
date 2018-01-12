# Embedded file name: scripts/client/gui/HUD2/features/arena/ArenaModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, DictT, StringT, IntT, List
from gui.HUD2.features.arena.ArenaSource import ArenaSource

class ArenaModel(AutoFilledDataModel):
    DATA_SOURCE = ArenaSource
    ArenaSector = Structure(sectorId=StringT, sectorPosX=IntT, sectorPosY=IntT, sectorLineHeight=IntT)
    SCHEME = Structure(bounds=DictT, arenaAllSectors=List(ArenaSector), arenaMapPath=StringT, arenaMapPathF1=StringT, arenaMiniMapPath=StringT, radarPath=StringT, radarOutlandPath=StringT, arenaName=StringT, arenaSecondName=StringT, arenaId=IntT, arenaDescription=StringT, trainingRoomDescription=StringT, gameTypeName=StringT, gameTypeDescription=StringT, battleType=IntT)