# Embedded file name: scripts/client/gui/HUD2/features/Skills/CrewSource.py
import BigWorld
from Helpers import AvatarHelper
from Helpers.CrewHelper import getSkillPenaltyData
from Helpers.i18n import localizePilot
from Helpers.namesHelper import CONTRY_PO_FILE_WRAPPER, FIRST_NAME_MSG_ID, CONTRY_MSG_ID_WRAPPER, LAST_NAME_MSG_ID, RANKS_MSG_ID, CREW_BODY_TYPE_LOCALIZE_PO_INDEX
from SkillsHelper import BASE_SKILL_EXP
from _skills_data import SkillDB
from consts import EXP_KEY
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
import BWLogging
HINT_TAG_COLOR_TYPE_RED = 'red'
HINT_TAG_COLOR_TYPE_YELLOW = 'yellow'
HINT_TAG_COLOR_TYPE_GREEN = 'green'
STATE_MAP = {HINT_TAG_COLOR_TYPE_YELLOW: 0,
 HINT_TAG_COLOR_TYPE_GREEN: 1,
 HINT_TAG_COLOR_TYPE_RED: 2}

class CrewSource(DataSource):

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).crews
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._db = features.require(Feature.DB_LOGIC)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._playerAvatar.ePlaneBattleCrewDataReceived += self._planeBattleCrewDataReceived
        self._playerAvatar.eTacticalRespawnEnd += self._onTacticalRespawnEnd
        import InputMapping
        self._inputProcessor = features.require(Feature.INPUT).commandProcessor
        self._inputProcessor.addListeners(InputMapping.CMD_MINIMAP_SIZE_DEC, self.onDecreaseMap)
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        else:
            self._clientArena.onNewAvatarsInfo += self._setupModel
        return

    def _getCrewData(self):
        planeId = self._playerAvatar.objTypeID
        self._playerAvatar.base.requestPlaneBattleCrewData(planeId)

    def _planeBattleCrewDataReceived(self, crewData):
        self._updateCrewData(crewData)

    def _onTacticalRespawnEnd(self, *args, **kwargs):
        self._getCrewData()

    def onDecreaseMap(self):
        self._getCrewData()

    def _updateCrewData(self, crewData):
        for crewmemberData in crewData:
            specializationID = crewmemberData.specialization
            mainExp = crewmemberData.experience[EXP_KEY.MAIN]
            skills = crewmemberData.skills
            expLeftToMain = BASE_SKILL_EXP - mainExp
            SP = crewmemberData.sp
            experience = crewmemberData.experience[EXP_KEY.ABOVE_MAIN]
            skillValue = crewmemberData.skillValue
            planeSpecializedOn = crewmemberData.planeSpecializedOn
            specializationSkill = crewmemberData.specializationSkill
            penaltyData = getSkillPenaltyData(crewmemberData.currentPlane, mainExp, skills, expLeftToMain, SP, experience, skillValue, planeSpecializedOn, specializationSkill)
            crewMemberStrc = self._model.crews.first(lambda a: a.specialization.get() == specializationID)
            if crewMemberStrc:
                plane = self._db.getAircraftData(crewmemberData.planeSpecializedOn).airplane
                country = plane.country
                bodyTypePO = CREW_BODY_TYPE_LOCALIZE_PO_INDEX[crewmemberData.bodyType]
                crewMemberStrc.firstName = localizePilot(CONTRY_PO_FILE_WRAPPER[country], FIRST_NAME_MSG_ID % (CONTRY_MSG_ID_WRAPPER[country], bodyTypePO, crewmemberData.firstName or 1))
                crewMemberStrc.lastName = localizePilot(CONTRY_PO_FILE_WRAPPER[country], LAST_NAME_MSG_ID % (CONTRY_MSG_ID_WRAPPER[country], bodyTypePO, crewmemberData.lastName or 1))
                crewMemberStrc.ranks = localizePilot(CONTRY_PO_FILE_WRAPPER[country], RANKS_MSG_ID % (CONTRY_MSG_ID_WRAPPER[country], crewmemberData.ranks))
                crewMemberStrc.planeSpecializedID = planeSpecializedOn
                crewMemberStrc.currentPlaneID = crewmemberData.currentPlane
                crewMemberStrc.penaltyPrc = penaltyData['mainSpecLevel'] if penaltyData['mainSpecLevel'] else 0
                crewMemberStrc.propsList.clean()
                for descrData in penaltyData['descriptions']:
                    crewMemberStrc.propsList.append(tagName=descrData['text'], isTooltip=descrData['tooltip'], tagType=STATE_MAP[descrData['color']])

    def _setupModel(self, newInfos):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._getCrewData()
        crewSkills = self._playerAvatar.crewSkills
        for data_ in crewSkills:
            specializationID = data_.specializationID
            crewMemberStrc = self._model.crews.first(lambda a: a.specialization.get() == specializationID)
            if not crewMemberStrc:
                crewMemberStrc = self._model.crews.append(specialization=specializationID, specializationResearchPercent=0)
                for skillIndex, skillData_ in enumerate(data_.skills):
                    id_ = getattr(skillData_, 'key')
                    skill = SkillDB[id_]
                    mainForSpecialization = getattr(skill, 'mainForSpecialization', -1)
                    if mainForSpecialization == -1:
                        crewMemberStrc.skills.appendSilently(id=id_, iconPath=skill.smallIcoPath, title=skill.name)
                    else:
                        crewMemberStrc.specializationResearchPercent = getattr(skillData_, 'value')

                crewMemberStrc.skills.finishAppending()

    def dispose(self):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._playerAvatar.eTacticalRespawnEnd -= self._onTacticalRespawnEnd
        self._playerAvatar.ePlaneBattleCrewDataReceived -= self._planeBattleCrewDataReceived
        self._model = None
        self._playerAvatar = None
        self._logger = None
        self._model = None
        self._db = None
        self._clientArena = None
        return