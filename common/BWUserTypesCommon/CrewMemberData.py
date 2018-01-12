# Embedded file name: scripts/common/BWUserTypesCommon/CrewMemberData.py
from consts import BARRACK_KEYS
from debug_utils import LOG_DEBUG

class CrewMemberData(object):
    """Wrapper for FIXED_DICT with plane data for HUD crewData
    """

    def __init__(self, memberId, currentPlane, planeSpecializedOn, specialization, specializationSkill, experience, firstName, lastName, ranks, spAvailable, skills, sp, skillValue, bodyType):
        self.memberId = memberId
        self.currentPlane = currentPlane
        self.planeSpecializedOn = planeSpecializedOn
        self.specialization = specialization
        self.specializationSkill = specializationSkill
        self.experience = experience
        self.firstName = firstName
        self.lastName = lastName
        self.ranks = ranks
        self.spAvailable = spAvailable
        self.skills = skills
        self.sp = sp
        self.skillValue = skillValue
        self.bodyType = bodyType

    def __str__(self):
        data = instance.getDictFromObj(self)
        return '<CrewMemberData: {0}>'.format(data)


class CrewMemberDataConverter(object):
    """CrewMemberData converter to/from FIXED_DICT
    """

    def getDictFromObj(self, obj):
        """Convert to FIXED_DICT
        @type obj: CrewMemberData
        @rtype: dict
        """
        return {'memberId': obj.memberId,
         'currentPlane': obj.currentPlane,
         'planeSpecializedOn': obj.planeSpecializedOn,
         'specialization': obj.specialization,
         'specializationSkill': obj.specializationSkill,
         'experience': obj.experience,
         'firstName': obj.firstName,
         'lastName': obj.lastName,
         'ranks': obj.ranks,
         'spAvailable': obj.spAvailable,
         'skills': obj.skills,
         'sp': obj.sp,
         'skillValue': obj.skillValue,
         'bodyType': obj.bodyType}

    def createObjFromDict(self, dict_):
        """Convert FIXED_DICT to CrewMemberData
        @type dict_: dict
        @rtype: CrewMemberData
        """
        return CrewMemberData(**dict_)

    def isSameType(self, obj):
        return isinstance(obj, CrewMemberData)


instance = CrewMemberDataConverter()