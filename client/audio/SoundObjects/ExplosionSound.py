# Embedded file name: scripts/client/audio/SoundObjects/ExplosionSound.py
import BigWorld
from WwiseGameObject import WwiseGameObject, GS

class _ExplosionSound(WwiseGameObject):

    def __init__(self, ev, pos):
        WwiseGameObject.__init__(self, 'ExplosionSound-{0}'.format(ev), 0, 0, pos)
        if hasattr(BigWorld.player(), 'eLeaveWorldEvent'):
            BigWorld.player().eLeaveWorldEvent += self.__destroy
        em = GS().explosionSFXManager
        if em is not None:
            em.register(self)
            self.postEvent(ev, self.__destroy)
        return

    def __destroy(self):
        if hasattr(BigWorld.player(), 'eLeaveWorldEvent'):
            BigWorld.player().eLeaveWorldEvent -= self.__destroy
        em = GS().explosionSFXManager
        if em is not None:
            em.unregister(self)
        self.destroy()
        return

    def __del__(self):
        self.__destroy()


class ExplosionSFXFactory(object):
    AVATAR_EXPLOSION = 'Play_explosion_avatar'
    NPC_EXPLOSION = 'Play_explosion_npc'
    NPC_EXPOSION_FRAG = 'Play_explosion_npc_frag'

    def __init__(self):
        self.__array = {}

    @staticmethod
    def play(ev, pos):
        _ExplosionSound(ev, pos)

    def register(self, obj):
        if obj and isinstance(obj, _ExplosionSound):
            obj_id = id(obj)
            self.__array[obj_id] = obj

    def unregister(self, obj):
        if obj and isinstance(obj, _ExplosionSound):
            obj_id = id(obj)
            self.__array.pop(obj_id, None)
        return

    def clear(self):
        self.__array = {}