# Embedded file name: scripts/client/Helpers/CrewHelper.py
import db.DBLogic
from SkillsHelper import getMainSpecializationLevel, calculateSkillPenalty, MAX_SKILL_SP, calculateEffectiveMainSkill
from _skills_data import SkillDB, SKILL_GROUP
from _specializations_data import SpecializationEnum
from consts import INVALID_SPECIALIZATION_SKILL_PENALTY

def getSkillPenaltyData(planeTo, mainExp, skills, expLeftToMain, SP, experience, skillValue, planeSpecializedOn, specialization):
    skillsList = skills[:]
    mainSpecLevel = getMainSpecializationLevel(mainExp)
    specialization = SkillDB[specialization].mainForSpecialization
    isGunner = specialization == SpecializationEnum.GUNNER
    mainSkillLock = __getMainSkillLock(planeSpecializedOn, planeTo)
    descriptions = []
    if planeTo == -1:
        SPLock = __getSPLockInBarrack(expLeftToMain, SP)
        descriptions.append(('LOBBY_GUNNER_DOES_NOT_GAIN_EXP', 'red', 'common') if isGunner else ('LOBBY_PILOT_DOES_NOT_GAIN_EXP', 'red', 'common'))
        return {'penaltyPrc': 0,
         'descriptions': descriptions,
         'skills': skillsList,
         'mainSpecLevel': mainSpecLevel,
         'mainSkillLock': mainSkillLock,
         'SPLock': SPLock}
    curPlaneSettings = db.DBLogic.g_instance.getAircraftData(planeSpecializedOn)
    newPlaneSettings = db.DBLogic.g_instance.getAircraftData(planeTo)
    isPremium = db.DBLogic.g_instance.isPlanePremium(planeTo)
    sameType = curPlaneSettings.airplane.planeType == newPlaneSettings.airplane.planeType
    samePlane = planeSpecializedOn == planeTo
    specSkillPenalty = samePlane and expLeftToMain > 0 or not samePlane and not isPremium
    descriptions.extend(__getBonusDescription(expLeftToMain, SP, isPremium, samePlane, isGunner))
    descriptions.extend(__getWarningDescription(expLeftToMain, experience, skills, skillValue, samePlane, sameType, specSkillPenalty))
    descriptions.extend(__getCriticalDescription(SP, skills, skillValue, isPremium, samePlane, sameType, specSkillPenalty, isGunner, planeTo))
    if specSkillPenalty and not isGunner and __hasUniqueSkill(skills):
        skillsList = [ id for id in skills if SkillDB[id].group != SKILL_GROUP.UNIQUE ]
    descriptions = [ dict(text=t, color=c, tooltip=h == 'tooltip') for t, c, h in descriptions ]
    penalty = calculateSkillPenalty(planeSpecializedOn, planeTo)
    SPLock = __getSPLockInPlane(expLeftToMain, SP, isPremium, samePlane)
    ret = {'penaltyPrc': penalty,
     'descriptions': descriptions,
     'mainSpecLevel': calculateEffectiveMainSkill(mainSpecLevel, planeSpecializedOn, planeTo),
     'skills': skillsList,
     'mainSkillLock': mainSkillLock,
     'SPLock': SPLock}
    return ret


def __hasUniqueSkill(skills):
    return any((SkillDB[skillID].group == SKILL_GROUP.UNIQUE for skillID in skills))


def __hasCommonSkill(skills):
    return any((SkillDB[skillID].group in [SKILL_GROUP.COMMON, SKILL_GROUP.IMPROVED] for skillID in skills))


def __getSPLockInBarrack(expLeftToMain, SP):
    if expLeftToMain == 0 and SP < MAX_SKILL_SP:
        return False
    return True


def __getSPLockInPlane(expLeftToMain, SP, isPremium, samePlane):
    if expLeftToMain == 0 and samePlane and SP < MAX_SKILL_SP:
        return False
    if not samePlane and isPremium and SP > 0 and SP < MAX_SKILL_SP:
        return False
    return True


def __getMainSkillLock(planeSpecializedOn, planeTo):
    if planeSpecializedOn != planeTo:
        return True
    return False


def __getBonusDescription(expLeftToMain, SP, isPremium, samePlane, isGunner):
    descriptions = []
    if isPremium:
        if SP > 0 and SP < MAX_SKILL_SP or expLeftToMain > 0 and samePlane:
            descriptions.append(('LOBBY_CREW_BONUS_EXP', 'green', 'common'))
        if not samePlane:
            if isGunner:
                descriptions.append(('LOBBY_GUNNER_EFFECTIVE_TURRET_INCREASED_100', 'green', 'tooltip'))
            else:
                descriptions.append(('LOBBY_PILOT_EFFECTIVE_STATS_INCREASED_100', 'green', 'tooltip'))
    return descriptions


def __getWarningDescription(expLeftToMain, experience, skills, skillValue, samePlane, sameType, specSkillPenalty):
    descriptions = []
    if not samePlane:
        descriptions.append(('LOBBY_CREW_ANOTHER_PLANE_FROZEN_EXP', 'yellow', 'common'))
    elif expLeftToMain > 0 and experience > 0:
        descriptions.append(('LOBBY_CREW_PROGRESS_OBTAIN_SKILL_POINT_SUSPENDED', 'yellow', 'common'))
    if specSkillPenalty:
        if __hasCommonSkill(skills):
            sameClassSkillValue = 100 - INVALID_SPECIALIZATION_SKILL_PENALTY
            if sameType and skillValue >= sameClassSkillValue:
                descriptions.append(('LOBBY_CREW_EFFECTIVE_STANDART_SKILLS_REDUCED_25', 'yellow', 'tooltip'))
            else:
                descriptions.append(('LOBBY_CREW_EFFECTIVE_STANDART_SKILLS_REDUCED_50', 'yellow', 'tooltip'))
    return descriptions


def __getCriticalDescription(SP, skills, skillValue, isPremium, samePlane, sameType, specSkillPenalty, isGunner, planeTo):
    descriptions = []
    for skillID in skills:
        if len(SkillDB[skillID].bindForPlanes) > 0 and planeTo not in SkillDB[skillID].bindForPlanes:
            descriptions.append(('TOOLTIPS_UNIQUE_SKILL_DOESNT_WORK', 'red', 'tooltip'))
            break

    if specSkillPenalty and not isGunner and __hasUniqueSkill(skills):
        descriptions.append(('LOBBY_PILOT_SPETIALS_SKILLS_DOESNT_WORK', 'red', 'tooltip'))
    if not samePlane and not isPremium:
        if SP > 0 and SP < MAX_SKILL_SP:
            descriptions.append(('LOBBY_CREW_PROGRESS_SKILLPOINT_FROZEN', 'red', 'common'))
        sameClassSkillValue = 100 - INVALID_SPECIALIZATION_SKILL_PENALTY
        if sameType and skillValue >= sameClassSkillValue:
            if isGunner:
                descriptions.append(('LOBBY_GUNNER_EFFECTIVE_TURRET_REDUCED_25', 'red', 'tooltip'))
            else:
                descriptions.append(('LOBBY_PILOT_EFFECTIVE_STATS_REDUCED_25', 'red', 'tooltip'))
        elif isGunner:
            descriptions.append(('LOBBY_GUNNER_EFFECTIVE_TURRET_REDUCED_50', 'red', 'tooltip'))
        else:
            descriptions.append(('LOBBY_PILOT_EFFECTIVE_STATS_REDUCED_50', 'red', 'tooltip'))
    return descriptions