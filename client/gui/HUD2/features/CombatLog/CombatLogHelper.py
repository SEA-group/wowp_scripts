# Embedded file name: scripts/client/gui/HUD2/features/CombatLog/CombatLogHelper.py
from CombatLogSettings import COMBAT_LOG_SETTINGS as SETTINGS

class COMBAT_EVENT_ID:
    UNDEFINED = 0
    KILL = 1
    HEAVY_ASSIST = 2
    ASSIST = 3
    DESTRUCTION = 4
    TURRET = 5


class COMBAT_EVENTS_NAMES:
    KILL_PLAYER = 'killPlayer'
    KILL_DEFENDER = 'killDef'
    KILL_BOMBER = 'killBomber'
    KILL_ALLY = 'killAlly'
    ASSISI_PLAYER_HEAVY = 'assistPlayerHeavy'
    ASSIST_PLAYER_LIGHT = 'assistPlayerLight'
    ASSIST_DEFENDER = 'assistDefender'
    ASSIST_BOMBER = 'assistBomber'


COMBAT_EVENTS_MAP = {COMBAT_EVENT_ID.KILL: [COMBAT_EVENTS_NAMES.KILL_PLAYER,
                        COMBAT_EVENTS_NAMES.KILL_DEFENDER,
                        COMBAT_EVENTS_NAMES.KILL_DEFENDER,
                        COMBAT_EVENTS_NAMES.KILL_ALLY],
 COMBAT_EVENT_ID.HEAVY_ASSIST: [COMBAT_EVENTS_NAMES.ASSISI_PLAYER_HEAVY],
 COMBAT_EVENT_ID.ASSIST: [COMBAT_EVENTS_NAMES.ASSIST_PLAYER_LIGHT, COMBAT_EVENTS_NAMES.ASSIST_DEFENDER, COMBAT_EVENTS_NAMES.ASSIST_BOMBER]}

class FILTER_MODIFICATORS:
    BY_ME = 'ByMe'
    BY_ALLY = 'ByAlly'
    BY_SQUAD = 'BySquad'
    BY_ENEMY = 'ByEnemy'
    DISABLED = 'Disabled'


class FilterManager(object):

    def __init__(self):
        self.__filterMap = {COMBAT_EVENTS_NAMES.KILL_DEFENDER: SETTINGS.KILL_DEFENDER,
         COMBAT_EVENTS_NAMES.KILL_BOMBER: SETTINGS.KILL_DEFENDER,
         COMBAT_EVENTS_NAMES.ASSISI_PLAYER_HEAVY: SETTINGS.ASSIST,
         COMBAT_EVENTS_NAMES.ASSIST_PLAYER_LIGHT: SETTINGS.ASSIST,
         COMBAT_EVENTS_NAMES.ASSIST_DEFENDER: SETTINGS.ASSIST_DEFENDER,
         COMBAT_EVENTS_NAMES.ASSIST_BOMBER: SETTINGS.ASSIST_DEFENDER}
        self.__filterModificators = {FILTER_MODIFICATORS.BY_ME: self.__filterByMe,
         FILTER_MODIFICATORS.BY_ALLY: self.__filterBySquad,
         FILTER_MODIFICATORS.BY_SQUAD: self.__filterByEnemy,
         FILTER_MODIFICATORS.BY_ENEMY: self.__filterByAlly}
        self._subFiltersMap = {SETTINGS.KILL_DEFENDER: [FILTER_MODIFICATORS.BY_ME,
                                  FILTER_MODIFICATORS.BY_ALLY,
                                  FILTER_MODIFICATORS.BY_SQUAD,
                                  FILTER_MODIFICATORS.BY_ENEMY],
         SETTINGS.ASSIST: [FILTER_MODIFICATORS.BY_ME, FILTER_MODIFICATORS.BY_ALLY, FILTER_MODIFICATORS.BY_SQUAD],
         SETTINGS.ASSIST_DEFENDER: [FILTER_MODIFICATORS.DISABLED]}

    def useFilter(self, filterName, playerInfo, killerInfo):
        if filterName not in self.__filterMap.keys():
            return True
        return self.__filterByID(self.__filterMap[filterName], playerInfo, killerInfo)

    def __filterByID(self, filterId, playerInfo, killerInfo):
        for filterModificator in self._subFiltersMap[filterId]:
            if filterModificator is FILTER_MODIFICATORS.DISABLED:
                return False

        if not SETTINGS.flags[filterId]:
            return False
        for filterModificator in self._subFiltersMap[filterId]:
            subFilterId = filterId + filterModificator
            if not SETTINGS.flags[subFilterId]:
                subFilter = self.__filterModificators[filterModificator]
                if subFilter(playerInfo, killerInfo):
                    return False

        return True

    def __filterByMe(self, playerInfo, killerInfo):
        if playerInfo['avatarID'] == killerInfo['avatarID']:
            return True
        return False

    def __filterBySquad(self, playerInfo, killerInfo):
        if playerInfo['avatarID'] != killerInfo['avatarID'] and playerInfo['squadID'] == killerInfo['squadID']:
            return True
        return False

    def __filterByAlly(self, playerInfo, killerInfo):
        if playerInfo['avatarID'] != killerInfo['avatarID'] and playerInfo['teamIndex'] == killerInfo['teamIndex']:
            return True
        return False

    def __filterByEnemy(self, playerInfo, killerInfo):
        if playerInfo['avatarID'] != killerInfo['avatarID'] and playerInfo['teamIndex'] != killerInfo['teamIndex']:
            return True
        return False