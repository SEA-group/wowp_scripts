# Embedded file name: scripts/client/audio/InteractiveMix/MixFocus.py
import BigWorld
from audio.AKConsts import SOUND_OBJECT_TYPES, TURRET_SOUND

class MixFocus:

    def __init__(self):
        self.__turretsFocusedOnPlayer = set()

    def onTurretTargetChanged(self, entityID, turretID, targetID):
        if BigWorld.player().id == targetID:
            self.__turretsFocusedOnPlayer.add((entityID, turretID))
        elif (entityID, turretID) in self.__turretsFocusedOnPlayer:
            self.__switchTurret(BigWorld.entities.get(entityID), turretID, TURRET_SOUND.SWITCH.TARGET_UNFOCUSED)
            self.__turretsFocusedOnPlayer.discard((entityID, turretID))
        if self.__turretsFocusedOnPlayer:
            self.__updateTurretsFocus()

    def __updateTurretsFocus(self):
        angles = {}
        for entityID, turretID in self.__turretsFocusedOnPlayer:
            entity = BigWorld.entities.get(entityID, None)
            if not entity:
                self.__turretsFocusedOnPlayer.discard((entityID, turretID))
            else:
                player = BigWorld.player()
                angle = player.getWorldVector().angle(entity.position - player.position)
                angles[angle] = (entity, turretID)
                self.__switchTurret(entity, turretID, TURRET_SOUND.SWITCH.TARGET_FOCUSED)

        min_angle = min(angles.keys())
        minAngleEntity, turretID = angles[min_angle]
        self.__switchTurret(minAngleEntity, turretID, TURRET_SOUND.SWITCH.TARGET_MAIN)
        return

    def __switchTurret(self, entity, turretId, state):
        soundController = entity.controllers.get('soundController')
        turretSound = soundController.getWwiseGameObject(SOUND_OBJECT_TYPES.TURRET(turretId))
        if turretSound:
            turretSound.setSwitch(TURRET_SOUND.SWITCH.TARGET, state)

    def clear(self):
        self.__turretsFocusedOnPlayer = set()

    def __registerTurretsEvents(self):
        pass