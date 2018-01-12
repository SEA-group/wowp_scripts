# Embedded file name: scripts/client/EffectManager/Effects/EffectTrailParticle.py
from EffectLoopParticle import EffectLoopParticle

class EffectTrailParticle(EffectLoopParticle):

    def __init__(self, properties, attachProperties, effectManager):
        EffectLoopParticle.__init__(self, properties, attachProperties, effectManager)