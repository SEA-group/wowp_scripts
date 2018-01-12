# Embedded file name: scripts/client/gui/HUD2/HudUI.py
import BigWorld
import GUI
import GameEnvironment
from Event import EventManager, Event
from clientConsts import SPECTATOR_TYPE
from gui import Cursor
from gui.HUD2.HUDController import HUDController
from gui.HudElements.MultiStateBombTarget import BombTargetHolder
from gui.Scaleform.windows import GUIWindow

class HudUI(GUIWindow):

    def __init__(self):
        super(HudUI, self).__init__('hud.swf')
        self._controller = HUDController()
        self.isModalMovie = False
        self._tick_callback = None
        self.__crosshairProvider = None
        self.__centerPoint = None
        self.__bombTarget = None
        self._em = EventManager()
        self._eReceive = Event(self._em)
        self._eSend = Event(self._em)
        self._eSend += self._send
        self.__isDisposed = False
        self.__crosshairVisible = False
        return

    def initialized(self, initData = None):
        self.movie.backgroundAlpha = 0.0
        self.addExternalCallbacks({'receive': self._eReceive,
         'hud2.subscribeCrosshair': lambda : self.__setCrosshairVisible(True),
         'hud2.unsubscribeCrosshair': lambda : self.__setCrosshairVisible(False),
         'debugMenuEvent': self.onDevMenuEvent,
         'settings.GetSettings': self.onEnterOptions,
         'settings.Close': self.onCloseOptions})
        self._controller.init(self._eReceive, self._eSend)
        self.hideCursor()
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.updateLocalizationTable()
        g_windowsManager.onMovieLoaded(self.className, self)
        GameEnvironment.g_instance.service('Chat').setUI(self)
        self._proxyPlayer = GameEnvironment.g_instance.playerAvatarProxy

    def _send(self, data):
        self.call_1('send', data)

    def _initMovingTarget(self):
        from gui.HudElements.CrosshairVariants import MovingTarget
        self.__crosshairProvider = MovingTarget()
        self.__crosshairProvider.init(self.movie)
        camera = GameEnvironment.getCamera()
        camera.leSetMovingTargetMatrix += self.__setMovingTargetMatrix
        BigWorld.player().eLeaveWorldEvent += self._disposeMovingTarget
        self._proxyPlayer.leTacticalSpectator += self.__setMovingTargetMatrixTS

    def _disposeMovingTarget(self):
        self.__crosshairProvider.removeProviders()
        self.__crosshairProvider = None
        camera = GameEnvironment.getCamera()
        camera.leSetMovingTargetMatrix -= self.__setMovingTargetMatrix
        BigWorld.player().eLeaveWorldEvent -= self._disposeMovingTarget
        self._proxyPlayer.leTacticalSpectator -= self.__setMovingTargetMatrixTS
        return

    def _initCenterPoint(self):
        from gui.HudElements.CenterPointVariants import CenterPoint
        self.__centerPoint = CenterPoint()
        self.__centerPoint.init(None, self.movie)
        camera = GameEnvironment.getCamera()
        camera.leSetCenterPointMatrix += self.__setCenterPointMatrix
        self._proxyPlayer.leTacticalSpectator += self.__setCenterPointMatrixTS
        BigWorld.player().eLeaveWorldEvent += self._disposeCenterPoint
        return

    def _disposeCenterPoint(self):
        camera = GameEnvironment.getCamera()
        camera.leSetCenterPointMatrix -= self.__setCenterPointMatrix
        self._proxyPlayer.leTacticalSpectator -= self.__setCenterPointMatrixTS
        BigWorld.player().eLeaveWorldEvent -= self._disposeCenterPoint
        self.__centerPoint.removeMatrixProvider()
        self.__centerPoint = None
        return

    def _initBombTarget(self):
        self.__bombTarget = BombTargetHolder(self._proxyPlayer)
        self.__bombTarget.initBombTarget()
        self._proxyPlayer.eSetBombTargetVisible += self.__bombTarget.setBombTargetVisible
        BigWorld.player().eLeaveWorldEvent += self._disposeBombTarget

    def _disposeBombTarget(self):
        self._proxyPlayer.eSetBombTargetVisible -= self.__bombTarget.setBombTargetVisible
        BigWorld.player().eLeaveWorldEvent -= self._disposeBombTarget
        self.__bombTarget.dispose()
        self.__bombTarget = None
        return

    def __setCenterPointMatrix(self, matrix):
        self.__centerPoint.setMatrixProvider(matrix)

    def __setCenterPointMatrixTS(self, spectatorType):
        if spectatorType is SPECTATOR_TYPE.TACTICAL:
            self.__centerPoint.setMatrixProvider(self._proxyPlayer.crossHairMatrix())

    def __setMovingTargetMatrix(self, matrix):
        self.__crosshairProvider.setTargetMatrix(matrix)

    def __setMovingTargetMatrixTS(self, *args, **kwargs):
        self.__setMovingTargetMatrix(self._proxyPlayer.crossHairMatrix())

    def onDevMenuEvent(self, VO):
        from debug.common import CustomMenu
        CustomMenu.debugMenuEvent(VO)

    def hideCursor(self):
        Cursor.forceShowCursor(False)
        entity = BigWorld.player()
        entity.setFlyMouseInputAllowed(True)

    def dispossessUI(self):
        if not self.__isDisposed:
            import BigWorld
            if self._tick_callback is not None:
                BigWorld.cancelCallback(self._tick_callback)
            self.removeAllCallbacks()
            self.__centerPoint = None
            self.__crosshairProvider = None
            self._controller.dispose()
            self._controller = None
            self._proxyPlayer = None
            self._em.clear()
            self._em = None
            self._eSend -= self.call_1
            self._eSend = None
            self._eReceive = None
        self.__isDisposed = True
        return

    def onEnterOptions(self):
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.showOptions()

    def onCloseOptions(self):
        if self._modalScreen:
            self._modalScreen.closeFlash()
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.hideOptions()

    def __getattr__(self, item):

        def wrapper(*args, **kwargs):
            pass

        return wrapper

    def _update(self):
        dispersionAngle = self._proxyPlayer.getWeaponController().getMaxVibroDispersionAngle()
        self.__crosshairProvider.setSize(GameEnvironment.getCamera().getFOV(), dispersionAngle)
        self.__bombTarget.updateBombTarget()
        self._tick_callback = BigWorld.callback(0.1, self._update)

    def __setCrosshairVisible(self, state):
        """
        @type state: bool
        """
        if state != self.__crosshairVisible:
            if state:
                self._subscribe()
                self._update()
            elif self._tick_callback is not None:
                BigWorld.cancelCallback(self._tick_callback)
                self._unsubscribe()
            self.__crosshairVisible = state
        return

    def _subscribe(self):
        self._initBombTarget()
        self._initMovingTarget()
        self._initCenterPoint()

    def _unsubscribe(self):
        self._disposeBombTarget()
        self._disposeMovingTarget()
        self._disposeCenterPoint()