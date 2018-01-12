# Embedded file name: scripts/client/gui/HUD2/features/loading/LoadingManager.py
import BigWorld
import Settings
from EntityHelpers import EntityStates
from debug_utils import LOG_DEBUG
from gui.HUD2.StateManager import DELAY_BEFORE_BATTLE
LOADING = 1
INTRO = 2
PRE_BATTLE = 4
BATTLE = 8
STATE_MAP = {LOADING: 'LOADING',
 INTRO: 'INTRO',
 PRE_BATTLE: 'PRE_BATTLE',
 BATTLE: 'BATTLE_STATE'}
LOG_TAG = ' <<< LoadingManager >>> :  '
DELAY_SHOW_HINT = 4

class LoadingManager(object):

    def __init__(self, _gameEnvironment, model):
        self._model = model
        self._state = STATE_MAP[LOADING]
        self._gameEnvironment = _gameEnvironment
        self._gameEnvironment.eSkipLoading += self._skipLoading
        self._arenaIsLoaded = False

    def dispose(self):
        self._gameEnvironment.eSkipLoading -= self._skipLoading

    def update(self):
        if self._state == STATE_MAP[BATTLE]:
            self._model.preBattleHintAvailable = False
            return
        self._checkLoading()
        self._checkIntro()
        self._checkPreBattle()

    def skipIntro(self):
        LOG_DEBUG(LOG_TAG, 'skipIntro')
        if self._state == STATE_MAP[PRE_BATTLE]:
            if BigWorld.serverTime() < BigWorld.player().arenaStartTime - DELAY_SHOW_HINT:
                LOG_DEBUG(LOG_TAG, 'skipIntro SETTINGS')
                Settings.g_instance.preIntroEnabled = False
                self._model.preBattleHintAvailable = False
        if self._state == STATE_MAP[INTRO]:
            self._finishIntro()

    def _checkIntro(self):
        if self._state == STATE_MAP[LOADING]:
            if self._arenaIsLoaded:
                loadingDelay = 10
                if BigWorld.player().arenaStartTime > 0 and BigWorld.serverTime() > BigWorld.player().arenaStartTime - loadingDelay:
                    self._finishLoading(True)

    def _checkLoading(self):
        if self._state == STATE_MAP[INTRO]:
            preBattleDelay = 10
            if BigWorld.player().arenaStartTime > 0 and BigWorld.serverTime() > BigWorld.player().arenaStartTime - preBattleDelay:
                self._finishIntro()

    def _checkPreBattle(self):
        if self._state == STATE_MAP[PRE_BATTLE]:
            delay = DELAY_BEFORE_BATTLE
            if BigWorld.player().arenaStartTime > 0 and BigWorld.serverTime() > BigWorld.player().arenaStartTime - DELAY_SHOW_HINT:
                self._model.preBattleHintAvailable = False
            if BigWorld.player().arenaStartTime > 0 and BigWorld.serverTime() > BigWorld.player().arenaStartTime - delay:
                self._finishPreBattle()

    def arenaReady(self):
        self._arenaIsLoaded = True

    def _skipLoading(self):
        LOG_DEBUG(LOG_TAG, '_skipLoading')
        self._finishLoading(False)

    def _finishLoading(self, isSkipIntro):
        LOG_DEBUG(LOG_TAG, '_finishLoading')
        if EntityStates.inState(BigWorld.player(), EntityStates.DEAD | EntityStates.OBSERVER | EntityStates.DESTROYED | EntityStates.DESTROYED_FALL):
            LOG_DEBUG(LOG_TAG, 'eLoadingDeathFinished call')
            self._gameEnvironment.eLoadingDeathFinished()
            self._state = STATE_MAP[BATTLE]
            return
        self._model.preBattleHintAvailable = False
        if not Settings.g_instance.preIntroEnabled or isSkipIntro:
            self._finishIntro()
        else:
            self._state = STATE_MAP[INTRO]
            self._gameEnvironment.eLoadingFinished()

    def _finishIntro(self):
        LOG_DEBUG(LOG_TAG, '_finishIntro')
        self._state = STATE_MAP[PRE_BATTLE]
        self._gameEnvironment.eIntroFinished()
        if Settings.g_instance.preIntroEnabled:
            self._model.preBattleHintAvailable = True

    def _finishPreBattle(self):
        LOG_DEBUG(LOG_TAG, '_finishPreBattle')
        self._state = STATE_MAP[BATTLE]
        self._gameEnvironment.ePreBattleFinished()