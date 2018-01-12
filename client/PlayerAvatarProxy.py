# Embedded file name: scripts/client/PlayerAvatarProxy.py
import BigWorld
import InputMapping
from clientConsts import SPECTATOR_TYPE
from Event import Event, LazyEvent, EventManager
import weakref

class TACTICAL_SPECTATOR_TYPE:
    AUTO = 0
    CONTROLLED = 1


def proxy_property(func):

    def wrapper(self):
        return getattr(self._fakePlayer, func.__name__)

    return property(wrapper)


def proxy_method(func):

    def wrapper(self, *args, **kwargs):
        return getattr(self._fakePlayer, func.__name__)(*args, **kwargs)

    return wrapper


class proxy_event(object):

    def __init__(self, eventType, *args, **kwargs):
        self._event = eventType(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self._event(*args, **kwargs)

    def __get__(self, instance, owner):
        return self

    def __set__(self, instance, value):
        pass

    def __delete__(self, instance):
        self._event.clear()

    def __iadd__(self, delegate):
        self._event += delegate
        return self

    def __isub__(self, delegate):
        self._event -= delegate
        return self


class PlayerAvatarProxy(object):

    def __init__(self, player):
        self.__realPlayerRef = weakref.ref(player)
        self.__fakePlayerRef = weakref.ref(player)
        self._spectatingID = -1
        self._relinkProxyEvents(None, self._fakePlayer)
        self._spectatorType = SPECTATOR_TYPE.NONE
        self._tacticalSpectatorType = TACTICAL_SPECTATOR_TYPE.AUTO
        self._em = EventManager()
        self.eTacticalSpectator = Event(self._em)
        self.leTacticalSpectator = LazyEvent(self._em)
        self.onStateChanged = Event(self._em)
        self.eUpdateHealth = Event(self._em)
        self.eUpdateSpectator = Event(self._em)
        self.eRespawn = Event(self._em)
        self._realPlayer.eRespawn += self._eRespawn
        self._realPlayer.eUpdateSpectator += self._eUpdateSpectator
        return

    @property
    def _realPlayer(self):
        return self.__realPlayerRef()

    @property
    def _fakePlayer(self):
        return self.__fakePlayerRef()

    def dispose(self):
        self._realPlayer.eRespawn -= self._eRespawn
        self._realPlayer.eUpdateSpectator -= self._eUpdateSpectator
        self._relinkProxyEvents(self._fakePlayer, None)
        self.__realPlayerRef = None
        self.__fakePlayerRef = None
        self._spectatingID = -1
        del self.eRepair
        del self.ePartStateChanged
        del self.eUpdateConsumables
        del self.eSetBombTargetVisible
        del self.eUnderRepairZoneInfluence
        del self.eUpdateHUDAmmo
        del self.eOnGunGroupFire
        del self.ePartFlagSwitchedNotification
        self._em.clear()
        return

    eRepair = proxy_event(Event)
    ePartStateChanged = proxy_event(Event)
    eUpdateConsumables = proxy_event(Event)
    eSetBombTargetVisible = proxy_event(LazyEvent)
    eUnderRepairZoneInfluence = proxy_event(Event)
    eUpdateHUDAmmo = proxy_event(Event)
    eOnGunGroupFire = proxy_event(Event)
    ePartFlagSwitchedNotification = proxy_event(Event)

    @staticmethod
    def _isEntityValid(e):
        return e is not None and e.inWorld

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__getattribute__(item)
        return getattr(self._realPlayer, item)

    def setProxyPlayer(self, entity):
        if self._fakePlayer.id != entity.id:
            self._relinkProxyEvents(self._fakePlayer, entity)
            self.__fakePlayerRef = weakref.ref(entity)
            return True
        return False

    def _onLeaveFakePlayerWorld(self):
        self._tryActivateTacticalSpectator(self._realPlayer)

    @property
    def spectatorTypeWithTacticalMode(self):
        if self._spectatorType == SPECTATOR_TYPE.NONE or self._spectatorType == SPECTATOR_TYPE.CINEMATIC:
            return self._spectatorType
        if self._tacticalSpectatorType == TACTICAL_SPECTATOR_TYPE.AUTO:
            return SPECTATOR_TYPE.AUTO_TACTICAL
        if self._tacticalSpectatorType == TACTICAL_SPECTATOR_TYPE.CONTROLLED:
            return SPECTATOR_TYPE.CONTROLLED_TACTICAL
        return SPECTATOR_TYPE.NONE

    def _tryActivateTacticalSpectator(self, entity):
        if self._isEntityValid(entity) and self.setProxyPlayer(entity):
            self.eTacticalSpectator(self.spectatorTypeWithTacticalMode)
            self.leTacticalSpectator(self.spectatorTypeWithTacticalMode)

    def activateTacticalSpectator(self, spectatorType):
        self._spectatorType = spectatorType
        if spectatorType & (SPECTATOR_TYPE.AUTO_TACTICAL | SPECTATOR_TYPE.CONTROLLED_TACTICAL) != 0:
            entity = BigWorld.entities.get(self._spectatingID)
            self._tryActivateTacticalSpectator(entity)
        else:
            self._tryActivateTacticalSpectator(self._realPlayer)

    def addInputListeners(self, processor):
        processor.addListeners(InputMapping.CMD_SWITCH_TACTICAL_MODE, None, None, lambda fired: self._switchTacticalMode())
        return

    def _switchTacticalMode(self):
        if self._tacticalSpectatorType == TACTICAL_SPECTATOR_TYPE.AUTO:
            self._tacticalSpectatorType = TACTICAL_SPECTATOR_TYPE.CONTROLLED
        else:
            self._tacticalSpectatorType = TACTICAL_SPECTATOR_TYPE.AUTO

    def _relinkProxyEvents(self, oldEntity, newEntity):
        if oldEntity is not None:
            oldEntity.eLeaveWorldEvent -= self._onLeaveFakePlayerWorld
            oldEntity.eOnEntityStateChanged -= self._onStateChanged
            oldEntity.eHealthChanged -= self._eUpdateHealth
            oldEntity.ePartStateChanged -= self.ePartStateChanged
            oldEntity.eUpdateConsumables -= self.eUpdateConsumables
            oldEntity.eUnderRepairZoneInfluence -= self.eUnderRepairZoneInfluence
            oldEntity.eRepair -= self.eRepair
            oldEntity.eSetBombTargetVisible -= self.eSetBombTargetVisible
            oldEntity.eUpdateHUDAmmo -= self.eUpdateHUDAmmo
            oldEntity.eOnGunGroupFire -= self.eOnGunGroupFire
            oldEntity.ePartFlagSwitchedNotification -= self.ePartFlagSwitchedNotification
        if newEntity is not None:
            newEntity.eLeaveWorldEvent += self._onLeaveFakePlayerWorld
            newEntity.eOnEntityStateChanged += self._onStateChanged
            newEntity.eHealthChanged += self._eUpdateHealth
            newEntity.ePartStateChanged += self.ePartStateChanged
            newEntity.eUpdateConsumables += self.eUpdateConsumables
            newEntity.eUnderRepairZoneInfluence += self.eUnderRepairZoneInfluence
            newEntity.eRepair += self.eRepair
            newEntity.eSetBombTargetVisible += self.eSetBombTargetVisible
            newEntity.eUpdateHUDAmmo += self.eUpdateHUDAmmo
            newEntity.eOnGunGroupFire += self.eOnGunGroupFire
            newEntity.ePartFlagSwitchedNotification += self.ePartFlagSwitchedNotification
        return

    def _eRespawn(self):
        self._tryActivateTacticalSpectator(self._realPlayer)
        self._spectatorType = SPECTATOR_TYPE.NONE
        self._spectatingID = -1
        self.eRespawn()

    def _eUpdateSpectator(self, curVehicleID):
        self.eUpdateSpectator(curVehicleID)
        if self._spectatorType is SPECTATOR_TYPE.TACTICAL:
            entity = BigWorld.entities.get(curVehicleID)
            self._tryActivateTacticalSpectator(entity)
        self._spectatingID = curVehicleID

    def _eUpdateHealth(self, id, health, lastDamagerID, oldValue, maxHealth):
        self.eUpdateHealth(health, lastDamagerID, oldValue)

    def _onStateChanged(self, id, oldState, state):
        self.onStateChanged(oldState, state)

    def isRealPlayer(self):
        return self._realPlayer.id == self._fakePlayer.id

    def crossHairMatrix(self):
        if self.isRealPlayer():
            return self._realPlayer.crossHairMatrix
        return self._fakePlayer.realMatrix

    @property
    def crewSkills(self):
        if self.isRealPlayer():
            return self._realPlayer.crewSkills
        return []

    @proxy_property
    def id(self):
        pass

    @proxy_property
    def health(self):
        pass

    @proxy_property
    def maxHealth(self):
        pass

    @proxy_property
    def baseVisionDistance(self):
        pass

    @proxy_property
    def globalID(self):
        pass

    @proxy_property
    def objTypeID(self):
        pass

    @proxy_property
    def settings(self):
        pass

    @proxy_property
    def partStates(self):
        pass

    @proxy_property
    def state(self):
        pass

    @proxy_property
    def planeType(self):
        pass

    @proxy_property
    def isUnderRepairZoneInfluence(self):
        pass

    @proxy_property
    def repair(self):
        pass

    @proxy_property
    def inWorld(self):
        pass

    @proxy_property
    def logicalParts(self):
        pass

    @proxy_property
    def consumables(self):
        pass

    @proxy_property
    def position(self):
        pass

    @proxy_property
    def shellsRechargeInfo(self):
        pass

    @proxy_property
    def realMatrix(self):
        pass

    @proxy_property
    def stallSpeed(self):
        pass

    @proxy_method
    def getShellController(self):
        pass

    @proxy_method
    def getWeaponController(self):
        pass

    @proxy_method
    def hasGunner(self):
        pass

    @proxy_method
    def getSpeed(self):
        pass

    @proxy_method
    def getAltitudeAboveWaterLevel(self):
        pass

    @proxy_method
    def getAltitudeAboveObstacle(self):
        pass

    @proxy_method
    def getAmmoBeltsInitialInfo(self):
        pass

    @proxy_method
    def getBeltsAmmoCountByGroup(self):
        pass

    @proxy_method
    def getShellsInitialInfo(self):
        pass

    @proxy_method
    def getRotation(self):
        pass