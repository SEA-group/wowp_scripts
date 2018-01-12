# Embedded file name: scripts/client/gui/HUD2/features/Entities/EntitiesModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import IntT, List, Structure, BoolT, UnicodeT, FloatT, StringT, DictT
from gui.HUD2.features.Entities.EntitiesSource import EntitiesSource

class EntitiesModel(AutoFilledDataModel):
    DATA_SOURCE = EntitiesSource
    planeScoreData = Structure(planeID=IntT, planeType=IntT, planeName=UnicodeT, battlePoints=IntT, rankID=IntT)
    Avatar = Structure(id=IntT, playerName=UnicodeT, planeGlobalID=IntT, squadIndex=IntT, teamIndex=IntT, previewIconPath=StringT, planeName=UnicodeT, planeType=IntT, planeLevel=IntT, isDefender=BoolT, isBot=BoolT, health=IntT, maxHealth=IntT, isRepair=BoolT, inWorld=BoolT, isLost=BoolT, state=IntT, points=IntT, rankID=IntT, planeScoresData=List(planeScoreData))
    Bomber = Structure(id=IntT, teamIndex=IntT, playerName=UnicodeT, planeName=UnicodeT, health=IntT, maxHealth=IntT, inWorld=BoolT, state=IntT)
    Part = Structure(id=IntT, partType=IntT, isDead=BoolT)
    TeamObject = Structure(id=IntT, position=DictT, parts=List(Part), objectName=UnicodeT, teamIndex=IntT, isAliveOutOfAOI=BoolT, objectType=IntT, featureRadius=FloatT, turretName=StringT, underRocketAttack=BoolT, health=IntT, maxHealth=IntT, inWorld=BoolT, state=IntT)
    TemporaryVisibleObject = Structure(id=IntT, position=DictT, yaw=FloatT, isAbovePlayer=BoolT)
    SCHEME = Structure(avatars=List(Avatar), teamObjects=List(TeamObject), bombers=List(Bomber), tempVisibleObjects=List(TemporaryVisibleObject), addTVObject=IntT, removeTVObject=IntT)