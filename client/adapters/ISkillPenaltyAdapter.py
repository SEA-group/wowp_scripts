# Embedded file name: scripts/client/adapters/ISkillPenaltyAdapter.py
from DefaultAdapter import DefaultAdapter
from Helpers.CrewHelper import getSkillPenaltyData
from Helpers.cache import getFromCache
from debug_utils import LOG_ERROR

class ISkillPenaltyAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        member = getFromCache([kw['idTypeList'][0]], 'ICrewMember')
        if member is None:
            LOG_ERROR('Try call ISkillPenalty for non-cached crew', [kw['idTypeList'][0]])
            return {'penaltyPrc': 100,
             'descriptions': [],
             'skills': [],
             'mainSpecLevel': 50,
             'mainSkillLock': False,
             'SPLock': False}
        else:
            planeTo = kw['idTypeList'][1][0]
            mainExp = member['mainExp']
            skills = member['skills']
            expLeftToMain = member['expLeftToMain']
            SP = member['SP']
            experience = member['experience']
            skillValue = member['skillValue']
            planeSpecializedOn = member['planeSpecializedOn']
            specialization = member['specialization']
            return getSkillPenaltyData(planeTo, mainExp, skills, expLeftToMain, SP, experience, skillValue, planeSpecializedOn, specialization)