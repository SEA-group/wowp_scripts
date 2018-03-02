# Embedded file name: scripts/common/db/DBAreaConquest/SectorPresetModel.py
from consts import DEFENDER_TYPE, PLANE_TYPE, PLANE_TYPE_NAME_REVERSED, GAME_MODE_PATH_NAMES
from debug_utils import LOG_ERROR
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBPropertyBase, DBStringProperty, DBIntProperty, DBFloatProperty, DBBoolProperty, DBModelProperty, DBListProperty
from BomberDispatcherModel import BomberDispatcherPresetModel
from RocketV2Model import RocketV2PresetModel
PRESET_KEY = 'preset'

class SectorDefendersProperty(DBPropertyBase):
    """Custom property to store defenders settings for sector
    """
    DEFAULT_LEVEL_KEY = 0

    @property
    def default(self):
        return {}

    def _doRead(self, section):
        result = {}
        for _, i in section.items():
            if not i.has_key('defenderType'):
                LOG_ERROR('Sector defenderCounter sub-element missing defenderType attribute')
                continue
            defenderTypeString = i['defenderType'].asString
            if not hasattr(DEFENDER_TYPE, defenderTypeString):
                LOG_ERROR('Sector defenderCounter sub-element has incorrect defenderType attribute')
                continue
            defenderType = getattr(DEFENDER_TYPE, defenderTypeString)
            battleLevel = i['battleLevel'].asInt if i.has_key('battleLevel') else self.DEFAULT_LEVEL_KEY
            result.setdefault(defenderType, dict())[battleLevel] = i.asInt

        return result


class SectorPlaneEffectiveness(DBPropertyBase):

    @property
    def default(self):
        return {}

    def _doRead(self, section):
        result = []
        for _, i in section.items():
            if not i.has_key('planeType'):
                continue
            planeTypeString = i['planeType'].asString
            planeType = getattr(PLANE_TYPE, planeTypeString)
            effectivness = i.asInt
            result.append({'planeType': planeType,
             'effectivness': effectivness})

        return result


class SectorSoundModel(DBModelBase):
    allyEvent = DBStringProperty(default='')
    enemyEvent = DBStringProperty(default='')
    conditions = DBIntProperty(default=0)


class SectorSoundBaseModel(DBModelBase):
    captureModel = DBModelProperty(factory=SectorSoundModel, sectionName='onCapture')
    captureLastModel = DBModelProperty(factory=SectorSoundModel, sectionName='onCaptureLast')
    alarmModel = DBModelProperty(factory=SectorSoundModel, sectionName='onAlarm')


class SectorHudBaseModel(DBModelBase):
    """HUD settings for sector
    """
    localizationID = DBStringProperty(default='')
    showBorder = DBBoolProperty(default=True)
    showMarker = DBBoolProperty(default=True)
    featuresName = DBStringProperty(default='')
    featuresIconPath = DBStringProperty(default='')
    sectorIconPath = DBStringProperty(default='')
    battleHintIcon = DBStringProperty(default='event_cc1')
    miniMapSectorIconPath = DBStringProperty(default='')
    miniMapFeaturesIconPath = DBStringProperty(default='')
    isNeedToShowTimer = DBBoolProperty(default=True)
    isBig = DBBoolProperty(default=False)
    isMulticolorInPermanentLockState = DBBoolProperty(default=True)
    isHideFeaturesName = DBBoolProperty(default=False)
    description = DBStringProperty(default='')
    sectorObjects = DBListProperty(elementType=DBIntProperty(sectionName='object'))
    descriptionList = DBListProperty(elementType=DBStringProperty(sectionName='description'))
    planesEffectiveness = SectorPlaneEffectiveness()


class PointsProducerModel(DBModelBase):
    """Model for sector points producer item settings
    """
    period = DBIntProperty(default=1)
    points = DBIntProperty(default=3)
    label = DBStringProperty(default='main')

    def shouldProducePoints(self, initialTick, currentTick):
        """Indicate if producer should produce points specified tick  
        :param initialTick: Tick when sector timer started (sector was captured) 
        :param currentTick: Current tick
        :rtype: bool
        """
        return (currentTick - initialTick + 1) % self.period == 0

    def getPointsInTick(self, initialTick, currentTick):
        """Return points amount that will be produced in specified tick
        :param initialTick: Tick when sector timer started (sector was captured) 
        :param currentTick: Current tick 
        :rtype: int
        """
        if self.shouldProducePoints(initialTick, currentTick):
            return self.points
        return 0


class PointsProductionModel(DBModelBase):
    """Model for sector points production feature
    """
    _ALL = object()
    producers = DBListProperty(elementType=DBModelProperty(factory=PointsProducerModel, sectionName='producer'))

    def getPointsInTick(self, initialTick, currentTick, labels = _ALL):
        return sum((p.getPointsInTick(initialTick, currentTick) for p in self.filterProducers(labels)))

    def filterProducers(self, labels = _ALL):
        for producer in self.producers:
            if labels is self._ALL or producer.label in labels:
                yield producer

    def getProducerByLabel(self, label):
        """Return producer model by its label
        :param label: Producer label
        :rtype: PointsProducerModel
        """
        return next((p for p in self.producers if p.label == label), None)


class MultiplierByPlaneTypeProperty(DBPropertyBase):
    """Custom property to store multiplier settings per plane type
    """

    @property
    def default(self):
        return {}

    def _strToPlaneType(self, s, section):
        res = PLANE_TYPE_NAME_REVERSED.get(s.strip(), None)
        if not res:
            raise ValueError('DBPlaneTypesProperty Error: conversion from {0} to plane type! (file: {1}; section: {2})'.format(s, section.filename, section.name))
        return res

    def _doRead(self, section):
        result = {}
        for _, i in section.items():
            planeTypeString = i['planeType'].asString
            planeType = self._strToPlaneType(planeTypeString, section)
            result[planeType] = i.asFloat

        return result


class SectorAIACModel(DBModelBase):
    """AI strategy settings for sector (Arena Conquest mode)
    """
    baseValue = DBFloatProperty(default=1000)
    planeTypeMultiplier = MultiplierByPlaneTypeProperty()
    antiGroundWeaponBonus = MultiplierByPlaneTypeProperty()


class SectorAIModel(DBModelBase):
    """AI strategy settings for sector
    """
    areaConquest = DBModelProperty(factory=SectorAIACModel)


class SectorPresetModel(DBModelBase):
    """Sector base settings container
    """
    gameplayType = DBStringProperty()
    teamIndex = DBIntProperty()
    state = DBStringProperty()
    lockTime = DBIntProperty()
    playerSpawnEnabled = DBBoolProperty()
    respawnCooldownReduceEnabled = DBBoolProperty()
    tacticalRespawnEnabled = DBBoolProperty()
    holdingPointsDefence = DBIntProperty()
    holdingPointsOffense = DBIntProperty()
    dynamicTimeIncrease = DBIntProperty()
    isPermanentLock = DBBoolProperty()
    neutralCapturePoints = DBIntProperty(default=2)
    ownedCapturePoints = DBIntProperty(default=2)
    defenderCounter = SectorDefendersProperty()
    bomberDispatcher = DBModelProperty(factory=BomberDispatcherPresetModel)
    rocketV2 = DBModelProperty(factory=RocketV2PresetModel)
    hudSettings = DBModelProperty(factory=SectorHudBaseModel, sectionName='hud')
    soundSettings = DBModelProperty(factory=SectorSoundBaseModel, sectionName='sound')
    aiSettings = DBModelProperty(factory=SectorAIModel, sectionName='ai')
    pointsProduction = DBModelProperty(factory=PointsProductionModel)

    def __init__(self, gameModeDir):
        super(SectorPresetModel, self).__init__()
        self._gameModeDir = gameModeDir

    def read(self, section):
        """Read model data from data section using preset model if specified
        """
        if section.has_key(PRESET_KEY):
            from SectorPresets import getPresetByName
            presetName = section[PRESET_KEY].asString
            presetModel = getPresetByName(presetName, self._gameModeDir)
            presetModel.copyTo(self)
        super(SectorPresetModel, self).read(section)

    def getDefenderCountWithBattleLevel(self, battleLevel):
        return sum(((defendersByType[battleLevel] if battleLevel in defendersByType else defendersByType.get(SectorDefendersProperty.DEFAULT_LEVEL_KEY, 0)) for defendersByType in self.defenderCounter.itervalues()))

    def getDefenderCountWithBattleLevelAndType(self, battleLevel, defenderType):
        defendersByType = self.defenderCounter.get(defenderType, dict())
        if battleLevel in defendersByType:
            return defendersByType[battleLevel]
        return defendersByType.get(SectorDefendersProperty.DEFAULT_LEVEL_KEY, 0)