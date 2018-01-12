# Embedded file name: scripts/client/EffectManager/Effects/_effectBase.py
import Math
from debug_utils import *
from random import uniform
from consts import WORLD_SCALING, IS_EDITOR
from clientConsts import LOCAL_PARTICLE_ADJUST
from audio import EffectSound
from audio import GameSound

class EffectBase:

    def __init__(self, properties, attachProperties, effectManager):
        self.properties = properties
        self.attachProperties = attachProperties
        self.effectManager = effectManager
        self.visible = True
        self.attached = False
        self._sound = None
        self.particleLoaded = False
        self.delayed = False
        self.delayCallbackId = None
        self.modelAttachNode = None
        self.effectAttachNode = None
        self.model = None
        self.sound_container = None
        if 'delay' in self.properties:
            self.delayed = True
            self.delayCallbackId = BigWorld.callback(uniform(self.properties['delay'][0], self.properties['delay'][1]), self.__onDelayEnds)
        else:
            self.__onDelayEnds()
        return

    def __onDelayEnds(self):
        self.delayed = False
        self.delayCallbackId = None
        if self.particleLoaded:
            self.attach()
        return

    def __playSound(self):
        if IS_EDITOR:
            return
        elif 'position' not in self.attachProperties:
            event = self.properties.get('SoundEffectID', None)
            if event:
                GameSound().camera.playCameraEffect(event)
            return
        else:
            pos = self.attachProperties['position']
            hitSFX = self.properties.get('sfx')
            if hitSFX:
                hitSFXManager = GameSound().hitSFXManager
                if hitSFXManager and hitSFXManager.canPlayEffect(hitSFX):
                    hitSFXManager.play(None, pos, hitSFX)
            explSFX = self.properties.get('exp')
            if explSFX:
                explosionSFXManager = GameSound().explosionSFXManager
                if explosionSFXManager:
                    explosionSFXManager.play(explSFX, pos)
            if 'SoundEffectID' not in self.properties:
                return
            self._sound = EffectSound(self.properties['SoundEffectID'], 0, 0, pos)
            return

    def __stopSound(self):
        if self._sound is None:
            return
        else:
            self._sound.stop()
            self._sound = None
            return

    def attach(self):
        if self.delayed or self.attached:
            return
        else:
            self.attached = True
            self.effectManager.registerParticle(self)
            overrideAttachType = self.properties.get('attachType')
            attachType = self.attachProperties['type'] if overrideAttachType is None else overrideAttachType
            if attachType == 'world':
                entity = self.properties.get('entity', None)
                if self.properties.get('attachToTarget', False) and entity is not None:
                    controllers = getattr(entity, 'controllers', None)
                    if controllers:
                        modelManipulator = controllers.get('modelManipulator')
                        if modelManipulator:
                            try:
                                rootModel = modelManipulator.getRootModel()
                                m = Math.Matrix(rootModel.matrix)
                                invRotation = Math.Quaternion()
                                invRotation.fromEuler(m.roll, m.pitch, m.yaw)
                                invRotation.invert()
                                localOffset = invRotation.rotateVec((self.attachProperties['position'] - m.translation) / WORLD_SCALING)
                                self.modelAttachNode = rootModel.node('Scene Root')
                                self.effectAttachNode = self.modelAttachNode
                                matrix = Math.Matrix()
                                rotation = self.properties.get('rotation')
                                if rotation:
                                    matrix.setRotateYPR(rotation)
                                matrix.translation = localOffset + LOCAL_PARTICLE_ADJUST
                                self.effectAttachNode.local = matrix
                            except:
                                LOG_CURRENT_EXCEPTION()

                else:
                    self.modelAttachNode = BigWorld.allocateGlobalNode()
                    self.effectAttachNode = self.modelAttachNode
                    if 'model' in self.attachProperties:
                        self.model = self.attachProperties['model']
                        self.modelAttachNode.attach(self.model)
                    rotation = self.properties.get('rotation')
                    if rotation:
                        matrix = Math.Matrix()
                        matrix.setRotateYPR(rotation)
                        matrix.translation = self.attachProperties['position']
                        self.modelAttachNode.local = matrix
                    else:
                        matrix = Math.Matrix()
                        matrix.translation = self.attachProperties['position']
                        self.modelAttachNode.local = matrix
                self.setVisible(True)
            elif attachType == 'model':
                self.modelAttachNode = self.attachProperties['node']
                self.effectAttachNode = self.modelAttachNode
                self.model = None
                if self.visible:
                    self.__playSound()
            else:
                if attachType == 'camera':
                    self.modelAttachNode = BigWorld.allocateGlobalNode()
                    self.effectAttachNode = self.modelAttachNode
                    localTransorm = self.properties.get('relativeTransform', None)
                    if localTransorm is not None:
                        attachMat = Math.MatrixProduct()
                        attachMat.a = localTransorm
                        attachMat.b = BigWorld.camera().billboardMatrix
                    else:
                        attachMat = BigWorld.camera().billboardMatrix
                    self.modelAttachNode.local = attachMat
                    self.setVisible(True)
                    return
                if attachType == 'model_grounded':
                    matrix = self.properties.get('matrix')
                    if matrix is not None:
                        self.modelAttachNode = BigWorld.allocateGlobalNode()
                        self.effectAttachNode = self.modelAttachNode
                        self.modelAttachNode.local = BigWorld.GroundedMatrixProvider(matrix)
                        self.setVisible(True)
                        return
                elif attachType == 'model_target':
                    matrix = self.properties.get('matrix')
                    if matrix is not None:
                        self.modelAttachNode = BigWorld.allocateGlobalNode()
                        self.effectAttachNode = self.modelAttachNode
                        self.modelAttachNode.local = matrix
                        self.setVisible(self.properties.get('setVisible', False))
                        return
            return

    def reAttachToNode(self, node):
        self.detach()
        self.attachProperties = {'type': 'model',
         'node': node}
        self.visible = True
        self.attach()

    def detach(self):
        if not self.attached:
            return
        else:
            self.attached = False
            self.setVisible(False)
            self.effectManager.unRegisterParticle(self)
            attachType = self.attachProperties['type']
            if attachType == 'world':
                if self.model is not None:
                    self.modelAttachNode.detach(self.model)
            elif attachType == 'model_grounded':
                self.modelAttachNode.local = None
            elif attachType == 'model_target':
                self.modelAttachNode.local = None
                self.modelAttachNode = None
                self.effectAttachNode = None
            elif attachType == 'model':
                if self.model is not None:
                    self.modelAttachNode.detach(self.model)
            if self.sound_container is not None:
                self.modelAttachNode.detach(self.sound_container)
            self.__stopSound()
            self.modelAttachNode = None
            self.effectAttachNode = None
            self.model = None
            self.sound_container = None
            return

    def destroy(self):
        if self.delayCallbackId is not None:
            BigWorld.cancelCallback(self.delayCallbackId)
            self.delayCallbackId = None
        self.detach()
        return

    def setVisible(self, value):
        self.visible = value
        if self.visible:
            self.__playSound()
        else:
            self.__stopSound()
        if self.effectManager.isDbgPrint:
            if self.visible:
                LOG_TRACE('START EFFECT:', self.properties.get('id', None), self.properties.get('sound', None))
            else:
                LOG_TRACE('END EFFECT:', self.properties.get('id', None))
        return

    def getPosition(self):
        return self.attachProperties.get('position', Math.Vector3(0, 0, 0))