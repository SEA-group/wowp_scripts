# Embedded file name: scripts/client/audio/DopplerEffect.py
import BigWorld
from AKConsts import SPEED_OF_SOUND, SOUND_CALLBACK_QUEUE_TYPES
from consts import WORLD_SCALING
from AKTunes import RTPC_DopplerEffect_Update_Interval, SOUND_CALLBACKS_PER_TICK
from EntityHelpers import EntityStates
from debug_utils import LOG_INFO
from audio.AKConsts import DEBUG_AUDIO_TAG
from SoundUpdateManager import SoundUpdateManager, SoundUpdateQueue
g_instance = None

class DopplerEffect(SoundUpdateQueue):
    RTPC = 'RTPC_NPC_Doppler_Delta'
    DOPPLER_RANGE = 500 * WORLD_SCALING

    def __init__(self):
        SoundUpdateQueue.__init__(self, SOUND_CALLBACK_QUEUE_TYPES.DOPPLER, SOUND_CALLBACKS_PER_TICK.DOPPLER)
        self.__soundSpeed = SPEED_OF_SOUND * WORLD_SCALING * WORLD_SCALING
        self.__entities = {}
        self.__listener = None
        self.__listenerID = 0
        self.__updateCB = None
        self.__entitiesQueue = []
        player = BigWorld.player()
        player.eLeaveWorldEvent += self.__onPlayerLeaveWorld
        player.onStateChanged += self.__onPlayerStateChanged
        return

    def __onPlayerLeaveWorld(self):
        self.deactivate()
        self.__entities.clear()

    def __onPlayerStateChanged(self, oldState, state):
        if state == EntityStates.OUTRO:
            self.deactivate()

    def activate(self):
        SoundUpdateManager.instance().registerQueue(SOUND_CALLBACK_QUEUE_TYPES.DOPPLER, self)
        LOG_INFO('%s %s' % (DEBUG_AUDIO_TAG, 'DopplerEffect; Activated'))

    def deactivate(self):
        SoundUpdateManager.instance().removeQueue(SOUND_CALLBACK_QUEUE_TYPES.DOPPLER)
        LOG_INFO('%s %s' % (DEBUG_AUDIO_TAG, 'DopplerEffect; Deactivated'))

    def __getDopplerEffect(self, source):
        distance = self.__listener.position - source.position
        if not distance:
            return 0
        sourceSpeed = source.getWorldVector()
        speed = sourceSpeed - self.__listener.getWorldVector()
        relativeSpeed = distance.dot(speed) / distance.length
        return relativeSpeed / self.__soundSpeed

    def __isInRange(self, source):
        return self.__listener.position.distTo(source.position) < DopplerEffect.DOPPLER_RANGE

    def add(self, entity, wwiseSoundObject):
        if entity not in self.__entities:
            self.__entities[entity] = set()
        self.__entities[entity].add(wwiseSoundObject)
        self.__entitiesQueue.append(entity)

    def discard(self, entityID, wwiseSoundObject):
        if entityID in self.__entities and self.__entities[entityID]:
            self.__entities[entityID].discard(wwiseSoundObject)
            if not len(self.__entities[entityID]):
                self.removeEntity(entityID)

    def removeEntity(self, entityID):
        del self.__entities[entityID]

    def updateQueue(self):
        for i in range(min(self._updatesPerTick, len(self.__entitiesQueue))):
            entityID = self.__entitiesQueue.pop()
            if entityID in self.__entities.keys():
                self.__singleEntityUpdate(entityID)

        if not len(self.__entitiesQueue):
            self.__entitiesQueue.extend(self.__entities.keys())

    def __singleEntityUpdate(self, entityID):
        self.__listener = BigWorld.entities.get(self.__listenerID, None)
        if not self.__listener or not self.__listener.inWorld:
            return
        else:
            entity = BigWorld.entities.get(entityID)
            if not entity or not entity.inWorld or entityID == self.__listener.id or not self.__isInRange(entity):
                return
            dopplerEffect = self.__getDopplerEffect(entity)
            for soundObject in self.__entities[entityID]:
                soundObject.setRTPC(DopplerEffect.RTPC, dopplerEffect)

            return

    def setListener(self, avatar):
        self.__listener = avatar
        self.__listenerID = 0 if avatar is None else avatar.id
        return

    @property
    def listener(self):
        return self.__listener

    @staticmethod
    def instance():
        global g_instance
        if not g_instance:
            g_instance = DopplerEffect()
        return g_instance