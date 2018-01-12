# Embedded file name: scripts/client/LockingTargetAdapter.py
import BigWorld
import GameEnvironment

class LockingTargetAdapter(object):

    def __init__(self, *battleStates):
        self._targetID = -1
        self._ownBattleStateTuple = battleStates
        self._currBattleState = None
        GameEnvironment.getInput().eBattleModeChange += self.__onBattleStateChange
        return

    def destroy(self):
        GameEnvironment.getInput().eBattleModeChange -= self.__onBattleStateChange

    def onSetTarget(self, targetID):
        if self._currBattleState in self._ownBattleStateTuple and targetID != self._targetID:
            self.__changeTarget(targetID)
            self._targetID = targetID

    def __onBattleStateChange(self, battleState):
        if battleState in self._ownBattleStateTuple:
            self.__changeTarget(self._targetID)
        self._currBattleState = battleState

    @staticmethod
    def __changeTarget(targetID):
        entity = BigWorld.entities.get(targetID)
        GameEnvironment.g_instance.eSetTargetEntity(entity)
        hud = GameEnvironment.getHUD()
        if hud is not None:
            hud.forestallingPoint.setTarget(entity)
        GameEnvironment.g_instance.eOnTargetEntity(targetID)
        BigWorld.player().setTargetEntityID(targetID)
        return