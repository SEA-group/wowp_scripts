# Embedded file name: scripts/client/EffectManager/__init__.py
from EffectManager.EffectsManager import EffectManager
from EffectManager.SideLogicOfEffects import SideLogicOfEffects
from wofdecorators import noexcept

class _EffectManagerWrapper(object):

    def __init__(self):
        self._emInst = EffectManager()
        self._slInst = SideLogicOfEffects(self._emInst)

    def destroy(self):
        self._slInst.destroy()
        self._emInst.destroy()
        self._emInst = None
        self._slInst = None
        return

    def __getattr__(self, item):
        return getattr(self._emInst, item, getattr(self._slInst, item, None))


g_instance = None

def Init():
    global g_instance
    if g_instance is None:
        g_instance = _EffectManagerWrapper()
    return g_instance


@noexcept
def Destroy():
    global g_instance
    if g_instance is not None:
        g_instance.destroy()
        g_instance = None
    return