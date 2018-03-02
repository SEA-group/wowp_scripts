# Embedded file name: scripts/common/db/DBAreaConquest/GMSettings/ArenaGameModeSettingsModel.py
from debug_utils import LOG_DEBUG
from db.DBAreaConquest.GMSettings.UiSettingsModel import UiSettingsModel
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBIntProperty, DBListProperty, DBStringProperty, DBBoolProperty, DBModelProperty
from GameModeSettings import ACSettings as DEFAULT_SETTINGS
from AirStrikeModel import AirStrikeModel
from BattleEventsModel import BattleEventsModel
from RespawnModel import RespawnGroupModel
from TacticalRespawnModel import TacticalRespawnModel

class ArenaGameModeSettingsModel(DBModelBase):
    """Model to store game mode specific settings for arena
    """
    PRESET_KEY = 'preset'
    battleDurationDynamic = DBIntProperty(default=DEFAULT_SETTINGS.BATTLE_DURATION_DYNAMIC_DEFAULT)
    battleDuration = DBIntProperty(default=DEFAULT_SETTINGS.BATTLE_DURATION)
    pointsToWin = DBIntProperty(default=DEFAULT_SETTINGS.POINTS_TO_WIN)
    defenceHPointsToWin = DBIntProperty(default=DEFAULT_SETTINGS.HOLDING_POINTS_TO_WIN_DEFENCE)
    offenseHPointsToWin = DBIntProperty(default=DEFAULT_SETTINGS.HOLDING_POINTS_TO_WIN_OFFENSE)
    resourcePointsStart = DBIntProperty(default=DEFAULT_SETTINGS.DEFAULT_RESOURCE_POINTS_TO_START)
    eliminationByDefence = DBBoolProperty(default=DEFAULT_SETTINGS.ELIMINATION_BY_DEFENCE)
    eliminationByOffense = DBBoolProperty(default=DEFAULT_SETTINGS.ELIMINATION_BY_OFFENSE)
    winByTimeout = DBIntProperty(default=DEFAULT_SETTINGS.WIN_BY_TIMEOUT)
    winByDynamicTimeout = DBIntProperty(default=DEFAULT_SETTINGS.WIN_BY_DYNAMIC_TIMEOUT)
    globalTickPeriod = DBIntProperty(default=DEFAULT_SETTINGS.GLOBAL_TICK_PERIOD)
    superiorityGlobalTickPeriod = DBIntProperty(default=DEFAULT_SETTINGS.SUPERIORITY_GLOBAL_TICK_PERIOD)
    endGameConditions = DBListProperty(elementType=DBStringProperty(sectionName='condition'))
    gameManagers = DBListProperty(elementType=DBStringProperty(sectionName='manager'))
    respawn = DBModelProperty(factory=RespawnGroupModel)
    tacticalRespawn = DBModelProperty(factory=TacticalRespawnModel)
    battleEvents = DBModelProperty(factory=BattleEventsModel)
    airStrike = DBModelProperty(factory=AirStrikeModel)
    uiSettings = DBListProperty(elementType=DBModelProperty(factory=UiSettingsModel, sectionName='widgetsList'))
    stopWhenOnlyBotsLeft = DBBoolProperty(default=DEFAULT_SETTINGS.STOP_WHEN_ONLY_BOTS_LEFT)
    aiPlayerGameModePlan = DBStringProperty(default=DEFAULT_SETTINGS.AI_PLAYER_GAME_MODE_PLAN)

    def read(self, section):
        if section.has_key(self.PRESET_KEY):
            from db.DBAreaConquest import GameModeSettingsPresets
            presetName = section[self.PRESET_KEY].asString
            presetModel = GameModeSettingsPresets.getPresetByName(presetName)
            presetModel.copyTo(self)
        super(ArenaGameModeSettingsModel, self).read(section)