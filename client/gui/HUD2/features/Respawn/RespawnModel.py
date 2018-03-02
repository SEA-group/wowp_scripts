# Embedded file name: scripts/client/gui/HUD2/features/Respawn/RespawnModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import IntT, Structure, BoolT, StringT, List, UnicodeT, DictT, FloatT
from gui.HUD2.features.Respawn.RespawnController import RespawnController
from gui.HUD2.features.Respawn.RespawnSource import RespawnSource

class RespawnModel(AutoFilledDataModel):
    DATA_SOURCE = RespawnSource
    CONTROLLER = RespawnController
    Skill = Structure(id=IntT, iconPath=StringT, isActive=BoolT, title=StringT, description=StringT)
    Equipment = Structure(id=IntT, iconPath=StringT)
    Consumable = Structure(id=IntT, iconPath=StringT, isActive=BoolT, amount=IntT, key=StringT, respawnEndTime=IntT, respawnStartTime=IntT, activeEndTime=IntT, isAuto=BoolT, isEmpty=BoolT, status=IntT)
    Crew = Structure(specialization=IntT, specializationResearchPercent=IntT, skills=List(Skill))
    AmmoBelt = Structure(id=IntT, iconPath=StringT, status=IntT, count=IntT, caliber=FloatT)
    Ammunition = Structure(id=IntT, iconPath=StringT, ammoName=StringT, amount=IntT, cluster=IntT, amountMax=IntT, key=StringT, componentType=IntT, cooldownEndTime=IntT, cooldownStartTime=IntT, isAvailable=BoolT, isInstalled=BoolT)
    RespawnPlaneData = Structure(planeID=IntT, planeNameShort=UnicodeT, planeLevel=IntT, iconPath=StringT, planeType=IntT, nation=IntT, planeStatus=IntT, isPrimary=BoolT, typeIconPath=StringT, crews=List(Crew), consumables=List(Consumable), equipments=List(Equipment), ammunitions=List(Ammunition), ammoBelts=List(AmmoBelt))
    SCHEME = Structure(timeToRespawnPossibility=IntT, timeToAutoRespawn=IntT, respawnAmount=IntT, deathTime=IntT, respawnUnlimited=BoolT, respawnIsAvailableBySector=BoolT, selectedPlaneID=IntT, spawnSectorID=StringT, planes=List(RespawnPlaneData), changeRespawnTimeData=DictT, allyResp=IntT, enemyResp=IntT, availablePlaneTypes=DictT)