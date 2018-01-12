# Embedded file name: scripts/common/FastCommandsConfiguration.py
import ResMgr
from consts import FAST_COMMANDS_SETTINGS_PATH
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import *
from debug_utils import LOG_ERROR

class FastCommandModel(object):

    def __init__(self):
        cfgSection = ResMgr.openSection(FAST_COMMANDS_SETTINGS_PATH)
        if not cfgSection:
            LOG_ERROR('FastCommand Settings: Failed to open ', FAST_COMMANDS_SETTINGS_PATH)
            return
        self.config = FastCommandsConfiguration()
        self.config.read(cfgSection)
        ResMgr.purge(FAST_COMMANDS_SETTINGS_PATH, True)

    @property
    def configuration(self):
        return self.config


class BaseFastCommandConfig(DBModelBase):
    captureRadiusKoef = DBFloatProperty(default=200)
    minDistBetweenTargets = DBIntProperty(default=30)
    minDeltaDist = DBIntProperty(default=30)
    planeProtectors = DBPlaneTypesProperty([])
    receiversRange = DBIntProperty(default=150)
    receiversTypes = DBPlaneTypesProperty([])


class SupportConfig(DBModelBase):
    captureRadiusKoef = DBFloatProperty(default=200)
    minDistBetweenTargets = DBIntProperty(default=30)
    minDeltaDist = DBIntProperty(default=30)
    receiversRange = DBIntProperty(default=150)
    planeProtectors = DBPlaneTypesProperty([])
    planeSupports = DBPlaneTypesProperty([])
    receiversProtectorsTypes = DBPlaneTypesProperty([])
    receiversTypes = DBPlaneTypesProperty([])


class FastCommandsConfiguration(DBModelBase):
    intentions = DBModelProperty(factory=BaseFastCommandConfig, sectionName='intentions')
    support = DBModelProperty(factory=SupportConfig, sectionName='support')
    offenseDefense = DBModelProperty(factory=BaseFastCommandConfig, sectionName='offenseDefense')
    danger = DBModelProperty(factory=BaseFastCommandConfig, sectionName='danger')
    affirmative = DBModelProperty(factory=BaseFastCommandConfig, sectionName='affirmative')
    negative = DBModelProperty(factory=BaseFastCommandConfig, sectionName='negative')
    goodJob = DBModelProperty(factory=BaseFastCommandConfig, sectionName='goodJob')


class CommandTargets:
    NOTARGET = '-1'


class CommandTypes:
    INTENTIONS = 2
    SUPPORT = 3
    OFFENSE_DEFENSE = 4
    DANGER = 5
    AFFIRMATIVE = 6
    NEGATIVE = 7
    GOOD_JOB = 8


CommandTypesNames = {v:k for k, v in vars(CommandTypes).iteritems()}

class NotificationType:
    SPECIFY_COMMAND = -1
    OK = 0
    IN_FLYING_TO_ATTACK = 0
    IN_FLYING_TO_PROTECT = 1
    IN_FLYING_TO = 2
    SUP_ATTACK_NEED_SUPPORT = 0
    SUP_PROTECTED_NEED_SUPPORT = 1
    SUP_NEED_SUPPORT = 2
    OFD_ATTACK_PLANE = 0
    OFD_COVER_PLANE = 1
    OFD_ATTACK_BOMBERS = 2
    OFD_COVER_BOMBERS = 3