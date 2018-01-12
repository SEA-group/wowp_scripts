# Embedded file name: scripts/common/updatable/UpdatableObjectSound.py
import BigWorld
from consts import IS_CLIENT
from UpdatableObjectBase import UPDATABLE_STATE
if IS_CLIENT:
    from audio.SoundObjects import ShellSound

def isClient(func):

    def wrapper(*args):
        if IS_CLIENT:
            func(*args)

    return wrapper


class UpdatableObjectSound:

    @isClient
    def __init__(self, soundName, creatorOwnerID):
        self.__soundName = soundName
        self.__soundObject = None
        return

    @isClient
    def updatePosition(self, position):
        if not self.__soundObject or self.__soundObject.destroyed:
            return
        self.__soundObject.setPosition(position)

    @isClient
    def startSound(self, weaponSoundID, position, state):
        if not weaponSoundID or UPDATABLE_STATE.DESTROY == state:
            return
        self.__soundObject = ShellSound('{0}-{1}'.format(self.__soundName, weaponSoundID), 0, 0, position, weaponSoundID)
        self.__soundObject.play()

    @isClient
    def stopSound(self):
        if self.__soundObject:
            self.__soundObject.stop()