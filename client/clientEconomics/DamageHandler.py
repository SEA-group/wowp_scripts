# Embedded file name: scripts/client/clientEconomics/DamageHandler.py
import BigWorld
from clientEconomics.EconomicsModelView import EconomicsModelView
from economics.EconomicsConfigParser import PARAMS_FIELD, REWARD_FIELD, TEXT_FIELD

class DamageHandler(object):
    """Damage economic events handling logic
    """
    ATTACK_TIMEOUT = 3.5

    def __init__(self, configuration):
        self._configuration = configuration
        self._currentTargetID = 0
        self._targetIDWithAccumulatedDamage = 0
        self._targetAccumulator = 0
        self._lastTargetDamageTime = 0

    def handleDamageEvent(self, eventData):
        """Handle damage event received from server. Return event view data for HUD
        :param eventData: Event data received from server
        :return: (Gained battle points, Update view data)
        :rtype: (int, dict)
        """
        currentTime = BigWorld.time()
        eventID, rewardsAmount, victimID = self._unpackEventData(eventData)
        reward = self._getEventReward(eventID)
        if victimID != self._currentTargetID:
            self._lastTargetDamageTime = 0
        isAccumulatorTimeout = currentTime - self._lastTargetDamageTime > self.ATTACK_TIMEOUT
        if victimID != self._currentTargetID or isAccumulatorTimeout:
            self._currentTargetID = victimID
            self._targetAccumulator = 0
        totalReward = int(rewardsAmount * reward)
        updateViewData = None
        if totalReward != 0:
            self._targetAccumulator += totalReward
            accumulatorResetted = self._currentTargetID != self._targetIDWithAccumulatedDamage or isAccumulatorTimeout
            self._targetIDWithAccumulatedDamage = self._currentTargetID
            updateViewData = self._buildUpdateViewData(eventID, self._targetAccumulator, accumulatorResetted)
        elif isAccumulatorTimeout:
            self._targetIDWithAccumulatedDamage = 0
        self._lastTargetDamageTime = currentTime
        return (totalReward, updateViewData)

    def destroy(self):
        self._configuration = None
        return

    @staticmethod
    def _unpackEventData(eventData):
        """Unpack event data received from server
        :param eventData: Server event data
        :return: (eventID, rewards amount, victimID)
        :rtype: (str, int, int)
        """
        eventID, payload = eventData
        rewardsAmount, victimID = payload
        return (eventID, rewardsAmount, victimID)

    def _getEventReward(self, eventID):
        """Return battle points reward for specified event
        :param eventID: Event identifier
        :return: Battle points reward
        :rtype: int
        """
        eventConfiguration = self._configuration[eventID]
        return eventConfiguration[PARAMS_FIELD][REWARD_FIELD]

    def _getEventDescriptionText(self, eventID):
        """Return event description text localization tag
        :param eventID: Event identifier
        :return: Description localization tag
        :rtype: str
        """
        eventConfiguration = self._configuration[eventID]
        return eventConfiguration[PARAMS_FIELD][TEXT_FIELD]

    def _buildUpdateViewData(self, eventID, accumReward, accumResetted):
        """Build update view data based on event data
        """
        return {'type': EconomicsModelView.SIMPLE_EVENT_TYPE,
         'isNew': accumResetted,
         'description': self._getEventDescriptionText(eventID),
         'points': accumReward}