# Embedded file name: scripts/common/performanceCharacteristics.py
import db.DBLogic
from SkillsHelper import calculateCommonAndImprovedSkillValue
from _airplanesConfigurations_db import airplanesConfigurations
import _performanceCharacteristics_db
from _skills_data import SkillDB
from _performanceCharacteristics_db import PC
from _skills_data import ModsTypeEnum as SkillModsTypeEnum
from _equipment_data import ModsTypeEnum as EquipmentModsTypeEnum
import types
from consts import LOGICAL_PART
performanceParamList = ['hp',
 'dps',
 'speedFactor',
 'maneuverability',
 'speedAtTheGround',
 'maxSpeed',
 'optimalHeight',
 'averageTurnTime',
 'mass',
 'shellMass',
 'rateOfClimbing',
 'optimalManeuverSpeed',
 'rollManeuverability',
 'controllability',
 'diveSpeed',
 'stallSpeed']

def hp(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].hp


def dps(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].dps


def speedFactor(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].speedFactor


def maneuverability(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].maneuverability


def speedAtTheGround(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].speedAtTheGround


def maxSpeed(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].maxSpeed


def optimalHeight(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].optimalHeight


def averageTurnTime(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].averageTurnTime


def mass(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].mass


def shellMass(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].shellMass


def rateOfClimbing(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].rateOfClimbing


def optimalManeuverSpeed(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].optimalManeuverSpeed


def rollManeuverability(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].rollManeuverability


def controllability(globalID, modifiers, bombCount, rocketCount):
    return _performanceCharacteristics_db.airplanes[globalID].controllability


def getPerformanceSpecs(globalID, equipment = None, skills = None):
    specs = _performanceCharacteristics_db.airplanes.get(globalID, None)
    if specs is None:
        return
    else:
        corrections = dict(specs.__dict__)
        skillModification = __getEquipmentSkillModificator(skills)
        if equipment:
            __equipmentHPModification(corrections, equipment, skillModification)
        return roundSpecs(corrections)


def __equipmentHPModification(specsDict, equipment, skillModification):
    for eid in equipment:
        entry = db.DBLogic.g_instance.getEquipmentByID(eid)
        if entry is not None:
            for mod in entry.mods:
                if mod.type == EquipmentModsTypeEnum.MAIN_HP:
                    specsDict['hp'] = specsDict['hp'] * (1 + (mod.value_ - 1) * skillModification)

    return


def __getEquipmentSkillModificator(skills):
    retValue = 1.0
    if skills is None:
        return retValue
    else:
        for crewMember in skills:
            for skillData in crewMember['skills']:
                skillID = skillData['key']
                skillValue = skillData['value']
                specValue = calculateCommonAndImprovedSkillValue(skillValue)
                for mod in SkillDB[skillID].mods:
                    if hasattr(mod, 'relation') and any((modType == SkillModsTypeEnum.MAIN_HP for modType in mod.relation.type)):
                        modificator = mod.states.good if hasattr(mod.states, 'good') else mod.states[0]
                        retValue *= 1 + (modificator - 1) * specValue / 100.0

        return retValue


def roundSpecs(stuff):
    return PC(**dict(((k, v) for k, v in stuff.iteritems() if isinstance(v, (types.IntType, types.LongType, types.FloatType)))))