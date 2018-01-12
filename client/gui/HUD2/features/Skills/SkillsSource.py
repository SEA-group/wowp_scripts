# Embedded file name: scripts/client/gui/HUD2/features/Skills/SkillsSource.py
import BigWorld
from Helpers import AvatarHelper
from _skills_data import SkillDB, SKILL_GROUP
from _specializations_data import SpecializationEnum
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class SkillsSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).skills
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._clientArena.onNewAvatarsInfo += self._setupModel
        self._playerAvatar.eUniqueSkillStateChanged += self._eUniqueSkillStateChanged
        self._playerAvatar.eTacticalRespawnEnd += self._onTacticalRespawnEnd
        self._playerAvatar.eTacticalSpectator += self._onTacticalRespawnEnd
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        return

    def _setupModel(self, newInfos):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self.__updateAllSkills()

    def __updateAllSkills(self):
        skills_ids = AvatarHelper.getAvatarSkillsList(self._playerAvatar)
        self._model.skills.clean()
        for id_ in skills_ids:
            skill = SkillDB[id_]
            if skill.crewMemberTypes[0] == SpecializationEnum.PILOT and skill.group == SKILL_GROUP.UNIQUE:
                self._model.skills.append(id=id_, iconPath=getattr(skill, 'icoHudPath', ''), title=getattr(skill, 'name', ''), description=getattr(skill, 'fullDescription', ''), isActive=False)

    def _onTacticalRespawnEnd(self, *args, **kwargs):
        self.__updateAllSkills()

    def _eUniqueSkillStateChanged(self, skill_id, is_active):
        skillStructure = self._model.skills.first(lambda e: e.id.get() == skill_id)
        if skillStructure:
            skillStructure.isActive = is_active

    def dispose(self):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._playerAvatar.eUniqueSkillStateChanged -= self._eUniqueSkillStateChanged
        self._playerAvatar.eTacticalRespawnEnd -= self._onTacticalRespawnEnd
        self._playerAvatar.eTacticalSpectator -= self._onTacticalRespawnEnd
        self._model = None
        self._playerAvatar = None
        self._clientArena = None
        return