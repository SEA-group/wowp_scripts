# Embedded file name: scripts/client/EffectManager/Effects/EffectJet.py
import BigWorld
from _effectBase import EffectBase
from debug_utils import LOG_ERROR

class EffectJet(EffectBase):

    def __init__(self, properties, attachProperties, effectManager):
        EffectBase.__init__(self, properties, attachProperties, effectManager)
        if 'uniqueId' not in properties:
            LOG_ERROR('Unknown uniqueId property for Jet effect!', properties['id'])
            properties['uniqueId'] = ''
        self.__jet = BigWorld.Jet(properties['uniqueId'] + self.attachProperties['node'].name, self.properties['texture'])
        self.__jet.threshold = float(self.properties['threshold'])
        self.__jet.animDuration = float(self.properties['animDuration'])
        self.__jet.angleScale = float(self.properties['angleScale'])
        self.__jet.fadeInTime = float(self.properties['fadeInTime'])
        self.__jet.radiusMin = float(self.properties['radiusMin'])
        self.__jet.radiusMul = float(self.properties['radiusMul'])
        self.__jet.radiusPow = float(self.properties['radiusPow'])
        self.__jet.scaleMin = float(self.properties['scaleMin'])
        self.__jet.scaleMul = float(self.properties['scaleMul'])
        self.__jet.scalePow = float(self.properties['scalePow'])
        self.__jet.alphaMin = float(self.properties['alphaMin'])
        self.__jet.alphaMul = float(self.properties['alphaMul'])
        self.__jet.alphaPow = float(self.properties['alphaPow'])
        self.__jet.colorR = float(self.properties['colorR'])
        self.__jet.colorG = float(self.properties['colorG'])
        self.__jet.colorB = float(self.properties['colorB'])
        self.__jet.colorA = float(self.properties['colorA'])
        self.__jet.particleWidth = float(self.properties['particleWidth'])
        self.__jet.particleLen = float(self.properties['particleLen'])
        self.attach()

    def attach(self):
        EffectBase.attach(self)
        if self.__jet is not None and self.effectAttachNode is not None:
            self.effectAttachNode.attach(self.__jet)
            self.__jet.enabled = self.visible
        else:
            self.destroy()
        return

    def detach(self):
        if self.__jet is not None and self.effectAttachNode is not None:
            self.effectAttachNode.detach(self.__jet)
        EffectBase.detach(self)
        return

    def setVisible(self, value):
        if self.visible == value:
            return
        else:
            EffectBase.setVisible(self, value)
            if self.__jet is not None:
                self.__jet.enabled = self.visible
            return

    def destroy(self):
        EffectBase.destroy(self)
        if self.__jet is not None:
            self.__jet.enabled = False
            self.__jet = None
        return