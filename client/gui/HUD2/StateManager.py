# Embedded file name: scripts/client/gui/HUD2/StateManager.py
import sys
import weakref
import BigWorld
import InputMapping
from EntityHelpers import EntityStates
from Event import Event
from StateMachine import ExternalBitStateMachine
from clientConsts import SPECTATOR_TYPE
from debug_utils import LOG_DEBUG
from gui import Cursor
from gui.HUD2.features.Respawn.RespawnSilentCheckManager import RespawnSilentCheckManager
from gui.HUD2.hudFeatures import Feature
from consts import HINTS_TYPE
from HUDStatesEffectsController import HUDStatesEffectsController
LOADING_FINISHED = 1
INTRO_FINISHED = 2
ON_DEATH = 8
ON_WAITE_RESPAWN = 16
HAS_CONTROL = 32
TAB_DOWN = 64
TAB_UP = 128
ON_END_RESPAWN = 256
ON_OUTRO = 512
ON_PRE_BATTLE_FINISH = 1024
HELP_PRESS_DOWN = 16384
HELP_PRESS_UP = 32768
ON_GO_TO_TACTICAL_SPECTATOR = 2097152
ON_GO_TO_SPECTATOR = 262144
ON_GO_BACK = 524288
EMPTY = 65536
ON_WAITE_DISABLED_RESPAWN = 4194304
ON_GO_BACK_NO_RESPAWN = 8388608
TOGGLE_PROMO = 1073741824
LOADING = 1
INTRO = 2
BATTLE_DEFAULT = 4
BATTLE_STATS = 8
OUTRO = 32
DEATH_STATE = 64
DEATH_TAB_STATE = 8388608
RESPAWN_STATE = 4194304
LOADING_TAB = 256
INTRO_TAB = 512
RESPAWN_TAB = 1024
PRE_BATTLE = 2048
PRE_BATTLE_TAB = 4096
SPECTATOR_STATE = 32768
SPECTATOR_TAB_STATE = 65536
SPECTATOR_TACTICAL_STATE = 131072
SPECTATOR_TAB_TACTICAL_STATE = 262144
OUTRO_TAB = 524288
RESPAWN_DISABLED_STATE = 1048576
RESPAWN_DISABLED_TAB_STATE = 2097152
PROMO_STATE = 1073741824
BATTLE = BATTLE_DEFAULT | BATTLE_STATS
INTERMISSION_FORCECLOSE_STATES = OUTRO
INTERMISSION_READY_STATES = (INTRO | PRE_BATTLE | BATTLE_DEFAULT | RESPAWN_STATE | RESPAWN_DISABLED_STATE | SPECTATOR_STATE | SPECTATOR_TACTICAL_STATE | DEATH_STATE) & ~INTERMISSION_FORCECLOSE_STATES
INTERMISSION_HIERARHY = {'TOP': 20,
 'MENU': 10,
 'HELP': 5}
RESPAWN_STATES = RESPAWN_STATE | RESPAWN_TAB | RESPAWN_DISABLED_STATE | RESPAWN_DISABLED_TAB_STATE
MOUSE_VISIBILITY_STATES = LOADING | LOADING_TAB | INTRO_TAB | PRE_BATTLE_TAB | BATTLE_STATS | RESPAWN_STATE | RESPAWN_TAB | RESPAWN_DISABLED_STATE | RESPAWN_DISABLED_TAB_STATE | SPECTATOR_TAB_STATE | SPECTATOR_TAB_TACTICAL_STATE | OUTRO | OUTRO_TAB
SPECTATOR_STATES = SPECTATOR_TAB_STATE | SPECTATOR_STATE
ALL_SPECTATOR_STATES = SPECTATOR_STATES | SPECTATOR_TAB_TACTICAL_STATE | SPECTATOR_TACTICAL_STATE
SPECTATOR_READY_STATES = RESPAWN_STATE | RESPAWN_TAB | RESPAWN_DISABLED_STATE | RESPAWN_DISABLED_TAB_STATE | DEATH_STATE | DEATH_TAB_STATE | LOADING | LOADING_TAB
CINEMA_SPECTATOR_READY_STATES = RESPAWN_STATE | RESPAWN_DISABLED_STATE | SPECTATOR_STATE
TACTICAL_SPECTATOR_READY_STATES = RESPAWN_STATE | RESPAWN_DISABLED_STATE | SPECTATOR_TACTICAL_STATE
RESPAWN_SILENT_CHECK_STATES = RESPAWN_STATE | RESPAWN_DISABLED_STATE
ANY_STATE = sys.maxint
STATE_MAP = {LOADING: 'LOADING_STATE',
 LOADING_TAB: 'LOADING_TAB_STATE',
 INTRO_TAB: 'INTRO_TAB_STATE',
 RESPAWN_TAB: 'RESPAWN_TAB_STATE',
 INTRO: 'INTRO_STATE',
 BATTLE_DEFAULT: 'NORMAL_STATE',
 BATTLE_STATS: 'TAB_STATE',
 OUTRO: 'OUTRO_STATE',
 OUTRO_TAB: 'OUTRO_TAB_STATE',
 RESPAWN_STATE: 'RESPAWN_STATE',
 DEATH_STATE: 'DEATH_STATE',
 DEATH_TAB_STATE: 'DEATH_TAB_STATE',
 PRE_BATTLE: 'PRE_BATTLE_STATE',
 PRE_BATTLE_TAB: 'PRE_BATTLE_TAB_STATE',
 SPECTATOR_STATE: 'SPECTATOR_STATE',
 SPECTATOR_TAB_STATE: 'SPECTATOR_TAB_STATE',
 SPECTATOR_TACTICAL_STATE: 'TACTIC_SPECTATOR_STATE',
 SPECTATOR_TAB_TACTICAL_STATE: 'TACTIC_SPECTATOR_TAB_STATE',
 RESPAWN_DISABLED_STATE: 'RESPAWN_DISABLED_STATE',
 RESPAWN_DISABLED_TAB_STATE: 'RESPAWN_DISABLED_TAB_STATE',
 PROMO_STATE: 'PROMO_STATE'}
DELAY_BEFORE_BATTLE = 1

class IntermissionStateManager:

    def __init__(self, owner, cbOnActivityChanged, cbOnInterOpen, cbOnInterClose, cbOnInterCloseForce):
        self._ownerManager = weakref.ref(owner)
        self._intermission = False
        self._currentWindow = None
        self._onActivityChanged = cbOnActivityChanged
        self._onInterOpen = cbOnInterOpen
        self._onInterClose = cbOnInterClose
        self._onInterCloseForce = cbOnInterCloseForce
        return

    def dispose(self):
        self._onInterOpen = None
        self._onInterClose = None
        self._onInterCloseForce = None
        self._ownerManager = None
        return

    def __setActive(self, active):
        LOG_DEBUG('IntermissionStateManager.Activate({0})'.format(active))
        self._intermission = active
        self._onActivityChanged(self._intermission)

    @property
    def isActive(self):
        return self._intermission

    def __openInterWindow(self, windowType):
        oldState = self._currentWindow and INTERMISSION_HIERARHY[windowType] > INTERMISSION_HIERARHY[self._currentWindow]
        if not self._currentWindow or oldState:
            if oldState:
                stateTransition = self._currentWindow + '>' + windowType
                self._onInterClose(stateTransition)
            self._currentWindow = windowType
            self._onInterOpen(windowType)
            self.__setActive(True)

    def __closeInterWindow(self, windowType):
        if windowType == 'TOP':
            self._onInterClose(windowType)
            self._currentWindow = None
        elif windowType == self._currentWindow:
            self._onInterClose(windowType)
            self._currentWindow = None
        return

    def onIntermissionPress(self, currStateId):
        stateIsHigh = self._currentWindow and INTERMISSION_HIERARHY[self._currentWindow] > INTERMISSION_HIERARHY['MENU']
        if not self._currentWindow == 'MENU' and not stateIsHigh:
            if currStateId & INTERMISSION_READY_STATES != 0:
                self.__openInterWindow('MENU')
        else:
            self.__closeInterWindow('TOP')

    def onHelpPress(self, pressed, currStateId):
        if currStateId & INTERMISSION_READY_STATES == 0:
            return
        if pressed:
            self.__openInterWindow('HELP')
        else:
            self.__closeInterWindow('HELP')

    def validateState(self, currStateId):
        if self._intermission and currStateId & INTERMISSION_FORCECLOSE_STATES != 0:
            self._onInterCloseForce()

    def onAllIntermissionClosed(self):
        self.__setActive(False)
        self._currentWindow = None
        return


class StateManager:

    def __init__(self):
        self._stateId = LOADING
        self._stateName = STATE_MAP[self._stateId]
        self._stateMachine = None
        self._goBackSignalID = ON_GO_BACK
        self._awaitLoadPlaneResources = False
        self._createEvents()
        self._createStateMachine()
        self._initStateMachine()
        self._interManager = IntermissionStateManager(self, self._onIntermissionActivityChanged, self.eOpenInter, self.eCloseInter, self.eCloseInterForce)
        self._initStatesEffectController()
        self.___endDeathStateCallback = None
        return

    def _initStatesEffectController(self):
        from HUDStatesEffectsSettings import EFFECTS_MAP
        from EffectManager import g_instance
        self._statesEffectsCtrl = HUDStatesEffectsController(EFFECTS_MAP, g_instance)

    @property
    def state(self):
        return self._stateName

    def _createEvents(self):
        self.eStateChanged = Event()
        self.eToggleHUDVisibility = Event()
        self.eOpenInter = Event()
        self.eCloseInter = Event()
        self.eCloseInterForce = Event()

    def _createStateMachine(self):
        stateMapReverse = dict(((v, k) for k, v in STATE_MAP.iteritems()))

        def stateSetter(stateID, *args):
            self._onStateChanged(stateID)

        def stateGetter():
            return stateMapReverse.get(self._stateName, None)

        self._stateMachine = ExternalBitStateMachine(stateSetter, stateGetter, None)
        return

    def _initStateMachine(self):
        self._stateMachine.addState(LOADING, None, None)
        self._stateMachine.addState(INTRO, None, None)
        self._stateMachine.addState(BATTLE_DEFAULT, None, None)
        self._stateMachine.addState(BATTLE_STATS, None, None)
        self._stateMachine.addState(OUTRO, None, None)
        self._stateMachine.addState(OUTRO_TAB, None, None)
        self._stateMachine.addState(RESPAWN_STATE, None, None)
        self._stateMachine.addState(DEATH_STATE, None, None)
        self._stateMachine.addState(DEATH_TAB_STATE, None, None)
        self._stateMachine.addState(LOADING_TAB, None, None)
        self._stateMachine.addState(INTRO_TAB, None, None)
        self._stateMachine.addState(RESPAWN_TAB, None, None)
        self._stateMachine.addState(RESPAWN_DISABLED_STATE, None, None)
        self._stateMachine.addState(RESPAWN_DISABLED_TAB_STATE, None, None)
        self._stateMachine.addState(PROMO_STATE, None, None)
        self._stateMachine.addTransition(LOADING, LOADING_TAB, TAB_DOWN)
        self._stateMachine.addTransition(LOADING_TAB, LOADING, TAB_UP)
        self._stateMachine.addTransition(LOADING | LOADING_TAB, BATTLE_DEFAULT, LOADING_FINISHED)
        self._stateMachine.addTransition(LOADING | LOADING_TAB, INTRO, HAS_CONTROL, lambda *args, **kwargs: self._showStartHint())
        self._stateMachine.addTransition(DEATH_STATE, DEATH_TAB_STATE, TAB_DOWN)
        self._stateMachine.addTransition(DEATH_TAB_STATE, DEATH_STATE, TAB_UP)
        self._stateMachine.addTransition(INTRO, INTRO_TAB, TAB_DOWN)
        self._stateMachine.addTransition(INTRO_TAB, INTRO, TAB_UP)
        self._stateMachine.addTransition(INTRO | LOADING, PRE_BATTLE, INTRO_FINISHED, lambda *args, **kwargs: self._showStartHint())
        self._stateMachine.addTransition(LOADING_TAB, PRE_BATTLE_TAB, INTRO_FINISHED, lambda *args, **kwargs: self._showStartHint())
        self._stateMachine.addTransition(INTRO_TAB, PRE_BATTLE_TAB, INTRO_FINISHED)
        self._stateMachine.addTransition(INTRO | INTRO_TAB | LOADING | LOADING_TAB, BATTLE_DEFAULT, ON_PRE_BATTLE_FINISH, lambda *args, **kwargs: self._showStartHint())
        self._stateMachine.addTransition(PRE_BATTLE, BATTLE_DEFAULT, ON_PRE_BATTLE_FINISH, lambda *args, **kwargs: self._goToBattle())
        self._stateMachine.addTransition(PRE_BATTLE_TAB, BATTLE_STATS, ON_PRE_BATTLE_FINISH, lambda *args, **kwargs: self._goToBattle())
        self._stateMachine.addTransition(PRE_BATTLE, PRE_BATTLE_TAB, TAB_DOWN)
        self._stateMachine.addTransition(PRE_BATTLE_TAB, PRE_BATTLE, TAB_UP)
        self._stateMachine.addTransition(RESPAWN_STATE, RESPAWN_TAB, TAB_DOWN)
        self._stateMachine.addTransition(RESPAWN_TAB, RESPAWN_STATE, TAB_UP)
        self._stateMachine.addTransition(RESPAWN_STATE | SPECTATOR_STATE | SPECTATOR_TACTICAL_STATE, BATTLE_DEFAULT, ON_END_RESPAWN, lambda *args, **kwargs: self._onRespawn())
        self._stateMachine.addTransition(RESPAWN_TAB | SPECTATOR_TAB_STATE | SPECTATOR_TAB_TACTICAL_STATE, BATTLE_STATS, ON_END_RESPAWN)
        self._stateMachine.addTransition(RESPAWN_DISABLED_STATE, RESPAWN_DISABLED_TAB_STATE, TAB_DOWN)
        self._stateMachine.addTransition(RESPAWN_DISABLED_TAB_STATE, RESPAWN_DISABLED_STATE, TAB_UP)
        self._stateMachine.addTransition(SPECTATOR_READY_STATES, SPECTATOR_STATE, ON_GO_TO_SPECTATOR, lambda *args, **kwargs: self._onSetSpectatorType(SPECTATOR_TYPE.CINEMATIC))
        self._stateMachine.addTransition(SPECTATOR_READY_STATES, SPECTATOR_TACTICAL_STATE, ON_GO_TO_TACTICAL_SPECTATOR, lambda *args, **kwargs: self._onSetSpectatorType(SPECTATOR_TYPE.TACTICAL))
        self._stateMachine.addTransition(ALL_SPECTATOR_STATES, RESPAWN_STATE, ON_GO_BACK, lambda *args, **kwargs: self._onSetSpectatorType(SPECTATOR_TYPE.NONE))
        self._stateMachine.addTransition(ALL_SPECTATOR_STATES, RESPAWN_DISABLED_STATE, ON_GO_BACK_NO_RESPAWN, lambda *args, **kwargs: self._onSetSpectatorType(SPECTATOR_TYPE.NONE))
        self._stateMachine.addTransition(SPECTATOR_STATE, SPECTATOR_TAB_STATE, TAB_DOWN)
        self._stateMachine.addTransition(SPECTATOR_TAB_STATE, SPECTATOR_STATE, TAB_UP)
        self._stateMachine.addTransition(SPECTATOR_TACTICAL_STATE, SPECTATOR_TAB_TACTICAL_STATE, TAB_DOWN)
        self._stateMachine.addTransition(SPECTATOR_TAB_TACTICAL_STATE, SPECTATOR_TACTICAL_STATE, TAB_UP)
        self._stateMachine.addTransition(BATTLE_DEFAULT | BATTLE_STATS, DEATH_STATE, ON_DEATH)
        self._stateMachine.addTransition(DEATH_STATE | DEATH_TAB_STATE, RESPAWN_STATE, ON_WAITE_RESPAWN)
        self._stateMachine.addTransition(LOADING | LOADING_TAB, RESPAWN_STATE, ON_WAITE_RESPAWN, lambda *args, **kwargs: self._connectToSpectator())
        self._stateMachine.addTransition(DEATH_STATE | DEATH_TAB_STATE, RESPAWN_DISABLED_STATE, ON_WAITE_DISABLED_RESPAWN, lambda *args, **kwargs: self._onRespawnDisabled())
        self._stateMachine.addTransition(LOADING | LOADING_TAB, RESPAWN_DISABLED_STATE, ON_WAITE_DISABLED_RESPAWN, lambda *args, **kwargs: self._connectToSpectator())
        self._stateMachine.addTransition(BATTLE_DEFAULT, BATTLE_STATS, TAB_DOWN)
        self._stateMachine.addTransition(BATTLE_STATS, BATTLE_DEFAULT, TAB_UP)
        self._stateMachine.addTransition(BATTLE_DEFAULT | BATTLE_STATS | RESPAWN_STATES | ALL_SPECTATOR_STATES | DEATH_STATE | DEATH_TAB_STATE, OUTRO, ON_OUTRO)
        self._stateMachine.addTransition(OUTRO, OUTRO_TAB, TAB_DOWN)
        self._stateMachine.addTransition(OUTRO_TAB, OUTRO, TAB_UP)
        self._stateMachine.addTransition(PROMO_STATE, BATTLE_DEFAULT, TOGGLE_PROMO)
        self._stateMachine.addTransition(ANY_STATE, PROMO_STATE, TOGGLE_PROMO)
        return

    def initSignals(self, features):
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._respawnModel = features.require(Feature.GAME_MODEL).respawn
        self._camera = features.require(Feature.CAMERA)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        inputProcessor = features.require(Feature.INPUT).commandProcessor
        sm = self._stateMachine
        inputProcessor.addListeners(InputMapping.CMD_VISIBILITY_HUD, None, None, self._onHUDVisibilityCommand)
        inputProcessor.addListeners(InputMapping.CMD_NEXT_VEHICLE_WHEN_DEAD, lambda : self._playerAvatar.switchObservee())
        inputProcessor.addListeners(InputMapping.CMD_INTERMISSION_MENU, self._onIntermissionPress)
        inputProcessor.addListeners(InputMapping.CMD_SHOW_TEAMS, lambda : self._onTabPressed(True), lambda : self._onTabPressed(False))
        inputProcessor.addListeners(InputMapping.CMD_HELP, lambda : self._onHelpPressed(True), lambda : self._onHelpPressed(False))
        inputProcessor.addListeners(InputMapping.CMD_GO_TO_SPECTATOR, lambda : self._onGoToSpectatorCommand(ON_GO_TO_SPECTATOR))
        inputProcessor.addListeners(InputMapping.CMD_GO_TO_TACTICAL_SPECTATOR, lambda : self._onGoToSpectatorCommand(ON_GO_TO_TACTICAL_SPECTATOR))
        inputProcessor.addListeners(InputMapping.CMD_SKIP_DEATH, self._skipDeath)
        inputProcessor.addListeners(InputMapping.CMD_SKIP_OUTRO, self._skipOutro)
        self._gameEnvironment.eIntroFinished += self._onIntroFinish
        self._gameEnvironment.eLoadingFinished += self._eLoadingFinished
        self._gameEnvironment.ePreBattleFinished += self._ePreBattleFinished
        self._gameEnvironment.eLoadingDeathFinished += self._eLoadingDeathFinished
        self._gameEnvironment.eAllIntreClosed += self._eAllIntreClosed
        self._gameEnvironment.eTogglePromoHUD += self.onPromoHUDToggle
        self._playerAvatar.onStateChanged += self._onPlayerStateChanged
        self._playerAvatar.eTacticalRespawnEnd += self._onTacticalRespawnEnd
        self._playerAvatar.eUpdateSpectator += self._onObserveeChanged
        self._playerAvatar.ePlaneModelLoaded += self._onPlaneModelLoaded
        self._clientArena.onBeforePlaneChanged += self._onBeforePlayerPlaneChanged
        self._addPredicates(inputProcessor)
        self._addAdditionalManager(features)
        return

    def _onStateChanged(self, newStateId):
        self._interManager.validateState(newStateId)
        self._stateId = newStateId
        self._stateName = STATE_MAP[newStateId]
        self.eStateChanged(self._stateName)
        self._updateDenyCursorHide()
        self.checkMouseState()
        self._updateAdditionalManager()
        self._statesEffectsCtrl.onHUDStateChanged(newStateId)

    def _updateAdditionalManager(self):
        self._respManager.changeState(self._stateId)

    def _addAdditionalManager(self, features):
        self._respManager = RespawnSilentCheckManager(features, RESPAWN_SILENT_CHECK_STATES)
        self._respManager.eRestDelay += self._onRespDelay

    def _onRespDelay(self):
        self._onGoToSpectatorCommand(ON_GO_TO_SPECTATOR)

    def _updateDenyCursorHide(self):
        self._gameEnvironment.eOnDenyCursorHideChanged(self._cursorVisibility())

    def _cursorVisibility(self):
        return self._interManager.isActive or self._stateId & MOUSE_VISIBILITY_STATES != 0

    def _onSetSpectatorType(self, sType, *args, **kwargs):
        self._playerAvatar.activateTacticalSpectator(sType)
        self._camera.onTacticalSpectator(self._playerAvatar.spectatorTypeWithTacticalMode)

    def _onObserveeChanged(self, newObserveeID):
        LOG_DEBUG('_onObserveeChanged', newObserveeID)
        if BigWorld.player().isObserverToBattleTransition:
            return
        if newObserveeID == 0:
            self._stateMachine.signal(self._goBackSignalID)

    def _onObserveeLost(self):
        if self.isRespawnAvailable():
            self._stateMachine.signal(self._goBackSignalID)
        else:
            self._stateMachine.signal(ON_GO_TO_SPECTATOR)

    def _onIntermissionActivityChanged(self, active):
        self._updateDenyCursorHide()

    def _onRespawnDisabled(self, *args, **kwargs):
        self._goBackSignalID = ON_GO_BACK_NO_RESPAWN

    def _onHUDVisibilityCommand(self, *args, **kwargs):
        LOG_DEBUG('HUD visibility command received')
        self.eToggleHUDVisibility()

    def _onIntermissionPress(self):
        chat = self._gameEnvironment.service('Chat')
        gamePlayHints = self._gameEnvironment.service('GamePlayHints')
        LOG_DEBUG('STATES TEST :  _onIntermissionPress ', self._stateId)
        if gamePlayHints.hintVisible:
            self._gameEnvironment.eDisableStartHint()
        elif chat.chatVisible:
            chat.hideChat()
        elif self._stateId & SPECTATOR_STATES:
            self._stateMachine.signal(self._goBackSignalID)
        else:
            self._stateMachine.signal(TAB_UP)
            self._interManager.onIntermissionPress(self._stateId)

    def _onHelpPressed(self, pressed):
        LOG_DEBUG('STATES TEST :  _onHelpPressed ', self._stateId)
        self._interManager.onHelpPress(pressed, self._stateId)

    def _onTabPressed(self, pressed):
        LOG_DEBUG('STATES TEST :  _onTabPressed ', self._stateId)
        if not self._interManager.isActive:
            if pressed:
                self._stateMachine.signal(TAB_DOWN)
            else:
                self._stateMachine.signal(TAB_UP)

    def _onBeforePlayerPlaneChanged(self, avatarID):
        if BigWorld.player().id == avatarID:
            self._awaitLoadPlaneResources = True

    def _onPlaneModelLoaded(self):
        if self._awaitLoadPlaneResources and BigWorld.player().state & EntityStates.GAME:
            self._stateMachine.signal(ON_END_RESPAWN)
        self._awaitLoadPlaneResources = False

    def _goToBattle(self, *args, **kwargs):
        """Reset camera for player to avoid some issues related to reconnect
        """
        self._camera.reset()
        self._requestShootingHint()

    def _onRespawn(self, *args, **kwargs):
        """Reset camera for player to avoid some issues related to reconnect
        """
        self._requestShootingHint()

    def _showStartHint(self, *args, **kwargs):
        """Reset camera for player to avoid some issues related to reconnect
        """
        gamePlayHints = self._gameEnvironment.service('GamePlayHints')
        if self._playerAvatar.startHintAvailable and not gamePlayHints.hintVisible:
            self._gameEnvironment.eShowHint(HINTS_TYPE.START)

    def _connectToSpectator(self, *args, **kwargs):
        self._playerAvatar.skipDeadFallState()
        self._camera.switchToSpectator()

    def _onGoToSpectatorCommand(self, signalID):
        if self._stateId & ALL_SPECTATOR_STATES:
            self._stateMachine.signal(self._goBackSignalID)
        else:
            if self._playerAvatar.observeeID == 0:
                self._playerAvatar.switchObservee()
                return
            self._stateMachine.signal(signalID)

    def _requestShootingHint(self):
        if self._playerAvatar.shootingHintAvailable and not self._playerAvatar.startHintAvailable:
            self._gameEnvironment.eShowHint(HINTS_TYPE.SHOOTING)

    def isRespawnAvailable(self):
        return self._respawnModel.respawnAmount.get() != 0

    def goToCinemaSpectatorPredicate(self):
        res = self._stateId & CINEMA_SPECTATOR_READY_STATES
        return res

    def goToTacticalSpectatorPredicate(self):
        res = self._stateId & TACTICAL_SPECTATOR_READY_STATES
        return res

    def isChatAvailable(self):
        res = not self._stateId & SPECTATOR_STATES
        return res

    def _addPredicates(self, processor):
        processor.addPredicate(InputMapping.CMD_GO_TO_SPECTATOR, self.goToCinemaSpectatorPredicate)
        processor.addPredicate(InputMapping.CMD_GO_TO_TACTICAL_SPECTATOR, self.goToTacticalSpectatorPredicate)
        processor.addPredicate(InputMapping.CMD_GO_BACK, self.isRespawnAvailable)
        processor.addPredicate(InputMapping.CMD_CHAT, self.isChatAvailable)

    def _skipOutro(self):
        if self._stateName == STATE_MAP[OUTRO]:
            self._playerAvatar.exitGame()

    def _skipDeath(self):
        if self._stateName == STATE_MAP[DEATH_STATE] or self._stateName == STATE_MAP[DEATH_TAB_STATE]:
            LOG_DEBUG(' STATES TEST :  _skipDeath ')
            signalID = ON_WAITE_RESPAWN if self.isRespawnAvailable() else ON_WAITE_DISABLED_RESPAWN
            BigWorld.callback(0, lambda : self._stateMachine.signal(signalID))

    def _eAllIntreClosed(self):
        LOG_DEBUG('STATES TEST :  onAllIntreClosed ')
        self._interManager.onAllIntermissionClosed()
        self.checkMouseState()

    def checkMouseState(self):
        Cursor.forceShowCursor(self._cursorVisibility())
        if self._stateId == BATTLE_DEFAULT and not self._interManager.isActive:
            self._playerAvatar.setFlyMouseInputAllowed(True)
        else:
            self._playerAvatar.setFlyMouseInputAllowed(False)

    def _onIntroFinish(self):
        LOG_DEBUG('STATES TEST :  _onIntroFinish ')
        self._stateMachine.signal(INTRO_FINISHED)

    def _eLoadingFinished(self):
        LOG_DEBUG('STATES TEST :  eLoadingFinished ')
        self._stateMachine.signal(HAS_CONTROL)

    def _ePreBattleFinished(self):
        LOG_DEBUG('STATES TEST :  _ePreBattleFinished ')
        self._stateMachine.signal(ON_PRE_BATTLE_FINISH)

    def _eLoadingDeathFinished(self):
        LOG_DEBUG(' STATES TEST :  _eLoadingDeathFinished ')
        self._endDeathState()

    def _onPlayerStateChanged(self, oldState, state):
        LOG_DEBUG(' STATES TEST :  currentState : ', EntityStates.getStateName(state))
        if state & (EntityStates.DESTROYED | EntityStates.DESTROYED_FALL):
            if oldState & EntityStates.GAME_CONTROLLED:
                LOG_DEBUG(' STATES TEST : ', 'DEAD')
                self._stateMachine.signal(ON_DEATH)
                self.___endDeathStateCallback = BigWorld.callback(10, self._endDeathState)
        if state & EntityStates.GAME:
            LOG_DEBUG('STATES TEST : ', 'START GAME AFTER RESPAWN')
            if not self._awaitLoadPlaneResources:
                self._stateMachine.signal(ON_END_RESPAWN)
        if state & EntityStates.OUTRO:
            LOG_DEBUG(' STATES TEST : ', ' OUTRO ')
            self._stateMachine.signal(ON_OUTRO)

    def _onTacticalRespawnEnd(self, *args, **kwargs):
        LOG_DEBUG(' STATES TEST : _onTacticalRespawnEnd')

    def _endDeathState(self):
        if self._stateName == STATE_MAP[DEATH_STATE] or self._stateName == STATE_MAP[DEATH_TAB_STATE] or self._stateName == STATE_MAP[LOADING]:
            signalID = ON_WAITE_RESPAWN if self.isRespawnAvailable() else ON_WAITE_DISABLED_RESPAWN
            self._stateMachine.signal(signalID)

    def onPromoHUDToggle(self):
        self._stateMachine.signal(TOGGLE_PROMO)

    def dispose(self):
        if self.___endDeathStateCallback:
            BigWorld.cancelCallback(self.___endDeathStateCallback)
            self.___endDeathStateCallback = None
        self._statesEffectsCtrl.destroy()
        self._statesEffectsCtrl = None
        self._interManager.dispose()
        self._interManager = None
        self._respManager.eRestDelay -= self._onRespDelay
        self._respManager = None
        self._gameEnvironment.eIntroFinished -= self._onIntroFinish
        self._gameEnvironment.eLoadingFinished -= self._eLoadingFinished
        self._gameEnvironment.ePreBattleFinished -= self._ePreBattleFinished
        self._gameEnvironment.eLoadingDeathFinished -= self._eLoadingDeathFinished
        self._gameEnvironment.eAllIntreClosed -= self._eAllIntreClosed
        self._gameEnvironment.eTogglePromoHUD -= self.onPromoHUDToggle
        self._playerAvatar.onStateChanged -= self._onPlayerStateChanged
        self._playerAvatar.eTacticalRespawnEnd -= self._onTacticalRespawnEnd
        self._playerAvatar.eUpdateSpectator -= self._onObserveeChanged
        self._playerAvatar.ePlaneModelLoaded -= self._onPlaneModelLoaded
        self._clientArena.onBeforePlaneChanged -= self._onBeforePlayerPlaneChanged
        self._playerAvatar = None
        self._gameEnvironment = None
        self._respawnModel = None
        self._camera = None
        self.eStateChanged.clear()
        self._stateMachine.destroy()
        return