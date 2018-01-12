# Embedded file name: scripts/client/audio/SoundObjects/HitSound.py
import BigWorld
import math
from consts import DAMAGE_REASON, BATTLE_MODE
import GameEnvironment
import Settings
from WwiseGameObject import WwiseGameObject, GS
from audio.AKTunes import RTPC_Zoomstate_MAX, FREECAM_DIST_STEP, RTPC_Aircraft_Camera_Zoomstate_VDT
from audio.AKConsts import SOUND_OBJECT_TYPES
import audio.debug

class _HitSound(WwiseGameObject):
    _RTPC_HIT_DIRECTION = 'RTPC_Hit_Direction'

    def __init__(self, entityID, position, ev, dmgType = None, enemyID = None):
        dmgRamming = [DAMAGE_REASON.RAMMING]
        self.__isPlayer = ev in ('Play_hit_LOGIC_Avatar', 'Play_hit_EFFECT_damage_Avatar')
        if dmgType == DAMAGE_REASON.TREES:
            ev = HitSFXFactory.OTHER_DAMAGE + 'Threes'
        elif dmgType in dmgRamming:
            ev = HitSFXFactory.OTHER_DAMAGE + 'Ram'
        ctx = node = 0
        if not position:
            entity = BigWorld.entities.get(entityID, None)
            if entity:
                soundController = entity.controllers.get('soundController', None)
                if soundController:
                    so = soundController.soundObjects.get(SOUND_OBJECT_TYPES.ENGINE, None)
                    if so:
                        ctx = so.context.cidProxy.handle
                        node = so.node.id
        WwiseGameObject.__init__(self, 'HitSound-{0}'.format(ev), ctx, node, position)
        cam = GameEnvironment.getCamera()
        if self.__isPlayer and cam:
            cam.eZoomStateChanged += self.__onZoomStateChanged
            cam.eDistanceChanged += self.__onDistanceChanged
            self.__onZoomStateChanged(RTPC_Zoomstate_MAX if cam.isSniperMode else Settings.g_instance.camZoomIndex)
        if hasattr(BigWorld.player(), 'eLeaveWorldEvent'):
            BigWorld.player().eLeaveWorldEvent += self.__onLeaveWorld
        if self.__isPlayer and enemyID:
            self.__setHitDirectionRTPC(enemyID)
        em = GS().hitSFXManager
        if em is not None:
            em.register(self)
            self.postEvent(ev, self.__onLeaveWorld)
        return

    def __del__(self):
        self.__onLeaveWorld()

    def __setHitDirectionRTPC(self, enemyID):
        player = BigWorld.player()
        enemy = BigWorld.entities.get(enemyID, None)
        if not enemy:
            return
        else:
            hitDirectionVector = enemy.position - player.position
            rotation = player.getRotation()
            rotation.invert()
            hitDirectionAngle = math.degrees(rotation.rotateVec(hitDirectionVector).yaw)
            self.setRTPC(self._RTPC_HIT_DIRECTION, hitDirectionAngle)
            if audio.debug.IS_AUDIO_DEBUG:
                audio.debug.SHOW_DEBUG_OBJ('Last Hit Direction', hitDirectionAngle, group='HitSound')
            return

    def __onZoomStateChanged(self, val):
        self.__RTPC_Zoomstate(RTPC_Zoomstate_MAX - val)

    def __onDistanceChanged(self, d):
        self.__RTPC_Zoomstate(math.floor(d / FREECAM_DIST_STEP))

    def __RTPC_Zoomstate(self, val):
        if self.destroyed:
            return
        else:
            value = min(max(0, val), RTPC_Zoomstate_MAX)
            state = 'Zoomstate_0{0}'.format(value) if value > 0 else None
            self.setRTPC('RTPC_Aircraft_Camera_Zoomstate', value, RTPC_Aircraft_Camera_Zoomstate_VDT)
            if state:
                self.setSwitch('SWITCH_Camera_Zoomstate', state)
            return

    def __onLeaveWorld(self):
        player = BigWorld.player()
        if hasattr(player, 'eLeaveWorldEvent'):
            player.eLeaveWorldEvent -= self.__onLeaveWorld
        cam = GameEnvironment.getCamera()
        if self.__isPlayer and cam:
            cam.eZoomStateChanged -= self.__onZoomStateChanged
            cam.eDistanceChanged -= self.__onDistanceChanged
        self.stopAll(500, True)
        em = GS().hitSFXManager
        if em is not None:
            em.unregister(self)
        self.destroy()
        return


class HitSFXFactory(object):
    AVATAR_LOGIC_HIT = 'Play_hit_LOGIC_Avatar'
    NPC_LOGIC_HIT = 'Play_hit_LOGIC_NPC'
    AVATAR_EFFECT_HIT = 'Play_hit_EFFECT_damage_Avatar'
    NPC_EFFECT_HIT = 'Play_hit_EFFECT_damage_Spectator'
    OTHER_DAMAGE = 'Play_hit_IMPACT_'

    def __init__(self):
        self.__array = {}

    @staticmethod
    def canPlayEffect(name):
        entityID = None
        player = BigWorld.player()
        if name == HitSFXFactory.AVATAR_EFFECT_HIT:
            entityID = BigWorld.player().id
        elif hasattr(player, 'curVehicleID'):
            entityID = player.curVehicleID
        return entityID and not GS().isBurning(entityID, 5.0)

    @staticmethod
    def canPlay(entityID, health, oldHealth, damagerID, dmgType):
        player = BigWorld.player()
        isNPC = entityID != player.id
        dmgRamming = [DAMAGE_REASON.TREES,
         DAMAGE_REASON.RAMMING,
         DAMAGE_REASON.OBSTACLE,
         DAMAGE_REASON.TERRAIN,
         DAMAGE_REASON.WATER]
        dmgExplosion = [DAMAGE_REASON.FIRING, DAMAGE_REASON.ROCKET_EXPLOSION, DAMAGE_REASON.BOMB_EXPLOSION]
        currentBattleMode = GameEnvironment.getInput().inputAxis.currentBattleMode
        DELTA_HEALTH = 0
        if GS().isReplayMute:
            return False
        if isNPC and (damagerID != player.id or dmgType == DAMAGE_REASON.AA_EXPLOSION or not BigWorld.entities.get(entityID).damagedByGunID and currentBattleMode != BATTLE_MODE.GUNNER_MODE):
            return False
        if oldHealth - health < DELTA_HEALTH:
            return False
        if dmgType in dmgExplosion:
            return False
        if isNPC and dmgType in dmgRamming:
            return False
        return True

    @staticmethod
    def play(entityID, position, ev, dmgType = None, enemyID = None):
        _HitSound(entityID, position, ev, dmgType, enemyID)

    def register(self, obj):
        if obj and isinstance(obj, _HitSound):
            obj_id = id(obj)
            self.__array[obj_id] = obj

    def unregister(self, obj):
        if obj and isinstance(obj, _HitSound):
            obj_id = id(obj)
            self.__array.pop(obj_id, None)
        return

    def clear(self):
        self.__array = {}