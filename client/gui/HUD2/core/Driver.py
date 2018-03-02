# Embedded file name: scripts/client/gui/HUD2/core/Driver.py
from DataView import ProxyView
from Protocol import ScaleformProtocol
from debug_utils import LOG_DEBUG

class ScaleformDriver(object):

    def __init__(self, messageRouter, model):
        LOG_DEBUG('ScaleformDriver initialized')
        self._model = model
        self._messageRouter = messageRouter
        self._protocol = None
        self._proxyView = None
        return

    def init(self, input, output):
        """
        :type input: Event.Event
        :type output: Event.Event
        """
        input += self._processInputData
        output += self._outputDebugPrinter
        self._protocol = ScaleformProtocol(output)
        self._proxyView = ProxyView(self._model, self._protocol)

    def updateState(self, state):
        LOG_DEBUG('ScaleformDriver state update: %r' % state)
        self._protocol.updateState(state)

    def toggleHUDVisibility(self):
        self._protocol.toggleHUDVisibility()

    def updateBattleGameMode(self, mode):
        LOG_DEBUG('ScaleformDriver updateBattleGameMode: %r' % mode)
        self._protocol.updateBattleGameMode(mode)

    def openInter(self, id):
        self._protocol.openInter(id)

    def closeInter(self, id):
        self._protocol.closeInter(id)

    def closeInterForce(self):
        self._protocol.closeInterForce()

    def _processInputData(self, data):
        if data.startswith('message'):
            self._messageRouter.processData(data[8:])
        elif data.startswith('subscribe'):
            self._proxyView.subscribe(data[len('subscribe') + 1:])
        elif data.startswith('unsubscribe'):
            self._proxyView.unsubscribe(data[len('unsubscribe') + 1:])

    @staticmethod
    def _outputDebugPrinter(data):
        pass