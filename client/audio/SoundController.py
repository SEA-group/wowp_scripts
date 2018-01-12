# Embedded file name: scripts/client/audio/SoundController.py
import BigWorld
from AvatarControllerBase import AvatarControllerBase
from modelManipulator.ModelManipulator3 import ObjectDataReader, CompoundBuilder
from audio import GameSound
from SoundBanksManager import SoundBanksManager
import db.DBLogic
from audio.SoundObjects import TurretSoundObjectsFactories, AircraftSoundObjectsFactories
import Helpers.BoolCombiner
import consts
from AKConsts import SOUND_OBJECT_TYPES, TURRET_SOUND
from EntityHelpers import EntityStates
import audio.debug

class SoundController(AvatarControllerBase):

    def __init__(self, owner, modelManipulator, entityID, weaponSoundID, turretSoundIDByTurretID):
        AvatarControllerBase.__init__(self, owner)
        self.__entityID = entityID
        self.__weaponSoundID = weaponSoundID
        self.__turretSoundIDByTurretID = turretSoundIDByTurretID
        self.__context = modelManipulator.context
        self.__isPlayer = BigWorld.player().id == self.__entityID
        self.__boolCombiner = Helpers.BoolCombiner.BoolCombiner()
        self.__partsByNames = self.__getPartsByNames()
        self.__soundObjects = {}
        self.__soundModeHandlers = {}
        self.__cache()
        self.__fillNodes()

    def __getNodeFromMountPoint(self, mountPoint):
        pathList = ObjectDataReader._resolvePath(mountPoint, '', self.__partsByNames)
        return self.__context.rootNode.resolvePath(CompoundBuilder.convertPath(pathList))

    def __getPartsByNames(self):
        modelParts = self.__context.objDBData.partsSettings.getPartsOnlyList()
        partsByNames = {}
        for partDb in modelParts:
            partsByNames[partDb.name] = partDb

        return partsByNames

    def __getModelContext(self):
        entity = BigWorld.entities.get(self.__entityID, None)
        if entity:
            modelManipulator = entity.controllers.get('modelManipulator', None)
            if modelManipulator:
                return modelManipulator.context
        return

    def __cache(self):
        info = db.DBLogic.g_instance.getAircraftSound(self.__context.objDBData.name)
        data = {'info': info,
         'isPlayer': self.__isPlayer,
         'weaponSoundID': self.__weaponSoundID,
         'turretSoundIDByTurretID': self.__turretSoundIDByTurretID,
         'soundObjects': self.__soundObjects,
         'context': self.__context,
         'partByNames': self.__partsByNames}
        if self.__turretSoundIDByTurretID:
            for soundObjectFactory in TurretSoundObjectsFactories:
                soundObjectFactory.getSoundObjectSettings(data)

        if not info:
            return
        for soundObjectFactory in AircraftSoundObjectsFactories:
            soundObjectFactory.getSoundObjectSettings(data)

    def __fillNodes(self):
        for soundObject in self.__soundObjects.values():
            soundObject.node = self.__getNodeFromMountPoint(soundObject.mountPoint)

    def updatePartsFlags(self, partsFlags):
        partsBitFlags = 0
        for partID, partFlags in partsFlags:
            partsBitFlags |= partFlags

        if self.__boolCombiner.setCondition(ObjectDataReader.fire(), bool(partsBitFlags & consts.PART_FLAGS.FIRE)):
            GameSound().onBurning(self.__context.entityId, self.__context.isPlayer, bool(partsBitFlags & consts.PART_FLAGS.FIRE))

    @property
    def soundObjects(self):
        return self.__soundObjects

    @property
    def soundModeHandlers(self):
        return self.__soundModeHandlers

    def getWwiseGameObject(self, soundObjectType):
        soundObject = self.__soundObjects.get(soundObjectType, None)
        if soundObject:
            return soundObject.wwiseGameObject
        else:
            return

    def destroy(self):
        SoundBanksManager.instance().unloadSoundCase(self.__entityID)
        self.__context = None
        self.__boolCombiner = None
        self.__partsByNames = None
        for soundHandler in self.__soundModeHandlers.values():
            soundHandler.clear()

        self.__soundModeHandlers = {}
        for soundObject in self.__soundObjects.values():
            soundObject.clear()

        self.__soundObjects = {}
        return

    def onTurretTargetChanged(self, turretId, turretTargetID):
        turretSound = self.getWwiseGameObject(SOUND_OBJECT_TYPES.TURRET(turretId))
        if turretSound:
            GameSound().interactiveMix.mixFocus.onTurretTargetChanged(self.__entityID, turretId, turretTargetID)