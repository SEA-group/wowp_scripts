# Embedded file name: scripts/client/ArenaHelpers/GameModes/AreaConquest/AvatarComponents/TacticalRespawnAvatar.py
import functools
import BWLogging
import Event
logger = BWLogging.getLogger('TacticalRespawnAvatar')

def pauseInTacticalRespawn(func):
    """Decorator to pause and cache property updates while avatar is in
    tactical respawn to prevent inconsistent avatar state.
    On respawn end all queued updates will be triggered.
    Usage example:
    
        @pauseInTacticalRespawn
        def set_consumables(self, oldValue):
            ...
    
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.isInTacticalRespawn:
            self.queuePropertyUpdate(functools.partial(func, self, *args, **kwargs))
        else:
            func(self, *args, **kwargs)

    return wrapper


class ConditionsBarrier(object):

    def __init__(self, conditions, callback = None):
        self._conditions = conditions
        self._state = {condition:False for condition in conditions}
        self._unlockedCallback = callback

    def fireCondition(self, condition):
        logger.debug('fireCondition: condition = {0}, state = {1}'.format(condition, self._state))
        self._state[condition] = True
        if self.isUnlocked() and callable(self._unlockedCallback):
            self._unlockedCallback()

    def isUnlocked(self):
        return all((fired for fired in self._state.itervalues()))

    def reset(self):
        self._state = {condition:False for condition in self._conditions}

    def __str__(self):
        return 'ConditionsBarrier: state={0}'.format(self._state)


class TACTICAL_RESPAWN_CONDITION:
    FINISHED_FLAG = 'finished_flag'
    PART_STATES_RECEIVED = 'part_states_received'
    AVATAR_INFO_RECEIVED = 'avatar_info_received'
    ALL = (FINISHED_FLAG, PART_STATES_RECEIVED, AVATAR_INFO_RECEIVED)


class TacticalRespawnAvatarMixin(object):
    """Tactical respawn mixin for client Avatar class
    """
    tacticalRespawnInProgress = False

    def __init__(self):
        self._updatesQueue = []
        self._isInTacticalRespawn = False
        self._arenaProgressFinished = False
        self._serverProgressFinished = False
        self._tacticalRespawnBarrier = ConditionsBarrier(TACTICAL_RESPAWN_CONDITION.ALL, self.onTacticalRespawnEnd)
        self.__eManager = Event.EventManager()
        self.eTacticalRespawnBegin = Event.Event(self.__eManager)
        self.eTacticalRespawnEnd = Event.Event(self.__eManager)

    @property
    def isInTacticalRespawn(self):
        return self._isInTacticalRespawn

    def onTacticalRespawnBegin(self):
        logger.info('onTacticalRespawnBegin: id = {0}'.format(self.id))
        self._isInTacticalRespawn = True
        self._tacticalRespawnBarrier.reset()
        self.stopCollisionDetection()
        self.eTacticalRespawnBegin(self)

    def onTacticalRespawnEnd(self):
        if self.isInTacticalRespawn:
            logger.info('onTacticalRespawnEnd: id = {0}, queued updates count: {1}'.format(self.id, len(self._updatesQueue)))
            self.startCollisionDetection()
            for callback in self._updatesQueue:
                callback()

            self._updatesQueue = []
            self._isInTacticalRespawn = False
            self._onTacticalRespawnEndInternal()
            self.eTacticalRespawnEnd(self)

    def queuePropertyUpdate(self, callback):
        self._updatesQueue.append(callback)

    def onArenaAvatarInfoUpdated(self):
        if self.isInTacticalRespawn:
            logger.info('onArenaAvatarInfoUpdated: id = {0}'.format(self.id))
            self._tacticalRespawnBarrier.fireCondition(TACTICAL_RESPAWN_CONDITION.AVATAR_INFO_RECEIVED)

    def onPartStatesUpdated(self):
        if self.isInTacticalRespawn:
            logger.info('onPartStatesUpdated: id = {0}, value = {1}'.format(self.id, self.partStates))
            if self.partStates:
                self._tacticalRespawnBarrier.fireCondition(TACTICAL_RESPAWN_CONDITION.PART_STATES_RECEIVED)

    def set_tacticalRespawnInProgress(self, oldValue):
        """BigWorld callback for tacticalRespawnInProgress property change
        """
        logger.debug('set_tacticalRespawnInProgress: id = {0}, {1}, old value: {2}'.format(self.id, self.tacticalRespawnInProgress, oldValue))
        if self.tacticalRespawnInProgress:
            self.onTacticalRespawnBegin()
        else:
            self._tacticalRespawnBarrier.fireCondition(TACTICAL_RESPAWN_CONDITION.FINISHED_FLAG)

    def onLeaveWorld(self):
        self.__eManager.clear()
        self._tacticalRespawnBarrier = None
        return

    def _onTacticalRespawnEndInternal(self):
        """Internal handler for tactical respawn end process, child classes can override to add custom logic
        """
        pass