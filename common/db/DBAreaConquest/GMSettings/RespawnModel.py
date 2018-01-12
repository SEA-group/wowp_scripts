# Embedded file name: scripts/common/db/DBAreaConquest/GMSettings/RespawnModel.py
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBIntProperty, DBBoolProperty, DBStringProperty, DBModelProperty
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


class RespawnModel(DBModelBase):
    """Respawn settings data model
    """
    unlimited = DBBoolProperty(default=DEFAULT_SETTINGS.RESPAWN.UNLIMITED)
    avatarLives = DBIntProperty(default=DEFAULT_SETTINGS.RESPAWN.AVATAR_LIVES)
    respawnType = DBStringProperty(default=DEFAULT_SETTINGS.RESPAWN.DEFAULT_TYPE, sectionName='type')
    _teamRespawn = DBModelProperty(factory=TeamRespawnModel, sectionName='strategy')
    _individualRespawn = DBModelProperty(factory=IndividualRespawnModel, sectionName='strategy')

    @property
    def respawnStrategySettings(self):
        """Respawn strategy settings model
        :rtype: TeamRespawnModel | IndividualRespawnModel
        """
        if self.respawnType == DEFAULT_SETTINGS.RESPAWN_TYPE.INDIVIDUAL:
            return self._individualRespawn
        else:
            return self._teamRespawn

    def read(self, section):
        super(RespawnModel, self).read(section)
        raise self.respawnType in DEFAULT_SETTINGS.RESPAWN_TYPE.ALL or AssertionError('Wrong respawn type: {0}, expected one of {1}'.format(self.respawnType, DEFAULT_SETTINGS.RESPAWN_TYPE.ALL))