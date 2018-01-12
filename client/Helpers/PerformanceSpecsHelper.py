# Embedded file name: scripts/client/Helpers/PerformanceSpecsHelper.py
import _performanceCharacteristics_db
import types
from _equipment_data import ModsTypeEnum as EquipmentModsTypeEnum
from _performanceCharacteristics_db import PC
from _skills_data import ModsTypeEnum as SkillModsTypeEnum
from _skills_data import SkillDB
from debug_utils import LOG_ERROR
import db
from HelperFunctions import wowpRound
from Helpers.cache import getFromCache
from Helpers.i18n import localizeLobby
from SkillsHelper import calculateCommonAndImprovedSkillValue
from consts import CHARACTERISTICS_LOCALIZATION_MAP, AIRCRAFT_CHARACTERISTIC, CHARACTERISTICS_HINTS_MAP, SPECS_KEY_MAP, SPECS_BOUNDARIES, MAIN_CHARACTERISTICS_LIST, ADDITIONAL_CHARACTERISTICS_PARENTS_MAP
from gui.Scaleform.utils.MeasurementSystem import MeasurementSystem

class ProjectileInfo(object):

    def __init__(self, slotID, configID, maxCount, curCount):
        self.curCount = curCount
        self.maxCount = maxCount
        self.slotID = slotID
        self.configurationID = configID


def getComparisonValue(specsTable, value, tag):
    if specsTable is not None and value is not None:
        keyOther, valueOther, unitOther, largerIsBetterOther = getAirplaneDescriptionPair(specsTable, tag)
        comparsionValue = value - valueOther
        return comparsionValue
    else:
        return 0


def __getCorrections(projectiles, diffs):
    corrections = {}
    for weaponConfig in projectiles:
        load = 1.0 - float(weaponConfig.curCount) / float(weaponConfig.maxCount)
        correction = diffs.get(db.DBLogic.slotLoadID([weaponConfig.slotID]), None)
        if correction:
            for k in correction.__dict__.keys():
                if not corrections.has_key(k):
                    corrections[k] = 0
                corrections[k] += getattr(correction, k) * load

    return corrections


def getPerformanceSpecsTable(globalID, modify = False, projectiles = None, equipment = None, crewList = None, maxHealth = None):
    specs = _performanceCharacteristics_db.airplanes.get(globalID, None)
    if specs is None:
        LOG_ERROR('getPerformanceSpecsTable() GlobalID {0} was not found in db'.format(globalID))
        return
    elif not modify:
        return roundSpecs(dict(specs.__dict__))
    else:
        diffs = specs.diff
        corrections = None
        if projectiles is not None:
            corrections = __getCorrections(projectiles, diffs)
            if corrections:
                for k in corrections.keys():
                    corrections[k] = getattr(specs, k) - corrections[k]

        if not corrections:
            corrections = dict(specs.__dict__)
        if maxHealth is not None:
            corrections['hp'] = int(maxHealth)
        else:
            skillModification = __getEquipmentSkillModificator(crewList)
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


def __getEquipmentSkillModificator(crewList):
    retValue = 1.0
    if crewList is None:
        return retValue
    else:
        for _, memberID in crewList:
            member = getFromCache([[memberID, 'crewmember']], 'ICrewMember')
            if member is None:
                continue
            skillValue = member['skillValue']
            specValue = calculateCommonAndImprovedSkillValue(skillValue)
            for skillID in member['skills']:
                for mod in SkillDB[skillID].mods:
                    if hasattr(mod, 'relation') and any((modType == SkillModsTypeEnum.MAIN_HP for modType in mod.relation.type)):
                        modificator = mod.states.good if hasattr(mod.states, 'good') else mod.states[0]
                        retValue *= 1 + (modificator - 1) * specValue / 100.0

        return retValue


def roundSpecs(stuff):
    return PC(**dict(((k, v) for k, v in stuff.iteritems() if isinstance(v, (types.IntType, types.LongType, types.FloatType)))))


def getPerformanceSpecsTableDeprecated(lobbyAirplane, modify, lobbyAirplaneGlobalID = None):
    planeID = lobbyAirplane.planeID
    if not lobbyAirplaneGlobalID:
        upgrades = [ upgrade['name'] for upgrade in lobbyAirplane.modules.getInstalled() ]
        lobbyAirplaneGlobalID = db.DBLogic.createGlobalID(planeID, upgrades, lobbyAirplane.weapons.getInstalledWeaponsList())
    characteristics = _performanceCharacteristics_db.airplanes.get(lobbyAirplaneGlobalID, None)
    if characteristics is None:
        LOG_ERROR('getPerformanceSpecsTableDeprecated - GlobalID(%s) not found in db, planeID=%s' % (lobbyAirplaneGlobalID, planeID))
        return
    elif not modify:
        return roundSpecs(characteristics.__dict__)
    else:
        diffs = characteristics.diff
        projectiles = lobbyAirplane.weapons.getInstalledProjectiles()
        corrections = __getCorrections(projectiles, diffs)
        if corrections:
            for k in corrections.keys():
                corrections[k] = getattr(characteristics, k) - corrections[k]

        else:
            corrections = dict(characteristics.__dict__)
        import BWPersonality
        if BWPersonality.g_lobbyCarouselHelper is not None:
            inv = BWPersonality.g_lobbyCarouselHelper.inventory
            skillModification = __getEquipmentSkillModificator(inv.getCrewList(planeID))
            __equipmentHPModification(corrections, inv.getEquipment(planeID), skillModification)
        return roundSpecs(corrections)


def _adjustSpec(value, tag, measurementSystem = None):
    largerIsBetter = True
    unit = None
    ms = measurementSystem or MeasurementSystem()
    if tag == AIRCRAFT_CHARACTERISTIC.MASS:
        value = int(round(ms.getKgs(value)))
        unit = ms.localizeMarket(CHARACTERISTICS_LOCALIZATION_MAP[tag])
        largerIsBetter = False
    elif tag == AIRCRAFT_CHARACTERISTIC.GROUND_MAX_SPEED:
        value = int(round(ms.getKmh(value)))
        unit = ms.localizeMarket(CHARACTERISTICS_LOCALIZATION_MAP[tag])
    elif tag == AIRCRAFT_CHARACTERISTIC.HEIGHT_MAX_SPEED:
        value = int(round(ms.getKmh(value)))
        unit = ms.localizeMarket(CHARACTERISTICS_LOCALIZATION_MAP[tag])
    elif tag in (AIRCRAFT_CHARACTERISTIC.OPTIMAL_HEIGHT, AIRCRAFT_CHARACTERISTIC.ALT_PERFORMANCE):
        value = int(round(ms.getMeters(value)))
        if tag == AIRCRAFT_CHARACTERISTIC.OPTIMAL_HEIGHT:
            unit = ms.localizeMarket(CHARACTERISTICS_LOCALIZATION_MAP[tag])
    elif tag == AIRCRAFT_CHARACTERISTIC.RATE_OF_CLIMB:
        value = wowpRound(ms.getMeters(value), 1)
        unit = ms.localizeMarket(CHARACTERISTICS_LOCALIZATION_MAP[tag])
    elif tag == AIRCRAFT_CHARACTERISTIC.AVERAGE_TURN_TIME:
        value = wowpRound(value, 1)
        unit = localizeLobby('MARKET_AIRPLANE_FULL_TURN_TIME_SEC')
        largerIsBetter = False
    elif tag == AIRCRAFT_CHARACTERISTIC.DIVE_SPEED:
        value = int(round(ms.getKmh(value)))
        unit = ms.localizeMarket(CHARACTERISTICS_LOCALIZATION_MAP[tag])
    elif tag == AIRCRAFT_CHARACTERISTIC.STALL_SPEED:
        value = int(round(ms.getKmh(value)))
        unit = ms.localizeMarket(CHARACTERISTICS_LOCALIZATION_MAP[tag])
        largerIsBetter = False
    elif tag == AIRCRAFT_CHARACTERISTIC.OPTIMAL_MANEUVER_SPEED:
        value = wowpRound(ms.getKmh(value), 1)
        unit = ms.localizeMarket(CHARACTERISTICS_LOCALIZATION_MAP[tag])
    elif tag == AIRCRAFT_CHARACTERISTIC.ROLL_MANEUVERABILITY:
        value = int(round(value))
        unit = ms.localizeMarket(CHARACTERISTICS_LOCALIZATION_MAP[tag])
    else:
        value = int(round(value))
    return (value, unit, largerIsBetter)


def getAirplaneDescriptionPair(characteristicsTable, tag, measurementSystem = None):
    name = localizeLobby(CHARACTERISTICS_LOCALIZATION_MAP[tag])
    if characteristicsTable is not None:
        value = getattr(characteristicsTable, SPECS_KEY_MAP[tag])
        value, unit, largerIsBetter = _adjustSpec(value, tag, measurementSystem)
    else:
        LOG_ERROR('Characteristics table is empty')
        value = 0
        unit = None
    return (name,
     value,
     unit,
     largerIsBetter)


class DescriptionFieldsGroup:

    def __init__(self):
        self.main = None
        self.additional = []
        return


class PlaneCharacteristicsField:

    def __init__(self, name = None, value = 0, comparisonValue = None, tag = None, unit = None, isWeapon = False, higherIsBetter = True):
        """is used for passing characteristics data to the flash"""
        self.higherIsBetter = higherIsBetter
        self.name = name
        self.value = value
        self.valueString = value if isinstance(value, basestring) else None
        self.unit = unit
        self.comparisonValue = comparisonValue
        self.isWeapon = isWeapon
        self.type = tag
        self.description = CHARACTERISTICS_HINTS_MAP[tag] if tag in CHARACTERISTICS_HINTS_MAP else None
        return


def getCharacteristicsList(specsTable, globalID, compareSpecsTable, measurementSystem = None):
    ret = []
    for tag in SPECS_KEY_MAP:
        key, value, unit, largerIsBetter = getAirplaneDescriptionPair(specsTable, tag, measurementSystem)
        if not (key is None and value is None and unit is None):
            comparisonValue = getComparisonValue(compareSpecsTable, value, tag)
            item = PlaneCharacteristicsField(name=key, value=value, unit=unit, tag=tag, comparisonValue=comparisonValue)
            ret.append(item)

    return ret


def getGroupedDescriptionFields(descriptionList):
    """
    @param forceBuild:
    @param aircraftForCompare:
    @param installedGlobalID:
    @return: {<main characteristic type> : <DescriptionFieldsGroup>, ...}
    """
    descriptionGroupDict = {}

    def getGroup(groupId):
        if groupId in descriptionGroupDict:
            return descriptionGroupDict[groupId]
        group = DescriptionFieldsGroup()
        descriptionGroupDict[groupId] = group
        return group

    for descriptionField in descriptionList:
        if descriptionField.type in MAIN_CHARACTERISTICS_LIST:
            group = getGroup(descriptionField.type)
            group.main = descriptionField
        elif descriptionField.type in ADDITIONAL_CHARACTERISTICS_PARENTS_MAP:
            group = getGroup(ADDITIONAL_CHARACTERISTICS_PARENTS_MAP[descriptionField.type])
            group.additional.append(descriptionField)

    result = []
    for groupId in MAIN_CHARACTERISTICS_LIST:
        group = descriptionGroupDict[groupId]
        group.additional.sort(lambda x, y: cmp(x.type, y.type))
        result.append(group)

    return result


def getMainCharacteristicBoundariesForPlane(planeID, tag):
    minValue, maxValue = db.DBLogic.g_instance.getPlaneMinMaxSpec(planeID, tag)
    minValue, _, _ = _adjustSpec(minValue, tag)
    maxValue, _, _ = _adjustSpec(maxValue, tag)
    return (minValue, maxValue)