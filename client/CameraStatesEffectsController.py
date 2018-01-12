# Embedded file name: scripts/client/CameraStatesEffectsController.py


class CameraStatesEffectsController(object):

    def __init__(self, effectsMap, effectMgr):
        """
        @param effectsMap: effectName -> integer key with combined key (see test_HUDStatesEffectsController)
        @type effectsMap: dict[str, tuple[int]]
        @type effectMgr: CameraEffect.CameraEffect
        """
        self._effectsMap = effectsMap
        self._effectsEnabled = set()
        self._effectMgr = effectMgr

    def destroy(self):
        for iD in self._effectsEnabled:
            self._setEffectEnabled(iD, False)

        self._effectsMap = None
        self._effectsEnabled = None
        self._effectMgr = None
        return

    def onCameraStateChanged(self, newStateId):
        effectsOn = set()
        effectsOff = set()
        for iD, states in self._effectsMap.iteritems():
            if newStateId in states:
                effectsOn.add(iD)
            else:
                effectsOff.add(iD)

        effectsTriggerOn = effectsOn - self._effectsEnabled
        effectsTriggerOff = effectsOff & self._effectsEnabled
        for iD in effectsTriggerOn:
            self._setEffectEnabled(iD, True)

        for iD in effectsTriggerOff:
            self._setEffectEnabled(iD, False)

        self._effectsEnabled = effectsOn

    def _setEffectEnabled(self, iD, isEnabled):
        self._effectMgr.onCameraEffect(iD, enable=isEnabled, stopImmediately=True)