# Embedded file name: scripts/client/LockingComponent.py
from AvatarControllerBase import AvatarControllerBase
import BigWorld
import InputMapping
import GameEnvironment
import weakref
from consts import DAMAGE_REASON, BATTLE_MODE
from EntityHelpers import isPlayerAvatar
from debug_utils import LOG_ERROR

def cppInCall(func):
    errorMsg = 'LockingComponent : call method {name}, cppObj = None'

    def wrapper(*args, **kwargs):
        self = args[0]
        if self._cppObj is not None:
            return func(*args, **kwargs)
        else:
            LOG_ERROR(errorMsg.format(name=func.__name__))
            return

    return wrapper


def cppOutCall(func):

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class LockingComponent(AvatarControllerBase):

    def __init__(self, owner, lockingAdapter):
        AvatarControllerBase.__init__(self, owner)
        self.__cppObj = None
        self._lockingAdapter = lockingAdapter
        self._owner.eTacticalRespawnEnd += self._tacticalRespawn
        GameEnvironment.g_instance.eAvatarHealthChange += self._hitEntity
        GameEnvironment.getInput().eAddProcessorListeners += self._addInputListeners
        GameEnvironment.getInput().eBattleModeChange += self.__onBattleModeChange
        return

    @property
    def _cppObj(self):
        return self.__cppObj()

    @cppOutCall
    def _init(self, cppObj):
        cppObj.setPlaneLevel(self._owner.settings.airplane.level)
        self.__cppObj = weakref.ref(cppObj)

    @cppOutCall
    def _destroy(self):
        self._owner.eTacticalRespawnEnd -= self._tacticalRespawn
        GameEnvironment.g_instance.eAvatarHealthChange -= self._hitEntity
        GameEnvironment.getInput().eAddProcessorListeners -= self._addInputListeners
        GameEnvironment.getInput().eBattleModeChange -= self.__onBattleModeChange
        self.__cppObj = None
        self._lockingAdapter.destroy()
        return

    @cppInCall
    def _tacticalRespawn(self, *args, **kwargs):
        self._cppObj.setPlaneLevel(self._owner.settings.airplane.level)

    @cppInCall
    def _hitEntity(self, entity, oldValue):
        if entity.lastDamageReason is DAMAGE_REASON.BULLET:
            if self._owner.id == entity.lastDamagerID:
                self._cppObj.hitEnemy(entity.id, (oldValue - entity.health) / entity.maxHealth)
            elif isPlayerAvatar(entity):
                self._cppObj.enemyHit(entity.lastDamagerID, (oldValue - entity.health) / entity.maxHealth)

    @cppInCall
    def _nextFrontTarget(self):
        self._cppObj.nextFrontTarget()

    @cppInCall
    def _nextCloselyTarget(self):
        self._cppObj.nextCloselyTarget()

    @cppInCall
    def _nextDangerousTarget(self):
        self._cppObj.nextDangerousTarget()

    @cppOutCall
    def _setTargetID(self, targetID):
        self._lockingAdapter.onSetTarget(targetID)

    @cppInCall
    def __onBattleModeChange(self, battleMode):
        if battleMode == BATTLE_MODE.ASSAULT_MODE:
            self._cppObj.setAirTargetsLockable(False)
            self._cppObj.setGroundTargetsLockable(True)
        elif battleMode == BATTLE_MODE.GUNNER_MODE:
            self._cppObj.setAirTargetsLockable(True)
            self._cppObj.setGroundTargetsLockable(False)
        else:
            self._cppObj.setAirTargetsLockable(True)
            self._cppObj.setGroundTargetsLockable(True)

    def _addInputListeners(self, processor):
        processor.addListeners(InputMapping.CMD_NEXT_TARGET, self._nextFrontTarget)
        processor.addListeners(InputMapping.CMD_NEXT_TARGET_TEAM_OBJECT, self._nextCloselyTarget)
        processor.addListeners(InputMapping.CMD_LOCK_TARGET, self._nextDangerousTarget)