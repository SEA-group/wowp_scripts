# Embedded file name: scripts/client/gui/HudElements/MultiStateBombTarget.py
import GUI
import GameEnvironment
import InputMapping
from BWLogging import getLogger
from EntityHelpers import isTeamObject, canAimToEnemyEntity, EntityStates, isCorrectBombingAngle
from consts import *
from BombTarget import BombTarget
from Camera import CameraState
from gui.HUDconsts import *
from CommonSettings import bombMarkerCollisionRadius

class EStates:
    ON_TARGET = 1
    ROLLED = 2
    NO_AMMO = 4
    OUT = 8


class BaseLayer(object):
    resource = {}

    @staticmethod
    def activity_predicate(is_bomb_target):
        return True

    @staticmethod
    def matrix(target_matrix_provider):
        return target_matrix_provider

    @staticmethod
    def get_state(state):
        if state & EStates.OUT:
            return 4
        elif state & EStates.NO_AMMO:
            return 3
        elif state & EStates.ROLLED:
            return 2
        elif state & EStates.ON_TARGET:
            return 1
        else:
            return 0


class ScatterLayer(BaseLayer):
    resource = dict(enumerate(BOMBER_BOMB_TARGET_SCATTER_VISUAL))


class SplashLayer(BaseLayer):
    resource = dict(enumerate(BOMBER_BOMB_TARGET_SPLASH_VISUAL))

    @staticmethod
    def activity_predicate(is_bomb_target):
        return is_bomb_target

    @staticmethod
    def matrix(target_matrix_provider):
        expD = 2 * BigWorld.player().controllers['shellController'].getMaxBombExplosionRadius() / WORLD_SCALING
        scaleMtx = Math.Matrix()
        scaleMtx.setScale((expD, 1, expD))
        resMc = Math.MatrixCombiner()
        resMc.s = scaleMtx
        resMc.r = target_matrix_provider
        resMc.t = target_matrix_provider
        return resMc


class CenterLayer(BaseLayer):
    resource = dict(enumerate(BOMBER_BOMB_TARGET_CENTER_VISUAL))

    @staticmethod
    def activity_predicate(is_bomb_target):
        return is_bomb_target


class eHudElem:
    scatter = 0
    splash = 1
    center = 2
    all_elements = {scatter: ScatterLayer,
     splash: SplashLayer,
     center: CenterLayer}


class CustomObject:
    pass


class MultiStateBombTargetHud(object):

    class ProxyEl(object):

        def __init__(self):
            self.visible = 0
            self.disabled = 0

        def disabledAllStates(self):
            pass

        def setViewState(self, state, activity):
            pass

        def init(self):
            pass

    def __init__(self, active_elements):
        self._state = 0
        self.__is_bomber_state = False
        self.elements = {}
        for ael in active_elements:
            self.elements[ael] = self.ProxyEl()

    def init(self):
        pass

    def delete(self):
        for key in self.elements.iterkeys():
            self.elements[key] = None

        return

    @property
    def state(self):
        return self._state

    def set_bomber_state(self, ibs):
        self.__is_bomber_state = ibs
        self.__try_set_view()

    def set_state(self, state, v):
        if v != bool(self._state & state):
            self._state ^= state
            self.__try_set_view()
            return True
        return False

    @property
    def visible(self):
        for el in self.elements.itervalues():
            if el.visible:
                return True

        return False

    @visible.setter
    def visible(self, v):
        for el in self.elements.itervalues():
            el.visible = v

        self.__try_set_view()

    def __set_view(self, el_key, state, activity):
        el = self.elements[el_key]
        el.disabledAllStates()
        el.setViewState(state, activity)

    def __try_set_view(self):
        for elID in self.elements.iterkeys():
            settings = eHudElem.all_elements.get(elID)
            if settings is not None:
                state = settings.get_state(self._state)
                self.__set_view(elID, state, settings.activity_predicate(self.__is_bomber_state))

        return


class MultiStateBombTarget(BombTarget):

    def __init__(self, activeElements):
        super(MultiStateBombTarget, self).__init__()
        self._hud = MultiStateBombTargetHud(activeElements)
        self._dispersionCfc = 1
        GameEnvironment.getCamera().eStateChanged += self._setBomberState

    def destroy(self):
        GameEnvironment.getCamera().eStateChanged -= self._setBomberState
        self.setVisible(False)
        if self._inited:
            for el in self._hud.elements.itervalues():
                GUI.delRoot(el)
                el.bombMP = None

        self._inited = False
        self._visible = False
        self._hud.delete()
        self.dispose()
        return

    def _createTargetHud(self):
        for el in self._hud.elements.iterkeys():
            hudElement = GUI.BombMultyViewHud()
            hudElement.materialIntensity = 25.0
            settings = eHudElem.all_elements.get(el)
            if settings is not None:
                for state, resource in settings.resource.iteritems():
                    hudElement.addViewState(state, resource)

                hudElement.bombMP = settings.matrix(self._matrixProvider)
            self._hud.elements[el] = hudElement

        return

    def _initHud(self):
        self._signEnabled = True
        self._inited = True
        self._hud.visible = True
        for el in self._hud.elements.itervalues():
            GUI.addRoot(el)

    def _setBomberState(self, newState):
        ibs = GameEnvironment.getCamera().getState() is CameraState.Bomber
        if self._matrixProvider is not None:
            maxBombExplosionD = self._player.getShellController().getMaxBombExplosionRadius() / WORLD_SCALING
            self._matrixProvider.minTargetSize = maxBombExplosionD if ibs else MIN_BOMB_TARGET_SIZE
        self._hud.set_bomber_state(ibs)
        return

    def _getMinMaxTargetSize(self):
        return (MIN_BOMB_TARGET_SIZE, MAX_BOMB_TARGET_SIZE)

    def __updateScaleFormHud(self):
        pos = None
        if not self._matrixProvider.isHide:
            pos = BigWorld.worldToScreen(self._matrixProvider.position)
        GameEnvironment.g_instance.eSetBombMarkerPos(pos)
        state = self._hud.state
        GameEnvironment.g_instance.eSetBombRolled(state & EStates.ROLLED > 0)
        return

    def _update(self):
        super(MultiStateBombTarget, self)._update()
        isOnTarget = False
        btPos = self._matrixProvider.position
        btScale = self._matrixProvider.hypotScale * bombMarkerCollisionRadius
        inZone = lambda ent: (ent.position - btPos).length < btScale
        for entity in BigWorld.entities.values():
            if isTeamObject(entity) and canAimToEnemyEntity(self._player, entity) and inZone(entity):
                isOnTarget = True
                break

        self.setOnTarget(isOnTarget)
        self.__updateScaleFormHud()

    def setIsAmmo(self, v):
        self._hud.set_state(EStates.NO_AMMO, not v)

    def setOnTarget(self, v):
        self._hud.set_state(EStates.ON_TARGET, v)

    def setBombTargetEnable(self, v):
        self._hud.set_state(EStates.ROLLED, not v)


class BombTargetProxy(object):

    @staticmethod
    def restart(self):
        pass

    @staticmethod
    def destroy():
        pass

    @staticmethod
    def isVisible():
        return False

    @staticmethod
    def disableUpdate(value):
        pass

    @staticmethod
    def setIsAmmo(value):
        pass

    @staticmethod
    def setVisible(value):
        pass

    @staticmethod
    def setBombTargetEnable(value):
        pass

    @staticmethod
    def setBombDispersionParams(value):
        pass


class BombTargetHolder(object):

    def __init__(self, player):
        self._player = player
        self._bombTarget = BombTargetProxy
        self._visibleBombing = True
        self._isTabActive = False
        self._isHudVisible = True
        self._player.eTacticalRespawnEnd += self._onTacticalRespawnEnd
        self._player.eTacticalSpectator += self._onTacticalRespawnEnd
        self._log = getLogger(self)
        self._input = GameEnvironment.getInput().commandProcessor
        self._input.addListeners(InputMapping.CMD_VISIBILITY_HUD, None, None, self._onHUDVisibilityCommand)
        self._input.addListeners(InputMapping.CMD_SHOW_TEAMS, None, None, self._setTabStateActive)
        return

    def dispose(self):
        if not self._input.destroyed:
            self._input.removeListeners(InputMapping.CMD_VISIBILITY_HUD, None, None, self._onHUDVisibilityCommand)
            self._input.removeListeners(InputMapping.CMD_SHOW_TEAMS, None, None, self._setTabStateActive)
        self._player.eTacticalRespawnEnd -= self._onTacticalRespawnEnd
        self._player.eTacticalSpectator -= self._onTacticalRespawnEnd
        self._player = None
        self._bombTarget.destroy()
        self._bombTarget = None
        return

    def initBombTarget(self):
        elements = []
        for groupID, weaponData in self._shellController.getShellGroupsInitialInfo().items():
            if weaponData['shellID'] is UPDATABLE_TYPE.BOMB and weaponData['description'] is not None:
                elements = [eHudElem.center, eHudElem.splash, eHudElem.scatter]

        self._bombTarget.destroy()
        if elements:
            self._bombTarget = MultiStateBombTarget(elements)
        else:
            self._bombTarget = BombTargetProxy
        return

    def _setTabStateActive(self, isTab):
        self._isTabActive = isTab
        self.setBombTargetVisible(self._visibleBombing)

    def setBombTargetVisible(self, visible):
        self._visibleBombing = visible
        visible = visible and self._isBombsAvailable() and self._inGame and not self._isTabActive and self._isHudVisible
        self._bombTarget.setVisible(visible)
        if visible:
            self._bombTarget.setBombDispersionParams(self._shellController.getBombDispersionAngle())

    def updateBombTarget(self):
        if self._bombTarget.isVisible():
            self._bombTarget.setIsAmmo(self._isAmmoBombs())
            rolling = isCorrectBombingAngle(self._player, self._player.getRotation())
            self._bombTarget.setBombTargetEnable(rolling)

    def _onHUDVisibilityCommand(self, state):
        self._log.trace('HUD visibility command %s', state)
        self._isHudVisible = not state
        self.setBombTargetVisible(self._isHudVisible)

    def disableBombTargetUpdate(self, value):
        self._bombTarget.disableUpdate(value)

    @property
    def _inGame(self):
        return EntityStates.inState(self._player, EntityStates.GAME)

    @property
    def _shellController(self):
        return self._player.getShellController()

    def _isAmmoBombs(self):
        return self._shellController.getShellCountForType(UPDATABLE_TYPE.BOMB) > 0

    def _isBombsAvailable(self):
        return self._shellController.isTypeOnBoard(UPDATABLE_TYPE.BOMB)

    def _onTacticalRespawnEnd(self, *args, **kwargs):
        """Handler for Avatar.eTacticalRespawnEnd event
        """
        self.initBombTarget()
        self.setBombTargetVisible(True)