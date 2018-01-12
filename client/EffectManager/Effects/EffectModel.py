# Embedded file name: scripts/client/EffectManager/Effects/EffectModel.py
from _effectBase import EffectBase

class EffectModel(EffectBase):

    def __init__(self, properties, attachProperties, effectManager):
        EffectBase.__init__(self, properties, attachProperties, effectManager)