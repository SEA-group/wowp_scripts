# Embedded file name: scripts/client/audio/SoundObjects/CameraSound.py
from WwiseGameObject import WwiseGameObject
from audio.AKConsts import CAMERA_SOUND
import db.DBLogic
from consts import BATTLE_MODE, PLANE_TYPE
import GameEnvironment
import BigWorld
from EntityHelpers import EntityStates
import CameraEffect
import WWISE_

class CameraSoundObject(WwiseGameObject):

    def __init__(self):
        WwiseGameObject.__init__(self, 'Camera')
        self.__pillowMaterial = None
        self.__currentSoundMode = None
        self.__forsageValue = None
        return

    def onPlayerEnterWorld(self):
        self.__registerEvents()

    def __registerEvents(self):
        pass

    def __clearEvents(self):
        pass

    def destroy(self):
        self.__clearEvents()

    def onBattleModeChange(self, battleMode):
        if battleMode == BATTLE_MODE.ASSAULT_MODE:
            self.__switchCameraSoundMode(CAMERA_SOUND.MODE.BOMBING)
        elif battleMode == BATTLE_MODE.GUNNER_MODE:
            self.__switchCameraSoundMode(CAMERA_SOUND.MODE.TAILGUNNER)
        elif battleMode == BATTLE_MODE.SNIPER_MODE and BigWorld.player().planeType != PLANE_TYPE.BOMBER:
            self.__switchCameraSoundMode(CAMERA_SOUND.MODE.SNIPER_MODE)
        else:
            self.__switchCameraSoundMode(CAMERA_SOUND.MODE.MAIN)

    def __switchCameraSoundMode(self, soundMode):
        if self.__currentSoundMode != soundMode and EntityStates.inState(BigWorld.player(), EntityStates.GAME):
            self.__currentSoundMode = soundMode
            self.postEvent(soundMode)

    def updatePillow(self, materialName, isActive):
        if not self.__pillowMaterial:
            if isActive:
                self.setSwitch(CAMERA_SOUND.PILLOW.SWITCH_MATERIAL, materialName)
                self.postEvent(CAMERA_SOUND.PILLOW.PLAY_EVENT_ID)
                self.__pillowMaterial = materialName
        elif isActive:
            if self.__pillowMaterial != materialName:
                self.__pillowMaterial = materialName
                self.setSwitch(CAMERA_SOUND.PILLOW.SWITCH_MATERIAL, materialName)
        else:
            self.postEvent(CAMERA_SOUND.PILLOW.STOP_EVENT_ID)
            self.__pillowMaterial = None
        return

    def playCameraEffect(self, eventID):
        event = db.DBLogic.g_instance.getEffectSound(eventID)
        if event:
            self.postEvent(event)

    def handleForsage(self, value):
        if not CameraEffect.g_instance:
            return
        else:
            if self.__forsageValue is None:
                self.__forsageValue = CameraEffect.CameraEffectManager.PS_NORMAL
            cam = GameEnvironment.getCamera()
            cameraState = cam.getState()
            signal = CameraEffect.g_instance._CameraEffectManager__forsageValueToSignal(value)
            if signal != self.__forsageValue and (signal == CameraEffect.CameraEffectManager.PS_NORMAL or cameraState in CameraEffect.g_instance._CameraEffectManager__FORSAGE_STATES):
                if signal == CameraEffect.CameraEffectManager.PS_FORSAGE:
                    WWISE_.setState(CAMERA_SOUND.FORSAGE.STATE, CAMERA_SOUND.FORSAGE.ON)
                elif signal == CameraEffect.CameraEffectManager.PS_STOP:
                    if self.__forsageValue == CameraEffect.CameraEffectManager.PS_FORSAGE:
                        WWISE_.setState(CAMERA_SOUND.FORSAGE.STATE, CAMERA_SOUND.FORSAGE.OFF)
                elif self.__forsageValue == CameraEffect.CameraEffectManager.PS_FORSAGE:
                    WWISE_.setState(CAMERA_SOUND.FORSAGE.STATE, CAMERA_SOUND.FORSAGE.OFF)
                self.__forsageValue = signal
            return