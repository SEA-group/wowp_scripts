# Embedded file name: scripts/client/audio/SoundObjects/WwiseGameObject.py
from WWISE_ import setRTPC, SoundObject
from Math import Vector3
import audio.AKConsts as AKConsts
from WeakMethod import WeakMethod

class WwiseGameObject:

    def __init__(self, name, cid = 0, node = 0, position = None, entityID = 0):
        self.__so = SoundObject(name, cid, node)
        if position is not None:
            self.__so.position = position
        self.__so.orientation = Vector3(0.0, 1.0, 0.0)
        if entityID:
            self.__so.setEntityID(entityID)
        return

    def destroy(self):
        if self.destroyed:
            return
        else:
            self.__so.destroy()
            self.__so = None
            return

    def stopAll(self, t = 0, destroyAfter = False, i = AKConsts.AkCurveInterpolation_Linear):
        if self.destroyed:
            return
        self.__so.stop(t, i)
        if destroyAfter:
            self.destroy()

    def setSwitch(self, group, state):
        if self.destroyed:
            return
        self.__so.setSwitch(group, state)

    def setRTPC(self, name, value, valueChangeDuration = 0):
        if self.destroyed:
            return
        self.__so.setRTPC(name, value, valueChangeDuration)

    def setRtpcWithGlobal(self, name, value, valueChangeDuration = 0):
        setRTPC(name, value, valueChangeDuration)
        self.setRTPC(name, value, valueChangeDuration)

    def postEvent(self, name, eventEndCB = None, wait_marker = False):
        if self.destroyed:
            return
        elif not name or name is '':
            return
        else:
            if eventEndCB is not None:
                self.__so.postEvent(name, wait_marker, WeakMethod(eventEndCB))
            else:
                self.__so.postEvent(name, wait_marker, None)
            return

    def postStopEvent(self, playEvent):
        self.postEvent(self.convPlay2StopEvent(playEvent))

    def convPlay2StopEvent(self, playEvent):
        raise False or AssertionError('override play2stopEvent')

    def trigger(self, name):
        if self.destroyed:
            return
        self.__so.postMusicTrigger(name)

    def dialogue(self, name, soundOn, soundOff, noise, delay, state, state2, prio):
        if self.destroyed:
            return
        self.__so.dialogue(name, soundOn, soundOff, noise, delay, state, state2, prio)

    def stopDynSeq(self, transition = 0, interpolation = AKConsts.AkCurveInterpolation_Linear):
        if self.destroyed:
            return
        self.__so.stopDynSeq(transition, interpolation)
        self.__dynSeqIndex = {}

    def breakDynSeq(self):
        if self.destroyed:
            return
        self.__so.breakDynSeq()

    def clearDynSeq(self):
        if self.destroyed:
            return
        self.__so.stopDynSeq(0, AKConsts.AkCurveInterpolation_Linear)

    def skipDynSeqItems(self, items):
        if self.destroyed:
            return
        self.__so.removeDynSeqItems(items)

    def setPosition(self, v):
        if self.destroyed:
            return
        self.__so.position = v

    def setOrientation(self, v):
        if self.destroyed:
            return
        self.__so.orientation = v

    def onStateChanged(self, entity, old, new):
        self._onStateChanged(entity, old, new)

    def _onStateChanged(self, entity, old, new):
        pass

    def setEntityID(self, entityID):
        if self.destroyed:
            return
        self.__so.setEntityID(entityID)

    def setReverseOrientation(self, isReverse):
        if self.destroyed:
            return
        self.__so.setReverseOrientation(isReverse)

    def clear(self):
        pass

    @property
    def id(self):
        if self.destroyed:
            return -1
        return self.__so.id

    @property
    def playing(self):
        if self.destroyed:
            return False
        return self.__so.playing

    @property
    def pos(self):
        if self.destroyed:
            return Vector3()
        return self.__so.position

    @property
    def orient(self):
        if self.destroyed:
            return Vector3()
        return self.__so.orientation

    @property
    def destroyed(self):
        if not hasattr(self, '_{0}__so'.format(WwiseGameObject.__name__)) or not self.__so:
            return True
        return self.__so.destroyed

    @property
    def entityID(self):
        if self.destroyed:
            return 0
        return self.__so.entityID

    @property
    def entityID(self):
        if self.destroyed:
            return False
        return self.__so.isReverseOrientation


def GS():
    from audio import GameSound
    return GameSound()


class WwiseGameObjectFactory(object):

    @staticmethod
    def instance():
        pass

    def createPlayer(self, so):
        pass

    def createAvatar(self, avatar, so):
        pass

    def createTurret(self, object, so, val):
        pass

    def createSpectator(self, avatar, so):
        pass

    @staticmethod
    def getSoundObjectSettings(data):
        pass