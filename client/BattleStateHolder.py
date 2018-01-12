# Embedded file name: scripts/client/BattleStateHolder.py
import BigWorld
import GameEnvironment
import InputMapping
import EffectManager
from clientConsts import SWITCH_STYLES_BUTTONS
from consts import BATTLE_MODE
from Avatar import ControllersNames

class BattleStateBase(object):
    """Base class for battle state objects
    """
    command = None
    battleModeID = None

    def __init__(self):
        self._isActive = False

    @property
    def isActive(self):
        """Indicate state activity status
        @rtype: bool
        """
        return self._isActive

    @property
    def isValid(self):
        """Indicate is activate possibility
        @return: bool
        """
        return True

    def activate(self):
        """Activate battle state
        """
        if self.isActive:
            return
        self._isActive = True
        self._setInputAxisBattleMode()
        self._syncInputCommandStatus()
        self._onActivate()

    def deactivate(self):
        """Deactivate battle state
        """
        if not self.isActive:
            return
        self._isActive = False
        self._syncInputCommandStatus()
        self._onDeactivate()

    def _setInputAxisBattleMode(self):
        """Set battle mode for input axis
        """
        GameEnvironment.getInput().inputAxis.setBattleState(self.battleModeID)

    def _syncInputCommandStatus(self):
        """Sync input command status with battle state status
        """
        if not self.command:
            return
        if InputMapping.g_instance.getSwitchingStyle(self.command) == SWITCH_STYLES_BUTTONS.SWITCH:
            GameEnvironment.getInput().commandProcessor.getCommand(self.command).isFired = self.isActive

    def _onActivate(self):
        """Custom activation logic. Child classes can override to add custom behaviour
        """
        pass

    def _onDeactivate(self):
        """Custom deactivation logic. Child classes can override to add custom behaviour
        """
        pass


class CombatBattleState(BattleStateBase):
    """Main battle state
    """
    battleModeID = BATTLE_MODE.COMBAT_MODE


class AssaultBattleState(BattleStateBase):
    """Bombing battle state
    """
    battleModeID = BATTLE_MODE.ASSAULT_MODE

    @property
    def command(self):
        return InputMapping.CMD_BATTLE_MODE

    def _onActivate(self):
        self._updateBombActivity(True)
        BigWorld.player().setBombHatchActivity(True)

    def _onDeactivate(self):
        self._updateBombActivity(False)
        BigWorld.player().setBombHatchActivity(False)

    @staticmethod
    def _updateBombActivity(active):
        EffectManager.g_instance.bomberCloudEffectVisible(active)
        sc = BigWorld.player().controllers.get(ControllersNames.SHELLS_CONTROLLER)
        if sc is not None:
            sc.setIsBombState(active)
        return


class GunnerBattleState(BattleStateBase):
    """Active gunner battle state
    """
    battleModeID = BATTLE_MODE.GUNNER_MODE

    @property
    def command(self):
        return InputMapping.CMD_GUNNER_MODE

    @property
    def isValid(self):
        return BigWorld.player().controllers.get(ControllersNames.TURRETS_LOGIC) is not None

    def _onActivate(self):
        self._updateGunnerActivity(True)

    def _onDeactivate(self):
        self._updateGunnerActivity(False)

    @staticmethod
    def _updateGunnerActivity(active):
        player = BigWorld.player()
        player.controlledGunner.activate(active)
        player.cell.clientTurretActivate(active)


class SniperBattleState(BattleStateBase):
    """Main battle state
    """
    battleModeID = BATTLE_MODE.SNIPER_MODE

    @property
    def command(self):
        return InputMapping.CMD_SNIPER_CAMERA


class BattleStateHolder(object):

    def __init__(self, mainState):
        self._currentState = None
        self._mainState = mainState
        self._stateInstances = {}
        return

    @property
    def mainState(self):
        """Main battle state. One of BATTLE_MODE.*
        @rtype: int
        """
        return self._mainState

    @property
    def currentState(self):
        """Current battle state. One of BATTLE_MODE.*
        @rtype: int
        """
        return self._currentState

    def addState(self, state, instance):
        """Add battle state
        @param state: One of BATTLE_STATE.*
        @param instance: Battle state instance
        """
        self._stateInstances[state] = instance

    def getStateInstance(self, state):
        """Current state instance
        @param state: One of BATTLE_STATE.*
        @rtype: BattleStateBase
        """
        return self._stateInstances[state]

    def activateState(self, state):
        """Activate state
        @param state: One of BATTLE_STATE.*
        """
        newState = self.getStateInstance(state)
        if newState.isValid:
            self._deactivateCurrentState()
            self._currentState = state
            newState.activate()

    def resetToMainState(self):
        self._deactivateCurrentState()
        self.activateState(self.mainState)

    def _deactivateCurrentState(self):
        if self.currentState:
            self.getStateInstance(self.currentState).deactivate()
            self._currentState = None
        return