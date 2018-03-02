# Embedded file name: scripts/common/db/DBAreaConquest/GMSettings/UiSettingsModel.py
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBBoolProperty, DBIntProperty, DBStringProperty

class UiSettingsModel(DBModelBase):
    """UiSettingsModel feature settings model
    """
    teamIndex = DBIntProperty(default=0)
    title = DBStringProperty(default='')
    isShowSetorsView = DBBoolProperty(default=True)
    isShowDominationView = DBBoolProperty(default=True)
    isShowTeamRespawnsView = DBBoolProperty(default=True)

    def read(self, section):
        super(UiSettingsModel, self).read(section)