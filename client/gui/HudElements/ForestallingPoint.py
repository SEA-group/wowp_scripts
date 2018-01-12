# Embedded file name: scripts/client/gui/HudElements/ForestallingPoint.py
import BigWorld
import GUI
from consts import *
from gui.HUDconsts import *
from EntityHelpers import isAvatar, isTeamObject

class ForestallingPoint:

    def __init__(self, offsetMtx):
        self.__offsetMtx = offsetMtx
        self.__centerPointOffsetMtx = GUI.OffsetMp()
        self.__inited = False
        self.__matrixProvider = None
        return

    def setTarget(self, entity):
        if not self.__inited:
            self.__createTarget()
        if entity is not None and isAvatar(entity):
            self.__matrixProvider.target = entity.matrix
            self.__deflectionTarget(entity)
            self.__offsetMtx.target = self.__matrixProvider
            self.__centerPointOffsetMtx.target = self.__matrixProvider
            if COLLISION_RECORDER:
                self.__matrixProvider.targetEntity = entity
        else:
            self.__matrixProvider.target = None
            self.__deflectionTarget(None)
            if entity is not None and TEAM_OBJECT_PARALLAX_ENABLED and isTeamObject(entity):
                self.__offsetMtx.target = entity.matrix
                self.__centerPointOffsetMtx.target = entity.matrix
            else:
                self.__offsetMtx.target = None
                self.__centerPointOffsetMtx.target = None
            if COLLISION_RECORDER:
                self.__matrixProvider.targetEntity = None
        return

    def setBulletSpeed(self, bulletSpeed):
        if not self.__inited:
            self.__createTarget()
        self.__matrixProvider.bulletSpeed = bulletSpeed

    def destroy(self):
        self.__inited = False
        self.__matrixProvider = None
        self.__offsetMtx.target = None
        self.__offsetMtx = None
        self.__centerPointOffsetMtx.target = None
        self.__centerPointOffsetMtx = None
        return

    def __deflectionTarget(self, entity):
        BigWorld.player().deflectionTargetsInProgress += 1
        BigWorld.player().cell.setDeflectionTarget(entity.id if entity is not None else 0)
        return

    def __createTarget(self):
        self.__matrixProvider = GUI.ForestallingMp()
        self.__matrixProvider.source = BigWorld.player().fakeRealMatrix
        self.__matrixProvider.target = None
        self.__matrixProvider.offset = self.__offsetMtx
        if COLLISION_RECORDER:
            self.__matrixProvider.sourceEntity = BigWorld.player()
            self.__matrixProvider.targetEntity = None
        self.__inited = True
        return