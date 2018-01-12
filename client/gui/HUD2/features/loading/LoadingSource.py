# Embedded file name: scripts/client/gui/HUD2/features/loading/LoadingSource.py
import random
import BigWorld
import InputMapping
import Settings
from EntityHelpers import EntityStates
from clientConsts import PLANE_TYPE_NAME_HINTS
from debug_utils import LOG_DEBUG
from gui.HUD2.StateManager import DELAY_BEFORE_BATTLE
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.features.loading.LoadingManager import LoadingManager
from gui.HUD2.hudFeatures import Feature
from gui.Scaleform.UIHelper import getKeyLocalization

class PLANE_TYPE_NAME_HINTSself(object):
    pass


class LoadingSource(DataSource):

    def __init__(self, features):
        self._LOG_TAG = ' LoadingSource: :'
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._bigWorld = features.require(Feature.BIG_WORLD)
        self.inputProcessor = features.require(Feature.INPUT).commandProcessor
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._timer.eUpdate += self._onUpdate
        self.inputProcessor.addListeners(InputMapping.CMD_SKIP_INTRO, self._skipIntroCommandEvent)
        self._playerAvatar.eArenaLoaded += self._onArenaLoaded
        self._playerAvatar.eArenaLoadedAndReady += self._onArenaLoadedAndReady
        self._gameEnvironment.eLoadingProgress += self._onProgress
        self._model = features.require(Feature.GAME_MODEL).loading
        self._model.progress = 0
        self._loadingManager = LoadingManager(self._gameEnvironment, self._model)
        self._setBaseData()
        LOG_DEBUG(self._LOG_TAG, ' preIntroEnabled:   ', Settings.g_instance.preIntroEnabled)

    def _setBaseData(self):
        from db.DBLogic import g_instance as dbLogic
        self._hintList = dbLogic.getACHudHints().getHintByPlaneType(PLANE_TYPE_NAME_HINTS[self._playerAvatar.planeType])
        index = random.randint(0, self._hintList.__len__() - 1)
        hintData = self._hintList[index]
        self._model.planeHint = hintData.hintLocalizationID
        self._hintList = dbLogic.getACHudHints().getHintByPlaneType('common')
        index = random.randint(0, self._hintList.__len__() - 1)
        hintData = self._hintList[index]
        self._model.commonHint = hintData.commonHintLocalizationID
        self._model.preBattleHintSkipKey = getKeyLocalization(InputMapping.CMD_SKIP_INTRO)

    def _onProgress(self, progress):
        self._model.progress = progress

    def _onUpdate(self):
        self._loadingManager.update()

    def _onArenaLoadedAndReady(self):
        self._playerAvatar.eArenaLoadedAndReady -= self._onArenaLoadedAndReady
        self._loadingManager.arenaReady()
        serverTime = self._bigWorld.serverTime()
        arenaStartTime = self._playerAvatar.arenaStartTime
        currentTime = int(round(serverTime - arenaStartTime))
        self._model.timeBetweenFinishLoadingAndStartBattle = currentTime

    def _skipIntroCommandEvent(self):
        self._loadingManager.skipIntro()

    def _onArenaLoaded(self):
        self._playerAvatar.eArenaLoaded -= self._onArenaLoaded
        self._gameEnvironment.eLoadingProgress -= self._onProgress
        self._model.progress = 100

    def _addHint(self, hintData):
        self._model.hints.append(hintDescription=hintData.hintLocalizationID, hintIcoPath=hintData.hintIcoPath)

    def dispose(self):
        self._timer.eUpdate -= self._onUpdate()
        self._gameEnvironment.eLoadingProgress -= self._onProgress
        self._loadingManager.dispose()
        self._loadingManager = None
        self._playerAvatar = None
        self._gameEnvironment = None
        self._model = None
        self._arenaTypeData = None
        self._bigWorld = None
        self._hintData = None
        return