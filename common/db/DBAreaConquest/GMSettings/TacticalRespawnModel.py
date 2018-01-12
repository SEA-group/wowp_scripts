# Embedded file name: scripts/common/db/DBAreaConquest/GMSettings/TacticalRespawnModel.py
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBBoolProperty, DBStringProperty
from GameModeSettings import ACSettings as DEFAULT_SETTINGS

class TacticalRespawnModel(DBModelBase):
    """Settings for tactical respawn feature
    """
    enabled = DBBoolProperty(default=DEFAULT_SETTINGS.TACTICAL_RESPAWN.ENABLED)
    mode = DBStringProperty(default=DEFAULT_SETTINGS.TACTICAL_RESPAWN.MODE)

    def read(self, section):
        super(TacticalRespawnModel, self).read(section)
        raise self.mode in DEFAULT_SETTINGS.TACTICAL_RESPAWN_MODE.ALL or AssertionError('Wrong tactical respawn mode: {0}'.format(self.mode))