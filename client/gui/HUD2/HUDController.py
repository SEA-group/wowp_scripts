# Embedded file name: scripts/client/gui/HUD2/HUDController.py
import BigWorld
from debug_utils import LOG_DEBUG
from features.GameModel import GameModel
from gui.HUD2.StateManager import StateManager
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Type
from gui.HUD2.core.Driver import ScaleformDriver
from gui.HUD2.core.FeatureBroker import FeatureBroker
from gui.HUD2.core.MessageRouter import MessageRouter
from gui.HUD2.hudFeatures import buildHudFeatures
from gui.Cursor import centerCursor
import weakref

class HUDController:

    def __init__(self):
        self._gameModel = None
        self._dataSources = []
        self._controllersDict = {}
        self._driver = None
        self._gameModel = GameModel()
        self._featureBroker = FeatureBroker()
        self._stateManager = StateManager()
        weakManager = weakref.ref(self._stateManager)
        buildHudFeatures(self._gameModel, self._featureBroker, weakManager)
        self._messageRouter = MessageRouter()
        return

    def dispose(self):
        self._featureBroker.clear()
        self._controllersDict.clear()
        for source in self._dataSources:
            source.dispose()

        self._dataSources = []
        if self._stateManager is not None:
            self._stateManager.dispose()
            self._stateManager = None
        self._driver = None
        self._messageRouter = None
        self._featureBroker = None
        self._gameModel.destroy()
        self._gameModel = None
        return

    def init(self, input, output):
        self._createModelServices(GameModel)
        self._driver = ScaleformDriver(self._messageRouter, self._gameModel)
        self._driver.init(input, output)
        self._initStateManager()
        self._driver.updateState(self._stateManager.state)

    def _initStateManager(self):
        self._stateManager.eStateChanged += self._onStateChange
        self._stateManager.eToggleHUDVisibility += self._onToggleHUDVisibility
        self._stateManager.eOpenInter += self._onOpenInter
        self._stateManager.eCloseInter += self._onCloseInter
        self._stateManager.eCloseInterForce += self._onCloseInterForce
        self._stateManager.initSignals(self._featureBroker)

    def _onStateChange(self, newValue):
        self._driver.updateState(newValue)

    def _onToggleHUDVisibility(self):
        self._driver.toggleHUDVisibility()

    def _onOpenInter(self, id):
        centerCursor()
        self._driver.openInter(id)

    def _onCloseInter(self, id):
        self._driver.closeInter(id)

    def _onCloseInterForce(self):
        self._driver.closeInterForce()

    def _createModelServices(self, modelCls):
        self._controllersDict = {}
        self._dataSources = []
        self._createModelService(modelCls)
        self._messageRouter.setupHandlers(self._controllersDict.itervalues())

    def _createModelService(self, cls):
        if issubclass(cls, AutoFilledDataModel):
            if cls.CONTROLLER is not None:
                self._createController(cls.CONTROLLER)
            if cls.DATA_SOURCE is not None:
                self._createSource(cls.DATA_SOURCE)
        for _, subCls in cls.SCHEME.fields:
            if not isinstance(subCls, Type):
                self._createModelService(subCls)

        return

    def _createController(self, controllerClass):
        self._controllersDict[controllerClass] = controllerClass(self._featureBroker)

    def _createSource(self, sourceClass):
        self._dataSources.append(sourceClass(self._featureBroker))