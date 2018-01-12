# Embedded file name: scripts/client/gui/MapEntry.py
import Math
import gui.HUDconsts as HUDconsts
from EntityHelpers import EntitySupportedClasses
from debug_utils import LOG_DEBUG
import db.DBLogic
import BigWorld
import consts

class MapEntry:

    def __init__(self, objID, classID, teamIndex, position, isAlive, modelID):
        self.id = objID
        self.classID = classID
        self.teamIndex = teamIndex
        self.mapMatrix = Math.Matrix()
        self.mapMatrix.setTranslate(position)
        self._isAlive = isAlive
        self.addedToPlate = False
        self._inClientWorld = False
        if self.classID == EntitySupportedClasses.TeamTurret:
            self.mapTexture = HUDconsts.HUD_MINIMAP_ENTITY_TYPE_TURRET
        elif self.classID == EntitySupportedClasses.TeamObject:
            settings = db.DBLogic.g_instance.getBaseData(modelID)
            if settings.turretName:
                self.mapTexture = HUDconsts.HUD_MINIMAP_ENTITY_TYPE_TURRET
            else:
                self.mapTexture = settings.type == consts.TYPE_TEAM_OBJECT.BIG and HUDconsts.HUD_MINIMAP_ENTITY_TYPE_TEAM_OBJECT_BASE or HUDconsts.HUD_MINIMAP_ENTITY_TYPE_TEAM_OBJECT
        elif EntitySupportedClasses.isAvatarClassID(self.classID):
            self.mapTexture = HUDconsts.HUD_MINIMAP_ENTITY_TYPE_AVATAR
        else:
            LOG_DEBUG('Unsupported class ID', self.classID)
            self.mapTexture = HUDconsts.HUD_MINIMAP_ENTITY_TYPE_UNKNOWN
        self.superiorityPoints = 0
        if not EntitySupportedClasses.isAvatarClassID(self.classID):
            self.superiorityPoints = db.DBLogic.g_instance.getBaseData(modelID).superiorityPoints
            self.superiorityPointsMax = self.superiorityPoints
        self._objectChanged = True

    def resetMarksOfChanges(self):
        self._objectChanged = False

    @property
    def isObjectChanged(self):
        return self._objectChanged

    @property
    def isAlive(self):
        return self._isAlive

    @isAlive.setter
    def isAlive(self, val):
        if self._isAlive != val:
            self._isAlive = val
            self._objectChanged = True

    @property
    def isClientInAOI(self):
        return self._inClientWorld

    @isClientInAOI.setter
    def isClientInAOI(self, val):
        if self._inClientWorld != val:
            self._inClientWorld = val
            self._objectChanged = True

    def getMapTexture(self):
        return self.mapTexture

    def setPositionAndYaw(self, newPos, yaw):
        self.mapMatrix.setRotateYPR((yaw, 0, 0))
        self.mapMatrix.translation = newPos
        self._objectChanged = True

    @property
    def position(self):
        return self.mapMatrix.translation

    @property
    def yaw(self):
        return self.mapMatrix.yaw