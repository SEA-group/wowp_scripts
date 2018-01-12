# Embedded file name: scripts/client/gui/HUD2/HUDStatesEffectsController.py


class HUDStatesEffectsController(object):

    def __init__(self, effectsMap, effectManager):
        """
        @param effectsMap: effectName -> integer key with combined key (see test_HUDStatesEffectsController)
        @type effectsMap: dict[str, int]
        @type effectManager: EffectManager.EffectManager
        """
        self._effectsMap = effectsMap
        self._effectsEnabled = set()
        self._effectMgr = effectManager

    def destroy(self):
        for iD in self._effectsEnabled:
            self._effectMgr.setScreenParticle(iD, active=False)

        self._effectMgr = None
        self._effectsMap = None
        self._effectsEnabled = None
        return

    def onHUDStateChanged(self, newState):
        effectsOn = set()
        effectsOff = set()
        for iD, states in self._effectsMap.iteritems():
            if states & newState == 0:
                effectsOff.add(iD)
            else:
                effectsOn.add(iD)

        effectsTriggerOn = effectsOn - self._effectsEnabled
        effectsTriggerOff = effectsOff & self._effectsEnabled
        for iD in effectsTriggerOn:
            self._effectMgr.setScreenParticle(iD, active=True)

        for iD in effectsTriggerOff:
            self._effectMgr.setScreenParticle(iD, active=False)

        self._effectsEnabled = effectsOn