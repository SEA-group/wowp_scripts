# Embedded file name: scripts/client/clientEconomics/ClientEconomic.py
import BigWorld
from Event import EventDispatcher, Event, EventManager
from GameServiceBase import GameServiceBase
from clientEconomics.DamageHandler import DamageHandler
from clientEconomics.EconomicsModelView import EconomicsModelView
from economics.EconomicsConfigParser import getConfig, TYPE_FIELD, ID_FIELD, TEXT_FIELD, PARAMS_FIELD, REWARD_FIELD, LEVELS_FIELD, EXPERIENCE_FIELD, SUBJECT_FIELD, ACTION_FIELD, TITLE_FIELD, ICON_FIELD, EXPERIENCE_FIELDID_INLEVEL, COUNT_FIELDID_INLEVEL, SUBTYPE_FIELD
from economics.EconomicsConfigParser import PROCESSOR_SUBTYPES
from operator import itemgetter
from debug_utils import LOG_DEBUG

class ClientEconomic(EventDispatcher, GameServiceBase):
    """
    @type _modelView: gui.HUD2.features.battleEvent.BattleLogSource.BattleLogSource
    @type _totalExp: int
    """

    def __init__(self):
        super(ClientEconomic, self).__init__()
        self._modelView = None
        self._clientArena = None
        self._totalExp = None
        self._battlePoints = None
        self._shouldResetNewLine = False
        self._config = {conf[PARAMS_FIELD][ID_FIELD]:conf for conf in getConfig()}
        self._damageHandler = DamageHandler(self._config)
        return

    def init(self, gameEnvironment):
        player = BigWorld.player()
        self._totalExp = player.economicsMasteryPoints
        self._battlePoints = player.economicsBattlePoints
        self._clientArena = gameEnvironment.service('ClientArena')
        self.__eventManager = EventManager()
        self.onUpdateBattlePoints = Event(self.__eventManager)

    def assignModelView(self, modelView):
        self._modelView = modelView
        self._refreshModelViewPoints()

    def destroy(self):
        super(ClientEconomic, self).destroy()
        self._damageHandler.destroy()
        self._damageHandler = None
        self._modelView = None
        self._clientArena = None
        return

    @property
    def experience(self):
        return self._totalExp

    @property
    def battlePoints(self):
        return self._battlePoints

    def onEconomicEvents(self, events):
        viewEvents = list()
        for eventData in events:
            eventId = eventData[0]
            eventConfig = self._config[eventId][PARAMS_FIELD]
            text = eventConfig[TEXT_FIELD]
            subtype = eventConfig[SUBTYPE_FIELD]
            if self._config[eventId][TYPE_FIELD] == 'Damage':
                updateViewData = self._handleDamageEvent(eventData)
                if updateViewData:
                    viewEvents.append(updateViewData)
            elif LEVELS_FIELD in eventConfig:
                level = eventData[1]
                levels = eventConfig[LEVELS_FIELD]
                subject = eventConfig[SUBJECT_FIELD]
                action = eventConfig[ACTION_FIELD]
                if level >= len(levels):
                    LOG_DEBUG('ECOVIEW error: event level index overflow')
                exp = levels[level][EXPERIENCE_FIELDID_INLEVEL]
                count = levels[level][COUNT_FIELDID_INLEVEL]
                maxCount = max(map(itemgetter(COUNT_FIELDID_INLEVEL), levels))
                self._totalExp = max(self._totalExp + exp, 0)
                icon = eventConfig[ICON_FIELD]
                viewEvents.append({'type': EconomicsModelView.ACCUMULATIVE_EVENT_TYPE,
                 'eventID': eventId,
                 'description': action,
                 'rank': level,
                 'icon': icon,
                 'curValue': count,
                 'maxValue': maxCount})
                LOG_DEBUG('ECOVIEW: eventType = {0}, eventID {1}, subject {2}, action {3}, rank {4}, count {5}, icon {6}, curValue {7}, maxValue {8} :: totalExp{9}'.format(EconomicsModelView.ACCUMULATIVE_EVENT_TYPE, eventId, subject, action, level, count, icon, exp, maxCount, self._totalExp))
            elif REWARD_FIELD in eventConfig:
                reward = eventConfig[REWARD_FIELD]
                self._battlePoints = max(self._battlePoints + reward, 0)
                isDefender = False
                isBomber = False
                victimID = None
                isKill = len(eventData) == 2
                if isKill:
                    victimID = eventData[1]
                    avatarInfo = self._clientArena.getAvatarInfo(eventData[1])
                    if avatarInfo:
                        isDefender = bool(avatarInfo['defendSector'])
                        isBomber = avatarInfo['isBomber']
                if isKill and not isDefender and not isBomber:
                    viewEvents.append({'type': EconomicsModelView.KILL_EVENT_TYPE,
                     'description': text,
                     'avatarID': victimID,
                     'points': reward})
                    LOG_DEBUG('ECOVIEW: eventType = {0}, eventID {1}, description {2}, avatarID {3}, points {4} :: totalBP {5}'.format(EconomicsModelView.KILL_EVENT_TYPE, eventId, text, victimID, reward, self._battlePoints))
                isNew = True
                viewEvents.append({'type': EconomicsModelView.SIMPLE_EVENT_TYPE,
                 'isNew': isNew,
                 'description': text,
                 'points': reward})
                self._shouldResetNewLine = True
                LOG_DEBUG('ECOVIEW: eventType = {0}, eventID {1}, isNew {2}, description {3}, points {4} :: totalBP {5}'.format(EconomicsModelView.SIMPLE_EVENT_TYPE, eventId, isNew, text, reward, self._battlePoints))
            elif EXPERIENCE_FIELD in eventConfig:
                exp = eventConfig[EXPERIENCE_FIELD]
                self._totalExp = max(self._totalExp + exp, 0)
                if subtype == PROCESSOR_SUBTYPES.TEAM_ACTIONS:
                    viewEvents.append({'type': EconomicsModelView.TEAMACTIONS_EVENT_TYPE,
                     'eventID': eventId,
                     'description': text})
                    LOG_DEBUG('ECOVIEW: eventType = {0}, eventID {1}, exp {2}, decription {3} :: totalExp{4}'.format(EconomicsModelView.TEAMACTIONS_EVENT_TYPE, eventId, exp, text, self._totalExp))
                else:
                    icon = eventConfig[ICON_FIELD]
                    title = eventConfig[TITLE_FIELD]
                    viewEvents.append({'type': EconomicsModelView.SPECIAL_EVENT_TYPE,
                     'title': title,
                     'description': text,
                     'icon': icon})
                    LOG_DEBUG('ECOVIEW: eventType = {0}, text {1} :: totalExp{2}'.format(EconomicsModelView.SPECIAL_EVENT_TYPE, text, self._totalExp))

        if self._modelView:
            self._modelView.refresh(self._battlePoints, self._totalExp, viewEvents)
        self.onUpdateBattlePoints(self._battlePoints, self._totalExp)
        return

    def _handleDamageEvent(self, eventData):
        totalReward, updateViewData = self._damageHandler.handleDamageEvent(eventData)
        if totalReward != 0:
            self._battlePoints = max(self._battlePoints + totalReward, 0)
            self.onUpdateBattlePoints(self._battlePoints, self._totalExp)
        if updateViewData:
            updateViewData['isNew'] = updateViewData['isNew'] or self._shouldResetNewLine
            self._shouldResetNewLine = False
        LOG_DEBUG('ECOVIEW: _onDamage: eventData = {0}, updateViewData = {1}, totalBP = {2}'.format(eventData[0], updateViewData, self._battlePoints))
        return updateViewData

    def _refreshModelViewPoints(self):
        if self._modelView:
            self._modelView.refresh(self.battlePoints, self.experience, [])