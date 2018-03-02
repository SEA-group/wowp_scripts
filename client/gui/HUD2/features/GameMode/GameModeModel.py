# Embedded file name: scripts/client/gui/HUD2/features/GameMode/GameModeModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import IntT, FloatT, StringT, BoolT, List, Structure, DictT
from gui.HUD2.features.GameMode.GameModeSource import GameModeSource
from gui.HUD2.features.GameMode.OffenseDefenceUiSettingsModel import OffenseDefenceUiSettingsModel
from gui.HUD2.features.Sectors.CurrentSectorModel import CurrentSectorModel
from gui.HUD2.features.Sectors.SectorsGameEffectsModel import SectorsGameEffectsModel

class GameModeModel(AutoFilledDataModel):
    DATA_SOURCE = GameModeSource
    PlaneEffectiveness = Structure(planeType=IntT, effectiveness=IntT)
    Sector = Structure(entityID=IntT, entityPosition=DictT, description=StringT, sectorID=StringT, radius=FloatT, maxPoints=IntT, currentPoints=IntT, isAttack=IntT, teamIndex=IntT, pointsInTick=IntT, sectorTypeIconPath=StringT, featuresIconPath=StringT, miniMapSectorIconPath=StringT, miniMapFeaturesIconPath=StringT, sectorName=StringT, featureName=StringT, lockEndTime=IntT, bonusEndTime=IntT, playerSpawnEnabled=BoolT, gameplayType=StringT, isNeedToShowTimer=BoolT, sectorItems=DictT, descriptionList=DictT, planeEffectiveness=List(PlaneEffectiveness), zOrder=IntT, isPermanentLock=BoolT, isBig=BoolT, isMulticolorInPermanentLockState=BoolT, isFeatureDisable=BoolT)
    Base = Structure(entityID=IntT, sectorID=StringT, sectorName=StringT, radius=FloatT, teamIndex=IntT, gameplayType=StringT, descriptionList=DictT)
    SCHEME = Structure(globalScoreAlly=IntT, tickScoreAlly=IntT, globalScoreEnemy=IntT, tickScoreEnemy=IntT, tickTime=IntT, pointsToWin=IntT, isAllSectorsCapture=BoolT, sectors=List(Sector), sectorsGameEffects=SectorsGameEffectsModel, bases=List(Base), currentSector=CurrentSectorModel, offenseDefenceUiSettings=OffenseDefenceUiSettingsModel)