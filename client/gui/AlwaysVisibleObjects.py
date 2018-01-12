# Embedded file name: scripts/client/gui/AlwaysVisibleObjects.py
import GameEnvironment
import Math
from MapEntry import MapEntry
import BigWorld
from EntityHelpers import unpackPositionFrom3DTuple, EntitySupportedClasses, unpackAngleFromByte
from debug_utils import LOG_DEBUG

class AlwaysVisibleObjects:

    def __init__(self):
        self.__list = {}

    def addAllTimeVisibleObject(self, entityID, classID, teamIndex, position, alive, modelID):
        """
        add object which must be visible on the map whole game time
        
        @param entityID: object ID
        @type entityID:int
        @param classID: EntitySupportedClasses const
        @type classID: int
        @param teamIndex: (0 or 1)
        @type teamIndex: int
        @param position: position for static objects
        @type position: Vector3
        @param alive: is object alive at this time (could be changed for restorable objects)
        @type alive: boolean
        @param modelID: object ID to get it settings
        @type modelID: int
        """
        self.__list[entityID] = MapEntry(entityID, classID, teamIndex, position, alive, modelID)
        self.__updateObjectVisibility(self.__list[entityID])

    def updateTemporaryVisibleObjectData(self, objectUpdatableData, objectClassID, objectTeamIndex, modelID):
        """
        add new object info or update it.
        Used for objects which could not be visible because of Bigworld issue
        
        @param objectUpdatableData:
        @type objectUpdatableData: ["id", "position", "angle", "isVisible"]
        @param objectClassID: EntitySupportedClasses const
        @type objectClassID: int
        @param objectTeamIndex: 0 or 1
        @type objectTeamIndex: int
        @param modelID: object ID to get it settings
        @type modelID: int
        """
        arenaData = GameEnvironment.getClientArena().arenaData
        iD, positionPacked, yawPacked, alive = objectUpdatableData
        position = unpackPositionFrom3DTuple(positionPacked, arenaData['bounds'])
        mapEntry = self.__list.get(iD, None)
        if not mapEntry:
            mapEntry = MapEntry(iD, objectClassID, objectTeamIndex, position, alive, modelID)
            self.__list[iD] = mapEntry
            if BigWorld.entities.has_key(iD):
                mapEntry.isClientInAOI = True
                BigWorld.entities[iD].onMapEntryCreated(mapEntry)
        else:
            mapEntry.isAlive = alive
            mapEntry.isClientInAOI = BigWorld.entities.has_key(iD)
        if mapEntry.isAlive:
            yaw = unpackAngleFromByte(yawPacked)
            mapEntry.setPositionAndYaw(Math.Vector3(position), yaw)
        if mapEntry.isObjectChanged:
            self.__updateObjectVisibility(mapEntry)
            mapEntry.resetMarksOfChanges()
        return

    def getMapEntry(self, objID):
        """return map entry for objID if present"""
        mapEntry = self.__list.get(objID, None)
        return mapEntry

    def getObjectName(self, id):
        if id in self.__list:
            return EntitySupportedClasses.getClassNameByID(self.__list[id].classID)
        else:
            return None

    def __updateObjectVisibility(self, obj):
        GameEnvironment.g_instance.eTemporaryVisibleObjectsUpdate(obj)