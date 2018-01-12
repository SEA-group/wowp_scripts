# Embedded file name: scripts/client/EffectManager/EffectsManager.py
import BigWorld
import db.DBLogic
import Math
from config_consts import IS_DEVELOPMENT
from debug_utils import LOG_TRACE, LOG_ERROR, LOG_DEBUG
from MathExt import clamp
from consts import IS_EDITOR
if not IS_EDITOR:
    import CameraEffect
from random import randint, choice
from consts import WORLD_SCALING
from clientConsts import BLAST_FORCE_DISTANCE_FACTOR, EFFECT_COLLISION_RANGE, BLAST_FORCE_MAX
from sets import Set
from EffectManager.Effects import EffectJet, EffectLoft, EffectLoopParticle, EffectTrailParticle, EffectModel, EffectTimedParticle

class EffectManager(object):
    EFFECT_CLASSES = {'LoopParticle': EffectLoopParticle,
     'TrailParticle': EffectTrailParticle,
     'TimedParticle': EffectTimedParticle,
     'Loft': EffectLoft,
     'Model': EffectModel,
     'Jet': EffectJet}

    def __init__(self):
        self.__particles = Set()
        self.__isFreeze = False
        self.__particleCache = {}
        self.__particleCount = {}
        self.__screenParticles = {}
        self.isDbgPrint = False
        self.__excludeEffects = tuple()

    def setFreeze(self, freeze):
        BigWorld.setPaticlesActive(not freeze)
        BigWorld.setBulletsActive(not freeze)
        self.__isFreeze = freeze

    def isFreeze(self):
        return self.__isFreeze

    def switchDebugPrinting(self):
        self.isDbgPrint = not self.isDbgPrint
        LOG_TRACE('Start EffectManager debug printing:', self.isDbgPrint)

    def getPreloadingResources(self):
        resourceList = []
        for effectID in db.DBLogic.g_instance.getEffectIds():
            varnames = db.DBLogic.g_instance.getEffectDataVariantNames(effectID)
            for name in varnames:
                effectDB = db.DBLogic.g_instance.getEffectDataVariant(effectID, name)
                if effectDB:
                    resourceFile = ''
                    if 'particleFile' in effectDB:
                        resourceFile = effectDB['particleFile']
                    if 'loftTexture' in effectDB:
                        resourceFile = effectDB['loftTexture']
                    if 'texture' in effectDB:
                        resourceFile = effectDB['texture']
                    if resourceFile != '':
                        resourceList.append(resourceFile)

        return resourceList

    def createWorldEffect(self, effectID, worldPos, properties, wasDelayed = False):
        effectDB = db.DBLogic.g_instance.getEffectDataVariant(effectID, properties.get('variant', 'OWN'))
        if effectDB is None:
            return ()
        else:
            count = int(effectDB.get('drawChance', 0))
            if count and count < randint(1, 100):
                return ()
            count = int(effectDB.get('maxCount', 0))
            if count:
                if effectID in self.__particleCount:
                    if self.__particleCount[effectID] > randint(1, int(count)):
                        return ()
                    self.__particleCount[effectID] += 1
                else:
                    self.__particleCount[effectID] = 1
            if worldPos is None:
                LOG_ERROR('Particle position is not Vector3 or tuple of 3')
                worldPos = Math.Vector3()
            if len(properties) > 0:
                effectProps = effectDB.copy()
                effectProps.update(properties)
            else:
                effectProps = effectDB
            attachData = {'type': effectDB.get('attachType', 'world'),
             'position': worldPos}
            if 'rotation' in properties:
                attachData['rotation'] = properties['rotation']
            if 'attachType' in properties:
                attachData['type'] = properties['attachType']
            if effectID in self.__particleCache and len(self.__particleCache[effectID]) > 0:
                effect = self.__particleCache[effectID].pop()
                effect.attachProperties = attachData
                effect.properties = effectProps
                if isinstance(effect, EffectTimedParticle):
                    effect.clearPixie()
                effect.attach()
            else:
                effect = self.__createEffect(effectDB['type'], effectProps, attachData)
            effect.effectID = effectID
            effects = [effect]
            if 'decal' in effectProps:
                decalData = effectProps['decal']
                decalTextureId = BigWorld.deferredImpactTextureIndex(decalData['texture'])
                if decalTextureId >= 0:
                    pos = Math.Vector3(worldPos)
                    decalStartRay = (pos[0], pos[1] + EFFECT_COLLISION_RANGE, pos[2])
                    decalEndRay = (pos[0], pos[1] - EFFECT_COLLISION_RANGE, pos[2])
                    BigWorld.addDeferredImpact(decalStartRay, decalEndRay, decalData['size'], decalTextureId)
            if 'blastForce' in effectProps:
                player = BigWorld.player()
                effectVec = worldPos - player.position
                effectBlastForce = effectProps['blastForce']
                if effectBlastForce > BLAST_FORCE_MAX:
                    effectBlastForce = clamp(0.0, effectBlastForce, BLAST_FORCE_MAX)
                force = (effectBlastForce - BLAST_FORCE_DISTANCE_FACTOR * (effectVec.length / WORLD_SCALING)) / BLAST_FORCE_MAX
                if CameraEffect.g_instance and force > 0 and not IS_EDITOR:
                    CameraEffect.g_instance.onCameraEffect('NEAR_EXPLOSION', True, force, effectVec)
                    self.showScreenParticle('screen_expl_dirt')
            if 'screenEffectID' in effectProps and not IS_EDITOR:
                self.setScreenParticle(effectProps['screenEffectID'], worldPos)
            if 'effectSet' in effectProps:
                if 'selectOne' in effectProps and effectProps['selectOne']:
                    effects += self.createWorldEffect(choice(effectProps['effectSet']), worldPos, properties)
                else:
                    for addEffect in effectProps['effectSet']:
                        effects += self.createWorldEffect(addEffect, worldPos, properties)

            return effects

    def createNodeAttachedEffect(self, effectID, node, properties, wasDelayed = False):
        effectDB = db.DBLogic.g_instance.getEffectDataVariant(effectID, properties.get('variant', 'OWN'))
        if effectDB is None:
            LOG_ERROR("can't find effect", effectID)
            return
        else:
            effectProps = effectDB.copy()
            effectProps.update(properties)
            attachData = {'type': 'model',
             'node': node}
            return self.__createEffect(effectDB['type'], effectProps, attachData)

    def createModelGroundedEffect(self, effectID, properties):
        effectDB = db.DBLogic.g_instance.getEffectDataVariant(effectID, properties.get('variant', 'OWN'))
        if effectDB is None:
            LOG_ERROR("can't find effect", effectID)
            return
        else:
            effectProps = effectDB.copy()
            effectProps.update(properties)
            attachData = {'type': 'model_grounded'}
            return self.__createEffect(effectDB['type'], effectProps, attachData)

    def createModelTargetEffect(self, effectID, properties):
        effectDB = db.DBLogic.g_instance.getEffectDataVariant(effectID, properties.get('variant', 'OWN'))
        if effectDB is None:
            LOG_DEBUG("can't find effect", effectID)
            return
        else:
            effectProps = effectDB.copy()
            effectProps.update(properties)
            attachData = {'type': 'model_target'}
            return self.__createEffect(effectDB['type'], effectProps, attachData)

    def createCameraAttachedEffect(self, effectID, sourcePos, properties, wasDelayed = False):
        effectDB = db.DBLogic.g_instance.getEffectDataVariant(effectID, properties.get('variant', 'OWN'))
        if effectDB is None or sourcePos and (sourcePos - BigWorld.player().position).length / WORLD_SCALING > effectDB['distance']:
            return
        else:
            effectProps = effectDB.copy()
            effectProps.update(properties)
            attachData = {'type': 'camera',
             'node': None}
            return self.__createEffect(effectDB['type'], effectProps, attachData)

    def setScreenParticle(self, effectName, sourcePos = None, active = True, relativeTransform = None):
        try:
            if effectName in self.__excludeEffects:
                return
        except Exception as error:
            LOG_ERROR(error)

        effectID = db.DBLogic.g_instance.getEffectId(effectName)
        if effectID:
            if active:
                particle = self.createCameraAttachedEffect(effectID, sourcePos, {'relativeTransform': relativeTransform})
                if particle:
                    if effectID in self.__screenParticles:
                        self.__screenParticles[effectID].append(particle)
                    else:
                        self.__screenParticles[effectID] = [particle]
                    particle.effectID = effectID
            else:
                particleType = self.__screenParticles.get(effectID)
                if particleType:
                    for particle in list(particleType):
                        particle.destroy()

    def showScreenParticle(self, effectName):
        effectID = db.DBLogic.g_instance.getEffectId(effectName)
        particles = self.__screenParticles.get(effectID, [])
        if len(particles) > 0:
            for particle in particles:
                particle.setVisible(True)

        else:
            self.setScreenParticle(effectName)

    def hideScreenParticle(self, effectName, clearPixie = False):
        effectID = db.DBLogic.g_instance.getEffectId(effectName)
        if effectID in self.__screenParticles:
            for particle in self.__screenParticles[effectID]:
                particle.setVisible(False)
                if clearPixie:
                    particle.clearPixie()

    def clearScreenParticles(self):
        for particleType in self.__screenParticles.values():
            particles = list(particleType)
            for particle in particles:
                particle.clearPixie()
                particle.destroy()

        self.__screenParticles = {}

    def clearParticlesCache(self):
        for particleType in self.__particleCache.values():
            for particle in particleType:
                particle.destroy()

        self.__particleCache = {}

    def destroy(self):
        particles = Set(self.__particles)
        for particle in particles:
            particle.destroy()

        self.clearParticlesCache()
        self.clearScreenParticles()
        if len(self.__particles):
            raise Exception('Not all particles deleted, error')

    def registerParticle(self, particle):
        self.__particles.add(particle)

    def getAllParticles(self):
        return self.__particles

    def unRegisterParticle(self, particle):
        self.__particles.discard(particle)
        if particle.attachProperties['type'] == 'world':
            if particle.effectID in self.__particleCache:
                self.__particleCache[particle.effectID].append(particle)
            else:
                self.__particleCache[particle.effectID] = [particle]
            if particle.effectID in self.__particleCount:
                self.__particleCount[particle.effectID] -= 1
        elif particle.attachProperties['type'] == 'camera':
            if particle.effectID in self.__screenParticles and particle in self.__screenParticles[particle.effectID]:
                self.__screenParticles[particle.effectID].remove(particle)

    def __createEffect(self, typeName, effectProps, attachData):
        if typeName in EffectManager.EFFECT_CLASSES:
            effectClass = EffectManager.EFFECT_CLASSES[typeName]
            return effectClass(effectProps, attachData, self)
        else:
            return None

    def isScreenParticlesActive(self, effectID):
        return len(self.__screenParticles.get(effectID, [])) > 0

    def setExcludeEffectsList(self, exclude):
        if IS_DEVELOPMENT:
            self.__excludeEffects = exclude
            self.clearScreenParticles()
        else:
            self.__excludeEffects = tuple()