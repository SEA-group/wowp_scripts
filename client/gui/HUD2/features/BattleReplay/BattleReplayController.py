# Embedded file name: scripts/client/gui/HUD2/features/BattleReplay/BattleReplayController.py
import BWLogging
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature

class BattleReplayController(DataController):

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).battleReplay

    @message('battleReplay.playPause')
    def playPause(self):
        self._logger.debug('playPause')
        self._model.source.playPause()

    @message('battleReplay.speedInc')
    def speedInc(self):
        self._logger.debug('speedInc')
        self._model.source.speedInc()

    @message('battleReplay.speedDec')
    def speedDec(self):
        self._logger.debug('speedDec')
        self._model.source.speedDec()

    @message('battleReplay.rewindForward')
    def rewindForward(self):
        self._logger.debug('rewindForward')
        self._model.source.rewindForward()

    @message('battleReplay.rewindBack')
    def rewindBack(self):
        self._logger.debug('rewindBack')
        self._model.source.rewindBack()

    @message('battleReplay.rewindBegin')
    def rewindBegin(self):
        self._logger.debug('rewindBegin')
        self._model.source.rewindBegin()

    @message('battleReplay.rewindTo')
    def rewindTo(self, time):
        self._logger.debug('rewindTo {0}'.format(time))
        self._model.source.rewindTo(time)