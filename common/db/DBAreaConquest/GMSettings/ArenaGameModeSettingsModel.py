# Embedded file name: scripts/common/db/DBAreaConquest/GMSettings/ArenaGameModeSettingsModel.py
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBIntProperty, DBListProperty, DBStringProperty, DBBoolProperty, DBModelProperty
from GameModeSettings import ACSettings as DEFAULT_SETTINGS
from AirStrikeModel import AirStrikeModel
from BattleEventsModel import BattleEventsModel
from RespawnModel import RespawnModel
from TacticalRespawnModel import TacticalRespawnModel

class ArenaGameModeSettingsModel(DBModelBase):
    """Model to store game mode specific settings for arena
    """
    PRESET_KEY = 'preset'
    battleDuration = DBIntProperty(default=DEFAULT_SETTINGS.BATTLE_DURATION)
    pointsToWin = DBIntProperty(default=DEFAULT_SETTINGS.POINTS_TO_WIN)
    globalTickPeriod = DBIntProperty(default=DEFAULT_SETTINGS.GLOBAL_TICK_PERIOD)
    superiorityGlobalTickPeriod = DBIntProperty(default=DEFAULT_SETTINGS.SUPERIORITY_GLOBAL_TICK_PERIOD)
    endGameConditions = DBListProperty(elementType=DBStringProperty(sectionName='condition'))
    respawn = DBModelProperty(factory=RespawnModel)
    tacticalRespawn = DBModelProperty(factory=TacticalRespawnModel)
    battleEvents = DBModelProperty(factory=BattleEventsModel)
    airStrike = DBModelProperty(factory=AirStrikeModel)
    stopWhenOnlyBotsLeft = DBBoolProperty(default=DEFAULT_SETTINGS.STOP_WHEN_ONLY_BOTS_LEFT)

    def read(self, section):
        if section.has_key(self.PRESET_KEY):
            from db.DBAreaConquest import GameModeSettingsPresets
            presetName = section[self.PRESET_KEY].asString
            presetModel = GameModeSettingsPresets.getPresetByName(presetName)
            presetModel.copyTo(self)
        super(ArenaGameModeSettingsModel, self).read(section)