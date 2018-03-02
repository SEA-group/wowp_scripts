# Embedded file name: scripts/common/db/DBAreaConquest/GMSettings/RespawnModel.py
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBIntProperty, DBBoolProperty, DBStringProperty, DBModelProperty, DBListProperty
from GameModeSettings import ACSettings as DEFAULT_SETTINGS

class TeamRespawnModel(DBModelBase):
    """Team respawn settings
    """
    cooldownBase = DBIntProperty(default=DEFAULT_SETTINGS.TEAM_RESPAWN.COOLDOWN_BASE)
    cooldownMinValue = DBIntProperty(sectionName='cooldownMinimal', default=DEFAULT_SETTINGS.TEAM_RESPAWN.COOLDOWN_MINIMAL)
    cooldownReduceStep = DBIntProperty(default=DEFAULT_SETTINGS.TEAM_RESPAWN.COOLDOWN_REDUCE_STEP)
    cooldownDeathPenalty = DBIntProperty(default=DEFAULT_SETTINGS.TEAM_RESPAWN.COOLDOWN_DEATH_PENALTY)


class IndividualRespawnModel(DBModelBase):
    """Individual respawn settings
    """
    cooldownBase = DBIntProperty(default=DEFAULT_SETTINGS.INDIVIDUAL_RESPAWN.COOLDOWN_BASE)
    cooldownMinValue = DBIntProperty(sectionName='cooldownMinimal', default=DEFAULT_SETTINGS.INDIVIDUAL_RESPAWN.COOLDOWN_MINIMAL)
    cooldownReduceStep = DBIntProperty(default=DEFAULT_SETTINGS.INDIVIDUAL_RESPAWN.COOLDOWN_REDUCE_STEP)
    cooldownDeathPenalty = DBIntProperty(default=DEFAULT_SETTINGS.INDIVIDUAL_RESPAWN.COOLDOWN_DEATH_PENALTY)


class IndividualWithTLRespawnModel(DBModelBase):
    """Individual respawn with death limit settings
    """
    cooldownBase = DBIntProperty(default=DEFAULT_SETTINGS.INDIVIDUAL_RESPAWN.COOLDOWN_BASE)
    cooldownMinValue = DBIntProperty(sectionName='cooldownMinimal', default=DEFAULT_SETTINGS.INDIVIDUAL_RESPAWN.COOLDOWN_MINIMAL)
    cooldownReduceStep = DBIntProperty(default=DEFAULT_SETTINGS.INDIVIDUAL_RESPAWN.COOLDOWN_REDUCE_STEP)
    cooldownDeathPenalty = DBIntProperty(default=DEFAULT_SETTINGS.INDIVIDUAL_RESPAWN.COOLDOWN_DEATH_PENALTY)
    deathTeamLimit = DBIntProperty(default=DEFAULT_SETTINGS.INDIVIDUAL_RESPAWN.DEATH_LIMIT)


class RespawnModel(DBModelBase):
    """Respawn settings data model
    """
    teamIndex = DBIntProperty(default=0)
    unlimited = DBBoolProperty(default=DEFAULT_SETTINGS.RESPAWN.UNLIMITED)
    avatarLives = DBIntProperty(default=DEFAULT_SETTINGS.RESPAWN.AVATAR_LIVES)
    respawnType = DBStringProperty(default=DEFAULT_SETTINGS.RESPAWN.DEFAULT_TYPE, sectionName='type')
    _teamRespawn = DBModelProperty(factory=TeamRespawnModel, sectionName='strategy')
    _individualRespawn = DBModelProperty(factory=IndividualRespawnModel, sectionName='strategy')
    _individualTLRespawn = DBModelProperty(factory=IndividualWithTLRespawnModel, sectionName='strategy')
    availablePlaneTypes = DBListProperty(elementType=DBIntProperty(sectionName='planeTypeId'))

    @property
    def respawnStrategySettings(self):
        """Respawn strategy settings model
        :rtype: TeamRespawnModel | IndividualRespawnModel
        """
        if self.respawnType == DEFAULT_SETTINGS.RESPAWN_TYPE.INDIVIDUAL:
            return self._individualRespawn
        elif self.respawnType == DEFAULT_SETTINGS.RESPAWN_TYPE.INDIVIDUAL_TL:
            return self._individualTLRespawn
        else:
            return self._teamRespawn

    def read(self, section):
        super(RespawnModel, self).read(section)
        raise self.respawnType in DEFAULT_SETTINGS.RESPAWN_TYPE.ALL or AssertionError('Wrong respawn type: {0}, expected one of {1}'.format(self.respawnType, DEFAULT_SETTINGS.RESPAWN_TYPE.ALL))


class RespawnGroupModel(DBModelBase):
    respawnModel = DBListProperty(elementType=DBModelProperty(factory=RespawnModel, sectionName='respawn_strategy'))