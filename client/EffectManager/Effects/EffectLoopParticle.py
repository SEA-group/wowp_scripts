# Embedded file name: scripts/client/EffectManager/Effects/EffectLoopParticle.py
from _effectBase import EffectBase
import Pixie
from debug_utils import *

class EffectLoopParticle(EffectBase):

    def __init__(self, properties, attachProperties, effectManager):
        EffectBase.__init__(self, properties, attachProperties, effectManager)
        self.__pixie = None
        particleFile = self.properties['particleFile']
        if particleFile is not None and particleFile != '':
            Pixie.createBG(particleFile, self.__onParticleLoaded)
        return

    def __onParticleLoaded(self, pixie):
        self.__pixie = pixie
        self.particleLoaded = True
        self.attach()

    def attach(self):
        if self.delayed or self.attached:
            return
        else:
            EffectBase.attach(self)
            if self.__pixie is not None and self.effectAttachNode is not None:
                self.effectAttachNode.attach(self.__pixie)
                self.setVisible(self.visible)
            else:
                self.destroy()
            return

    def detach(self):
        if not self.attached:
            return
        else:
            if self.__pixie is not None and self.effectAttachNode is not None:
                self.effectAttachNode.detach(self.__pixie)
            EffectBase.detach(self)
            return

    def destroy(self):
        EffectBase.destroy(self)
        self.__pixie = None
        return

    def setVisible(self, value):
        EffectBase.setVisible(self, value)
        try:
            if self.__pixie is not None:
                for i in range(0, self.__pixie.nSystems()):
                    system = self.__pixie.system(i)
                    for action in system.actions:
                        if hasattr(action, 'timeTriggered'):
                            action.timeTriggered = value

        except:
            LOG_CURRENT_EXCEPTION()

        return

    def clearPixie(self):
        if self.__pixie is not None:
            self.__pixie.clear()
        return

    def setVisibleForce(self, value):
        self.clearPixie()
        self.setVisible(value)

    def stopEmission(self):
        if self.__pixie:
            for i in range(0, self.__pixie.nSystems()):
                system = self.__pixie.system(i)
                for action in system.actions:
                    if hasattr(action, 'rate'):
                        action.rate = 0