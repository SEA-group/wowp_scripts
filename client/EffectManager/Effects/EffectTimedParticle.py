# Embedded file name: scripts/client/EffectManager/Effects/EffectTimedParticle.py
import BigWorld
import Pixie
from _effectBase import EffectBase

class EffectTimedParticle(EffectBase):

    def __init__(self, properties, attachProperties, effectManager):
        EffectBase.__init__(self, properties, attachProperties, effectManager)
        self.callbackId = None
        self.__pixie = None
        self.__triggered = properties.get('alias', None) is not None
        self.force = 0
        if 'force' in self.properties:
            self.force = int(self.properties['force'])
        particleFile = self.properties['particleFile']
        if particleFile is not None and particleFile != '':
            Pixie.createBG(particleFile, self.__onParticleLoaded)
        return

    def attach(self):
        if self.delayed or self.attached:
            return
        else:
            EffectBase.attach(self)
            if self.__pixie is not None and self.effectAttachNode is not None:
                self.effectAttachNode.attach(self.__pixie)
                if self.force == 0:
                    self.__pixie.force()
                else:
                    self.__pixie.force(self.force)
                effectDuration = self.__pixie.duration()
                self.callbackId = BigWorld.callback(effectDuration * 1.1, self.__onParticleTimeEnd)
            else:
                self.destroy()
            return

    def detach(self):
        if not self.attached:
            return
        else:
            if self.__pixie is not None and self.effectAttachNode is not None and self.attached:
                self.effectAttachNode.detach(self.__pixie)
            if self.callbackId is not None:
                BigWorld.cancelCallback(self.callbackId)
                self.callbackId = None
            EffectBase.detach(self)
            return

    def setVisible(self, value):
        if self.__triggered:
            if self.visible == value:
                return
            if value:
                self.attach()
        EffectBase.setVisible(self, value)

    def clearPixie(self):
        if self.__pixie is not None:
            self.__pixie.clear()
        return

    def __onParticleLoaded(self, pixie):
        self.__pixie = pixie
        self.particleLoaded = True
        if not self.__triggered:
            self.attach()

    def __onParticleTimeEnd(self):
        self.callbackId = None
        self.detach()
        return

    def destroy(self):
        self.detach()
        EffectBase.destroy(self)
        self.__pixie = None
        self.callbackId = None
        return

    def collidesWithPoint(self, v3point):
        if not self.__pixie:
            return False
        self.__pixie.point_collide(v3point.x, v3point.y, v3point.z)