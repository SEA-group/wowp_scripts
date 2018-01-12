# Embedded file name: scripts/client/EffectManager/Effects/EffectLoft.py
import BigWorld
from _effectBase import EffectBase
from consts import IS_EDITOR

class EffectLoft(EffectBase):

    def __init__(self, properties, attachProperties, effectManager):
        EffectBase.__init__(self, properties, attachProperties, effectManager)
        self.__loft = None
        if IS_EDITOR:
            return
        else:
            loftTexture = self.properties['loftTexture']
            loftHeight = float(self.properties['loftHeight'])
            loftAge = float(self.properties['loftAge'])
            loftGrownStage = int(self.properties['loftGrownStage'])
            self.__loft = BigWorld.Loft(loftTexture)
            self.__loft.maxAge = loftAge
            self.__loft.height = loftHeight
            self.__loft.colour = (255, 255, 255, 25)
            self.__loft.grownStage = loftGrownStage
            self.attach()
            return

    def attach(self):
        EffectBase.attach(self)
        if self.__loft is not None and self.effectAttachNode is not None:
            self.effectAttachNode.attach(self.__loft)
            self.__loft.enabled = self.visible
        else:
            self.destroy()
        return

    def detach(self):
        if self.__loft is not None and self.effectAttachNode is not None:
            self.effectAttachNode.detach(self.__loft)
        EffectBase.detach(self)
        return

    def setVisible(self, value):
        if self.visible == value:
            return
        else:
            EffectBase.setVisible(self, value)
            if self.__loft is not None:
                self.__loft.enabled = self.visible
            return

    def destroy(self):
        EffectBase.destroy(self)
        if self.__loft is not None:
            self.__loft.enabled = False
            self.__loft = None
        return