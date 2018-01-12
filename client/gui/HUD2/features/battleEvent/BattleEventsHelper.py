# Embedded file name: scripts/client/gui/HUD2/features/battleEvent/BattleEventsHelper.py
from os.path import basename, splitext
from Helpers.i18n import localizeLobby, localizeTooltips
from clientConsts import PREBATTLE_PLANE_TYPE_NAME
from consts import PLANE_TYPE
from clientEconomics.EconomicsModelView import EconomicsModelView
from GameEvents.features.achievements.model import AchievementModel
from GameEvents.features.quests.model import QuestModel
from GameEvents.features.coach.model import RankModel
planeTypeToPath = {PLANE_TYPE.FIGHTER: 'fighter',
 PLANE_TYPE.HFIGHTER: 'heavy',
 PLANE_TYPE.NAVY: 'multi',
 PLANE_TYPE.BOMBER: 'bomber',
 PLANE_TYPE.ASSAULT: 'attack'}

def createQuestCompletedEventModel(questID):
    qst = QuestModel.get(id=questID)
    isFull = True
    if qst.parent:
        isFull = False
        qst = QuestModel.get(id=qst.parent)
    return {'type': EconomicsModelView.COMPOSITE_EVENT_TYPE,
     'title': qst.client.name.locale,
     'isFull': isFull}


def createAchievementUnlockedEventModel(achievementID):
    achv = AchievementModel.get(id=achievementID)
    return {'type': EconomicsModelView.AWARD_EVENT_TYPE,
     'title': achv.client.name.locale,
     'icon': achv.client.icon.small}


def createRankGainedEventModel(rankID):
    rankModel = RankModel.getRankByID(rankID)
    planeType = rankModel.relatedPlaneType
    iconPathTemplate = rankModel.iconPath
    templateData = {'type': 'achievements',
     'class': planeTypeToPath[planeType],
     'state': 'normal',
     'size': '72x88'}
    iconPath = iconPathTemplate.format(**templateData)
    titleTemplate = localizeTooltips(rankModel.title)
    localizedPlaneTypeName = localizeLobby(PREBATTLE_PLANE_TYPE_NAME[planeType])
    return {'type': EconomicsModelView.AWARD_EVENT_TYPE,
     'title': titleTemplate.format(class_name=localizedPlaneTypeName),
     'icon': iconPath}


def extractFileName(path):
    return splitext(basename(path))[0]