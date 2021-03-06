# Embedded file name: scripts/common/Weapons.py
import collections
import BigWorld
import db.DBLogic
from operator import ior
from random import choice, uniform, random
from EntityHelpers import EntityStates, getEntityBattleLevelProperty, getRotation, getEntityPartDataByID, isTeamObject, getBulletExplosionEffectFromMaterial, getEntityVector, isAvatar, PART_ENUM
from AvatarControllerBase import AvatarControllerBase
from config_consts import IS_DEVELOPMENT
from db.DBEffects import Effects
from MathExt import repeatGauss, clamp
from consts import IS_CLIENT, IS_CELLAPP, WORLD_SCALING, LOGICAL_PART, SERVER_TICK_LENGTH, COMPONENT_TYPE, BOMB_ALLY_DAMAGE, GUN_TYPE, COLLISION_TYPE_TREE, BULLET_EFFECTIVE_DIST, DAMAGE_REASON, COLLISION_RECORDER, AUTOGIDER_ENABLED, ACTION_DEALER, AUTOGIDER_ANGLE_SCALE, FAM_PIVOT, FAM_SPEED_ETALON_MULT, FAM_CLAMP_MIN, FAM_CLAMP_MAX, BOMB_ENEMY_DAMAGE, AUTOGUIDER_SCALE_MINDIST, AUTOGUIDER_SCALE_MAXDIST, AUTOGUIDER_ANGLE_GROUND, DEAD_PILOT_ADD_DISPERSION, AUTOGUIDER_SMOOTH_ANGLE, AUTOGUIDER_FULL_POWER_ANGLE, AUTOGUIDER_SMOOTH_POWER, AUTOGUIDER_EDGE_MAX, AUTOGUIDER_EDGE_MIN, AUTOGUIDER_ANGULAR_MIN_PLATO, AUTOGUIDER_ANGULAR_MAX_PLATO, AUTOGUIDER_ANGULAR_MIN_EFFECT
import Math
import math
import MathExt
import db.DBLogic
from db.DBEffects import Effects
from debug_utils import *
from _airplanesConfigurations_db import airplanesConfigurations
from WeaponsHelpers import normalizeVictimsPartsMap, WeaponReductionDirHandler
from _skills_data import SpecializationEnum

def Angle(a, b):
    if a.length == 0 or b.length == 0:
        return 0
    angle = a.dot(b) / (a.length * b.length)
    return abs(math.acos(clamp(-1, angle, 1)))


class Weapons(AvatarControllerBase):

    def __init__(self, owner, guns):
        AvatarControllerBase.__init__(self, owner)
        self.__guns = guns
        self.__middleBulletSpeed = self.__guns.calculateMiddleBulletSpeed()
        self.__bulletSpeedForMostLargeCaliberGroup = self.__guns.calculateBulletSpeedForMostLargeCaliberGroup()
        self.__id = id
        self.fireFlags = 0
        self.oneTickFireFlag = 0
        self.__tempQuat = Math.Quaternion()
        self.__tempVec3 = Math.Vector3()
        self.__prevControllerPosition = None
        self.__prevControllerRotation = None
        self.__storedArmament = 0
        self.__pastTime = 0.0
        if IS_CLIENT:
            self.__registerGunsRender()
            self.__updateCallBack = None
            maxGroup = max(self.__guns.groups, key=lambda g: g.gunDescription.caliber) if self.__guns.groups else None
            self.__maxCaliberGroups = [ g for g in self.__guns.groups if g.gunDescription.caliber == maxGroup.gunDescription.caliber ]
            self.__so = {}
            self.__playingSounds = set()
            if IS_DEVELOPMENT:
                Weapons.drawBulletCollision = False
                Weapons.showBulletCollisionEffects = False
                from collections import deque
                Weapons.bulletCollisionEffectsQue = deque([], 50)
        self._wrdh = WeaponReductionDirHandler(self._owner)
        self.setOwner(owner)
        self.__isPilotDead = False
        return

    @property
    def guns(self):
        return self.__guns

    @property
    def weaponReductionDirHandler(self):
        return self._wrdh

    def onPartStateChanged(self, part):
        self.onPartsStateChanged([part])

    def onPartsStateChanged(self, parts):
        for part in parts:
            if part.enumName == PART_ENUM.PILOT:
                self.__isPilotDead = not part.isAlive
                break

    def onExtModifiersChanged(self, modifiers):
        if self._owner.armamentFreeUse != (modifiers.FREE_GUNS_FIRING != 1):
            self._owner.armamentFreeUse = modifiers.FREE_GUNS_FIRING != 1
            self.onArmamentFreeUseChanged(self._owner.armamentFreeUse)

    def onArmamentFreeUseChanged(self, flag):
        for i, group in enumerate(self.__guns.groups):
            group.onArmamentFreeUseChanged(flag)

    def setOwner(self, owner):
        AvatarControllerBase.setOwner(self, owner)
        self.__pastTime = 0.0
        self.__isMainEntityAvatar = False if not owner else isAvatar(owner)
        self._wrdh.setOwner(owner)
        if IS_CLIENT:
            if owner:
                self.__isPlayer = self._owner.isPlayer()
                self.__isOwnerAvatar = not isTeamObject(owner)
                self.__initClientUpdateCallBack()
            elif self.__updateCallBack:
                BigWorld.cancelCallback(self.__updateCallBack)
                self.__updateCallBack = None
        return

    def destroy(self):
        if IS_CLIENT:
            self.__maxCaliberGroups = None
            if self.__updateCallBack:
                BigWorld.cancelCallback(self.__updateCallBack)
                self.__updateCallBack = None
        self.__guns.destroy()
        self._wrdh.dispose()
        AvatarControllerBase.destroy(self)
        return

    def stopFiring(self):
        self.oneTickFireFlag = 0
        self.changeFireFlags(0)

    def changeFireFlags(self, flag):
        if flag == 0:
            self._owner.lastFireTime = BigWorld.time()
        else:
            self._owner.lastFireTime = 0
        self.fireFlags = flag
        self.oneTickFireFlag |= flag

    def restart(self):
        self.__guns.restart()
        self.stopFiring()
        self._wrdh.restart()

    def __getGunID(self, bullet):
        return bullet[2].gunID

    def backup(self):
        return {'guns': self.__guns.backup(),
         'fireFlags': self.fireFlags,
         'storedArmament': self.__storedArmament,
         'wrdh': self._wrdh.backup()}

    def restore(self, backupContainer):
        self.__guns.restoreFromBackup(backupContainer['guns'])
        self.fireFlags = backupContainer['fireFlags']
        self.__storedArmament = backupContainer['storedArmament']
        self._wrdh.restore(backupContainer['wrdh'])

    def getUsedGunsMask(self):
        """
        get used guns
        @return: {gunName: wasUsed}
        """
        return dict(((group.gunName, self.__storedArmament & 1 << i != 0) for i, group in enumerate(self.__guns.groups)))

    def getGunNames(self):
        return [ group.gunName for group in self.__guns.groups ]

    def update(self, dt):
        if EntityStates.inState(self._owner, EntityStates.GAME):
            self._wrdh.update(dt)
            if not self.__prevControllerPosition:
                self.__prevControllerPosition = Math.Vector3(self._owner.getShootingControllerPosition())
                self.__prevControllerRotation = Math.Quaternion(self._owner.getShootingControllerRotation())
            groups1 = reduce(ior, map(lambda group: group.singleShotBit, filter(lambda group: group.isReady(), self.__guns.groups)), 0)
            armaments = self.__guns.cellUpdate(dt, self.oneTickFireFlag | self.fireFlags)
            groups2 = reduce(ior, map(lambda group: group.singleShotBit, filter(lambda group: group.isReady(), self.__guns.groups)), 0)
            groups = ~groups1 & groups2
            if groups:
                self._owner.onSingleShotReady(groups)
            if COLLISION_RECORDER:
                self._owner.markPosition(0, self.__prevControllerPosition, self._owner.syncedRandom.getInfo())
            if self._owner.armamentStates and self._owner.armamentStates != armaments:
                self._owner.shootingSync = self._owner.syncedRandom.refresh()
                self.syncGunsRandom()
            if armaments != 0:
                self._owner.onDisclosure()
                self.__storedArmament |= armaments
                readyGroups = self.__guns.shoot(armaments)
                if readyGroups:
                    self.__shootCell(dt, readyGroups)
            self.oneTickFireFlag = 0
            if armaments != self._owner.armamentStates:
                if self._owner.armamentStates:
                    self._owner.syncGunsWithClient(self.__guns.getSyncData())
                self._owner.armamentStates = armaments
            self.__prevControllerPosition = Math.Vector3(self._owner.getShootingControllerPosition())
            if COLLISION_RECORDER:
                self._owner.markPosition(1, self.__prevControllerPosition, self._owner.syncedRandom.getInfo())
            self.__prevControllerRotation = Math.Quaternion(self._owner.getShootingControllerRotation())

    def syncGunsRandom(self):
        for group in self.__guns.groups:
            group.syncedRandom.state = self._owner.syncedRandom.randint(0, 65535)

    def __calcGunShootData(self, historyLayer, group, gun, gd, shootPosition, shootOrientation, bulletTime):
        bulletStartPos = shootPosition + shootOrientation.rotateVec(gun.posDelta)
        rnd = group.syncedRandom.random()
        externalModifiers = self._owner.controllers.get('externalModifiers', None) if hasattr(self._owner, 'controllers') else None
        autoAim = externalModifiers.modifiers.AUTO_AIM if externalModifiers else 1
        reductionDir = gun.reductionDir(self._wrdh.getLocalShootDirection(shootOrientation))
        if AUTOGIDER_ENABLED and autoAim:
            autoAimAngleMod = externalModifiers.modifiers.AUTOAIM_ANGLE if externalModifiers else 1
            aimAxis, aimAngle, entityId = self._owner.autoAim(historyLayer, bulletStartPos, shootOrientation.rotateVec(reductionDir), gd.bulletSpeed, gd.bulletFlyDist, bulletTime, AUTOGUIDER_ANGLE_GROUND, group.autoguiderAngle, autoAimAngleMod)
            entity = BigWorld.entities.get(entityId)
            if entity:
                autogiuderAngle = AUTOGUIDER_ANGLE_GROUND if isTeamObject(entity) else group.autoguiderAngle
                dist = (self._owner.position - entity.position).length
                norm = min(dist / gd.bulletFlyDist, 1.0)
                k = AUTOGUIDER_SCALE_MINDIST * (1 - norm) + AUTOGUIDER_SCALE_MAXDIST * norm
                if aimAngle < k * autogiuderAngle * autoAimAngleMod:
                    aimAngleNorm = aimAngle / (autogiuderAngle * k * autoAimAngleMod)
                    smoothCfc = MathExt.clamp(0.0, 1 - (aimAngleNorm - AUTOGUIDER_SMOOTH_ANGLE) / (1 - AUTOGUIDER_SMOOTH_ANGLE), 1.0)
                    if aimAngleNorm <= AUTOGUIDER_FULL_POWER_ANGLE:
                        autoguiderEdge = AUTOGUIDER_EDGE_MIN
                    else:
                        autoguiderEdge = AUTOGUIDER_EDGE_MIN + math.pow((aimAngleNorm - AUTOGUIDER_FULL_POWER_ANGLE) / (1 - AUTOGUIDER_FULL_POWER_ANGLE), AUTOGUIDER_SMOOTH_POWER) * (AUTOGUIDER_EDGE_MAX - AUTOGUIDER_EDGE_MIN)
                    angularArgument = Angle(getEntityVector(self._owner), getEntityVector(entity))
                    if angularArgument > math.pi * 0.5:
                        angularArgument = math.pi - angularArgument
                    angularNorm = MathExt.clamp(0.0, (angularArgument - AUTOGUIDER_ANGULAR_MIN_PLATO) / (AUTOGUIDER_ANGULAR_MAX_PLATO - AUTOGUIDER_ANGULAR_MIN_PLATO), 1.0)
                    angularCfc = MathExt.lerp(AUTOGUIDER_ANGULAR_MIN_EFFECT, 1.0, angularNorm)
                    if rnd >= autoguiderEdge:
                        minAngle = aimAngle * AUTOGIDER_ANGLE_SCALE * smoothCfc * angularCfc
                    else:
                        minAngle = aimAngle * AUTOGIDER_ANGLE_SCALE * rnd * smoothCfc * angularCfc
                    self.__tempQuat.fromAngleAxis(minAngle, aimAxis)
                    shootOrientation = self.__tempQuat.mul(shootOrientation)
        axisRnd, powRnd = group.syncedRandom.random(), group.syncedRandom.random()
        shootDirection = self.__calculateBulletDir(shootOrientation, group, reductionDir, axisRnd, powRnd)
        bulletMinFlightDist = self._owner.settings.airplane.flightModel.weaponOptions.bulletMinFlightDist
        distDispersion = bulletMinFlightDist + (1 - bulletMinFlightDist) * rnd
        return (bulletStartPos,
         shootDirection * gd.bulletSpeed,
         gd.bulletFlyDist * distDispersion / gd.bulletSpeed,
         axisRnd,
         powRnd)

    def __grid(self, a, base):
        if a > 0:
            ab = a / base
            c = int(ab)
            return c + int(ab - c - 1)
        return int(a / base) - 1

    def __shootCell(self, dt, weaponGroups):
        controllerRotation = self._owner.getShootingControllerRotation()
        shootOrientation = Math.Quaternion()
        firedBulletCount = 0
        groups = 0
        modsActivity = self._owner.getTargetSkillModsActivity(SpecializationEnum.PILOT)
        fmTimeOffset = float(self._owner.fmTimeOffset) / 255
        for group in weaponGroups:
            gd = group.gunDescription
            while group.isReady():
                shootTime = group.shoot(dt) - fmTimeOffset
                historyLayer = -(self.__grid(shootTime, dt) + 1)
                if historyLayer < 0 or historyLayer > 31:
                    prev, current = self.__prevControllerPosition, self._owner.getShootingControllerPosition()
                    if historyLayer < -1 or historyLayer > 31:
                        LOG_ERROR('Wrong history: dt = {0}, shootTime = {1}, historyLayer = {2}, fmTimeOffset = {3}'.format(dt, shootTime, historyLayer, fmTimeOffset))
                        shootTime += fmTimeOffset
                        historyLayer = -1
                else:
                    prev, current = self._owner.historyPosition(historyLayer)
                shootTime += (historyLayer + 1) * dt
                shootPosition = (current - prev) * shootTime / dt + prev
                if COLLISION_RECORDER:
                    self._owner.markPosition(2, shootPosition, 'shootTime = {0}\nbulletFlyDist = {1}\nbulletSpeed = {2}\n{3}'.format(shootTime, gd.bulletFlyDist, gd.bulletSpeed, group.syncedRandom.getInfo()))
                shootOrientation.slerp(self.__prevControllerRotation, controllerRotation, shootTime / dt)
                bulletTime = dt - shootTime
                for gun in group.guns:
                    bulletStartPos, bulletVelocity, timeToLive, axisRnd, powRnd = self.__calcGunShootData(historyLayer + 1, group, gun, gd, shootPosition, shootOrientation, bulletTime)
                    firedBulletCount += 1
                    self._owner.addBulletBody(historyLayer + 1, bulletStartPos, bulletVelocity, bulletTime, timeToLive, gd.weaponType == GUN_TYPE.AA or gd.weaponType == GUN_TYPE.AA_NORMAL, {'ammoID': group.shootInfo.index,
                     'gunID': gd.index,
                     'shooterID': self._owner.id,
                     'modsActivity': modsActivity})
                    groups |= group.singleShotBit

        if groups:
            self._owner.onSingleShot(groups)
        if self.__isMainEntityAvatar:
            self._owner.onShot(ACTION_DEALER.PILOT, firedBulletCount)

    def __shootClient(self, dt, weaponGroups):
        controllerPosition = self._owner.getShootingControllerPosition()
        controllerRotation = self._owner.getShootingControllerRotation()
        rotation = self._owner.getRotation()
        shootOrientation = Math.Quaternion()
        groups = 0
        sounds = set()
        for group in weaponGroups:
            gd = group.gunDescription
            weaponSoundID = group.gunProfile.sounds.weaponSoundID
            sounds.add(weaponSoundID)
            self.__onGunGroupFire(group)
            while group.isReady():
                shootTime = group.shoot(dt)
                if group.gunProfile.clientSkipBulletCount == 0 or group.clientProcessedBulletCount % group.gunProfile.clientSkipBulletCount == 0:
                    if COLLISION_RECORDER:
                        shootPosition = (controllerPosition - self.__prevControllerPosition) * shootTime / dt + self.__prevControllerPosition
                        self._owner.markPosition(2, shootPosition, 'shootTime = {0}\nbulletFlyDist = {1}\nbulletSpeed = {2}\n{3}'.format(shootTime, gd.bulletFlyDist, gd.bulletSpeed, group.syncedRandom.getInfo()))
                    for gun in group.guns:
                        shootOrientation.slerp(self.__prevControllerRotation, controllerRotation, shootTime / dt)
                        bulletTime = dt - shootTime
                        shootPosition = (controllerPosition - self.__prevControllerPosition) * shootTime / dt + self.__prevControllerPosition
                        bulletStartPos, bulletVelocity, timeToLive, axisRnd, powRnd = self.__calcGunShootData(0, group, gun, gd, shootPosition, shootOrientation, bulletTime)
                        data = {'gunID': gd.index,
                         'isPlayer': self.__isPlayer}
                        bulletEndPos, terrainMatKind, treeEndPos = self._owner.addBulletBody(0, bulletStartPos, bulletVelocity, bulletTime, timeToLive, False, data)
                        explosionEffect = terrainMatKind != -1 and getBulletExplosionEffectFromMaterial(group.gunProfile, db.DBLogic.g_instance.getMaterialName(terrainMatKind)) or None
                        bulletSpeed = bulletVelocity.length
                        gun.shootInfo = group.shootInfo
                        bulletStartPos = controllerPosition + rotation.rotateVec(gun.posDelta)
                        bulletTime = -(shootTime + random() * group.gunProfile.bulletGroupDispersionCfc * 60 / gun.RPM)
                        if treeEndPos:
                            data['bullets'] = [self._owner.addBullet(bulletStartPos, bulletEndPos, bulletSpeed, bulletTime, gun, explosionEffect, -bulletTime, dPos=gun.posDelta), self._owner.addInvisibleBullet(bulletStartPos, treeEndPos, bulletSpeed, bulletTime, group, getBulletExplosionEffectFromMaterial(group.gunProfile, db.DBLogic.g_instance.getMaterialName(COLLISION_TYPE_TREE)))]
                        else:
                            data['bullets'] = [self._owner.addBullet(bulletStartPos, bulletEndPos, bulletSpeed, bulletTime, gun, explosionEffect, -bulletTime, dPos=gun.posDelta)]
                        groups |= group.singleShotBit

                group.clientProcessedBulletCount += 1

        if groups:
            self._owner.onSingleShot(groups)
        self.__playShootingSounds(sounds)
        return

    def getSyncData(self):
        return self.__guns.getSyncData()

    @staticmethod
    def doExplosiveDamage(owner, bulletPos, explosionRadius, explosionRadiusEffective, explosionDamage, damageReason = DAMAGE_REASON.COMMON_EXPLOSION):
        try:
            spaceID = owner.spaceID
        except:
            return

        closestParts = BigWorld.hm_closestParts(spaceID, bulletPos, explosionRadius)
        if not closestParts:
            return
        victimsMap = {}
        for victim, partId, closestPos, dist in closestParts:
            isFriendlyVictim = victim.teamIndex == owner.teamIndex
            if not (isFriendlyVictim and isTeamObject(victim)):
                victimParts = victimsMap.get(victim, [])
                if not victimParts:
                    victimsMap[victim] = victimParts
                victimParts.append((partId, dist))

        normalizeVictimsPartsMap(victimsMap)
        for victim, victimParts in victimsMap.items():
            victimData = db.DBLogic.g_instance.getDestructibleObjectData(victim)
            damagedParts = []
            storePartId = -1
            storeDamage = -1
            if isTeamObject(victim):
                numParts = len(victimParts)
            else:
                numParts = 1
            isFriendlyVictim = victim.teamIndex == owner.teamIndex
            for partId, dist in victimParts:
                victimPartData = getEntityPartDataByID(victim, partId, victimData)
                if victimPartData:
                    if isFriendlyVictim:
                        if damageReason == DAMAGE_REASON.BOMB_EXPLOSION:
                            damage = BOMB_ALLY_DAMAGE
                        elif damageReason == DAMAGE_REASON.ROCKET_EXPLOSION:
                            damage = owner.SETTINGS.ROCKET_ALLY_DAMAGE
                        else:
                            damage = 1.0
                    elif isAvatar(victim) and damageReason == DAMAGE_REASON.BOMB_EXPLOSION:
                        damage = BOMB_ENEMY_DAMAGE
                    else:
                        damage = 1.0
                    if dist < explosionRadiusEffective:
                        damage *= explosionDamage / numParts
                    elif dist <= explosionRadius:
                        damage *= explosionDamage * (explosionRadius - dist) / ((explosionRadius - explosionRadiusEffective) * numParts)
                    else:
                        LOG_ERROR('doExplosiveDamage : dist > explosionRadius, ', partId, 'for object', victim, victim.id)
                    if damage > 0:
                        damagedParts.append({'key': partId,
                         'value': damage})
                else:
                    LOG_ERROR('Invalid partID', partId, 'for object', victim, victim.id)

            if storeDamage > 0 and storePartId != -1:
                damagedParts.append({'key': storePartId,
                 'value': storeDamage})
            if damagedParts:
                victim.receiveExplosiveDamage(owner, damagedParts, owner.entityGroupMask, owner.teamIndex, damageReason, owner.unitNumber)

        owner.onHitTarget(victimsMap.iterkeys(), damageReason, ACTION_DEALER.PILOT)

    @staticmethod
    def doUnownedExplosion(spaceID, bulletPos, explosionRadius, explosionRadiusEffective, explosionDamage, teamIndex, damageReason = DAMAGE_REASON.COMMON_EXPLOSION):
        """
        Perform unowned explosion in specified point with specified params
        """
        closestParts = BigWorld.hm_closestParts(spaceID, bulletPos, explosionRadius)
        if not closestParts:
            return
        else:
            victimsMap = collections.defaultdict(list)
            for victim, partId, closestPos, dist in closestParts:
                if victim.teamIndex != teamIndex:
                    victimsMap[victim].append((partId, dist))

            normalizeVictimsPartsMap(victimsMap)
            for victim, victimParts in victimsMap.iteritems():
                victimData = db.DBLogic.g_instance.getDestructibleObjectData(victim)
                damagedParts = []
                storePartId = -1
                storeDamage = -1
                if isTeamObject(victim):
                    numParts = len(victimParts)
                else:
                    numParts = 1
                for partId, dist in victimParts:
                    victimPartData = getEntityPartDataByID(victim, partId, victimData)
                    if victimPartData:
                        damage = 1.0
                        if dist < explosionRadiusEffective:
                            damage *= explosionDamage / numParts
                        elif dist <= explosionRadius:
                            distK = (explosionRadius - dist) / ((explosionRadius - explosionRadiusEffective) * numParts)
                            damage *= explosionDamage * distK
                        else:
                            LOG_ERROR('doUnownedExplosion : dist > explosionRadius, ', partId, 'for object', victim.id)
                        if damage > 0:
                            damagedParts.append({'key': partId,
                             'value': damage})
                    else:
                        LOG_ERROR('Invalid partID', partId, 'for object', victim, victim.id)

                if storeDamage > 0 and storePartId != -1:
                    damagedParts.append({'key': storePartId,
                     'value': storeDamage})
                if damagedParts:
                    victim.receiveExplosiveDamage(None, damagedParts, 0, teamIndex, damageReason, 0)

            return

    @staticmethod
    def onClientBulletExplosion(gd, contacts, isPlayer, victim, bulletDir):
        materialId = isTeamObject(victim) and 254 or 255
        materialName = db.DBLogic.g_instance.getMaterialName(materialId)
        if hasattr(gd.explosionParticles, materialName):
            explosionEffectName = gd.explosionParticles.__dict__[materialName]
        else:
            explosionEffectName = gd.explosionParticles.default
        if explosionEffectName:
            import Avatar
            for position, partID, bbox, armor in contacts:
                Avatar.onBulletExplosion(Effects.getEffectId(explosionEffectName), isPlayer, position, bulletDir if materialName == 'aircraft' else None, victim)
                if isPlayer:
                    Weapons.debug_addBulletCollisionEffects(explosionEffectName)
                    Weapons.debug_drawBulletCollisionLines(position)

        return

    @staticmethod
    def calculateDistEffectiveness(gd, ad, bulletStartPos, bulletContactPoint):
        dist = (bulletContactPoint - bulletStartPos).length
        if dist > BULLET_EFFECTIVE_DIST:
            l = gd.bulletFlyDist - BULLET_EFFECTIVE_DIST
            if l > 0:
                bulletEffectivenessOnMaxDist = ad.kineticPartMaxDist / ad.kineticPartMinDist
                return (gd.bulletFlyDist - dist) / l * (1 - bulletEffectivenessOnMaxDist) + bulletEffectivenessOnMaxDist
        return 1.0

    @staticmethod
    def calculateBulletDamage(shooter, victim, gd, v0, shootInfo, distEffectiveness):
        k = max(0.0, v0 * distEffectiveness / (gd.bulletSpeed / WORLD_SCALING))
        damage = k * shootInfo.kineticPartMinDist * gd.DPS * 60.0 / gd.RPM
        distVector = victim.position - shooter.position
        v1 = getEntityVector(shooter)
        v2 = getEntityVector(victim)
        distLen = distVector.length
        vProjectionLen = 0 if distLen == 0 else (v1 - v2).dot(distVector) / distLen
        vSum = (Weapons.getEntityNominalSpeed(shooter) + Weapons.getEntityNominalSpeed(victim)) * WORLD_SCALING
        famK = 1.0 if vSum == 0.0 else FAM_PIVOT + (FAM_SPEED_ETALON_MULT - FAM_PIVOT) * vProjectionLen / vSum
        return damage * clamp(FAM_CLAMP_MIN, famK, FAM_CLAMP_MAX)

    @staticmethod
    def getEntityNominalSpeed(entity):
        if isAvatar(entity):
            settings = db.DBLogic.g_instance.getDestructibleObjectData(entity)
            return settings.flightModel.engine[airplanesConfigurations[entity.globalID].logicalParts[LOGICAL_PART.ENGINE]].maxSpeed
        else:
            return 0.0

    @staticmethod
    def onBulletCollision(victim, bulletStartPos, bulletSpeed, bulletDir, bulletPos, contacts, data):
        gunDescription = db.DBLogic.g_instance.getComponentByIndex(COMPONENT_TYPE.GUNS, data['gunID'])
        if IS_CLIENT:
            for bulletId in data['bullets']:
                if bulletId != None:
                    BigWorld.removeBullet(bulletId)

            Weapons.onClientBulletExplosion(gunDescription, contacts, data['isPlayer'], victim, bulletDir)
        else:
            shooter = BigWorld.entities.get(data['shooterID'], None)
            bIsTeamObject = isTeamObject(victim)
            if shooter and not victim.isDestroyed and (not bIsTeamObject or shooter.teamIndex != victim.teamIndex):
                ammoDescription = db.DBLogic.g_instance.getComponentByIndex(COMPONENT_TYPE.AMMO, data['ammoID'])
                distEffectiveness = Weapons.calculateDistEffectiveness(gunDescription, ammoDescription, bulletStartPos, bulletPos)
                damage = Weapons.calculateBulletDamage(shooter, victim, gunDescription, bulletSpeed / WORLD_SCALING, ammoDescription, distEffectiveness)
                parts = [ c[1] for c in contacts ]
                victim.receiveBullet(shooter, parts, shooter.entityGroupMask, shooter.teamIndex, data['ammoID'], data['gunID'], data['modsActivity'], shooter.objTypeID, shooter.unitNumber, damage)
                shooter.onHitTarget([victim], DAMAGE_REASON.BULLET, ACTION_DEALER.PILOT)
        return

    @staticmethod
    def onBulletEnd(bulletStartPos, bulletSpeed, bulletDir, bulletPos, data):
        pass

    @property
    def maxCaliber(self):
        if self.__maxCaliberGroups:
            return self.__maxCaliberGroups[0].gunDescription.caliber
        return 0

    def getMainWeaponGroupAimType(self):
        return self.__maxCaliberGroups[0].gunProfile.aimType

    def getGunGroupsInitialInfo(self):
        """return bullet counters for all weapon groups"""
        return self.__guns.getGunGroupsInitialInfo()

    def getGunGroupCounters(self):
        """return bullet counters for all weapon groups"""
        return self.__guns.getGunGroupCounters()

    def getGunGroupsStates(self):
        """return gun groups not able to shot now (overheated, destroyed etc)"""
        return self.__guns.getGunGroupsStates()

    def getMass(self):
        return self.__guns.getMass()

    def getDps(self):
        return self.__guns.getDps()

    def getFullDPS(self):
        return self.__guns.getFullDPS()

    def damagePerPass(self):
        return self.__guns.damagePerPass(self._owner.controllers['staticAttributesProxy'].stallSpeed)

    @property
    def middleBulletSpeed(self):
        return self.__middleBulletSpeed

    @property
    def bulletSpeedForMostLargeCaliberGroup(self):
        return self.__bulletSpeedForMostLargeCaliberGroup

    def getMaxVibroDispersionAngle(self):
        if self.__maxCaliberGroups:
            return sum((self.__getDispersion(g.dispersionAngle, g.reductionAngle) for g in self.__maxCaliberGroups)) / len(self.__maxCaliberGroups)
        return 0

    def getBaseDispersionAngle(self):
        if self.__maxCaliberGroups:
            return sum((g.dispersionAngle for g in self.__maxCaliberGroups)) / len(self.__maxCaliberGroups)
        return 0

    def __getDispersion(self, dispersionAngle, gunReduction):
        reduction, reductionMod = self._owner.dynamicalDispersionCfc()
        pilotReduction = DEAD_PILOT_ADD_DISPERSION if self.__isPilotDead else 0
        return (dispersionAngle + reduction + gunReduction + pilotReduction) * reductionMod

    def __calculateBulletDir(self, originalRotation, weaponGroup, reductionDir, axisRnd, powRnd):
        axisAngle = axisRnd * math.pi * 2.0
        self.__tempVec3.set(math.sin(axisAngle), math.cos(axisAngle), 0)
        angle = math.pow(powRnd, 1.5) * self.__getDispersion(weaponGroup.dispersionAngle, weaponGroup.reductionAngle)
        self.__tempQuat.fromAngleAxis(angle, self.__tempVec3)
        gunRotation = originalRotation.mul(self.__tempQuat)
        return gunRotation.rotateVec(reductionDir)

    def getWeaponGroupsMaxAttackRange(self):
        return self.__guns.getWeaponGroupsMaxAttackRange()

    def getGunGroups(self):
        return self.__guns.groups

    def syncGuns(self, data):
        self.__guns.syncGuns(data)

    def __initClientUpdateCallBack(self):
        """it's constructed to be called only for owner != None !!!"""
        if not self.__updateCallBack:
            self.__setClientUpdateCallBack()

    def __setClientUpdateCallBack(self):
        self.__updateCallBack = BigWorld.callback(SERVER_TICK_LENGTH, self.__clientUpdate)
        self.__lastUpdateTime = BigWorld.time()

    def __clientUpdate(self):
        dt = BigWorld.time() - self.__lastUpdateTime
        self.__setClientUpdateCallBack()
        if EntityStates.inState(self._owner, EntityStates.DEAD | EntityStates.OBSERVER):
            self.__stopShootingSounds()
        if EntityStates.inState(self._owner, EntityStates.GAME):
            self._wrdh.update(dt)
            if not self.__prevControllerPosition:
                self.__prevControllerPosition = Math.Vector3(self._owner.getShootingControllerPosition())
                self.__prevControllerRotation = Math.Quaternion(self._owner.getShootingControllerRotation())
            shootingGroups = self._owner.shootingGroups()
            singleShotGroups = self._owner.popSingleShotGroups(shootingGroups & self.__guns.singleShotMask)
            from Helpers.AvatarHelper import isSpectating
            if shootingGroups or singleShotGroups or self.__isPlayer or isSpectating(self._owner.id):
                if self.__pastTime > 0.0:
                    self.__guns.commonUpdate(self.__pastTime, 0)
                self.__guns.commonUpdate(dt, shootingGroups)
                self.__pastTime = 0.0
                shootClient = False
                shootingGroups &= ~self.__guns.singleShotMask
                weaponGroups = self.__guns.shoot(shootingGroups)
                if weaponGroups:
                    self.__shootClient(dt, weaponGroups)
                    shootClient = True
                if singleShotGroups:
                    self.__guns.reload(singleShotGroups)
                    weaponGroups = self.__guns.shoot(singleShotGroups)
                    if weaponGroups:
                        self.__shootClient(dt, weaponGroups)
                        shootClient = True
                if COLLISION_RECORDER:
                    self._owner.markPosition(0, self.__prevControllerPosition, self._owner.syncedRandom.getInfo())
                if not shootClient:
                    self.__stopShootingSounds()
            else:
                if self.__pastTime == 0.0:
                    self.__stopShootingSounds()
                self.__pastTime += dt
            self.__prevControllerPosition.set(self._owner.getShootingControllerPosition())
            if COLLISION_RECORDER:
                self._owner.markPosition(1, self.__prevControllerPosition, self._owner.syncedRandom.getInfo())
            self.__prevControllerRotation = self._owner.getShootingControllerRotation()
            if self.__isOwnerAvatar:
                self._owner.updateAmmo()
        Weapons.debug_showBulletCollisionEffects()

    def __registerGunsRender(self):
        for group in self.__guns.groups:
            group.ammoBelt.registerShotRender()

    def __onGunGroupFire(self, group):
        if group.isReady():
            self._owner.onGunGroupFire(group)

    def __playShootingSounds(self, arraySoundShot):
        for weaponSoundID, so in self.__so.iteritems():
            if weaponSoundID in arraySoundShot:
                if weaponSoundID not in self.__playingSounds:
                    if not so[0].isOneshot():
                        self.__playingSounds.add(weaponSoundID)
                    for s in so:
                        s.play()

            elif weaponSoundID in self.__playingSounds:
                self.__playingSounds.remove(weaponSoundID)
                for s in so:
                    s.stop()

    def __stopShootingSounds(self):
        for weaponSoundID, so in self.__so.iteritems():
            if weaponSoundID in self.__playingSounds:
                self.__playingSounds.remove(weaponSoundID)
                for s in so:
                    s.stop()

    def linkSound(self, wid, so):
        if wid not in self.__so:
            self.__so[wid] = []
        self.__so[wid].append(so)

    def getSounds(self, weaponSoundID):
        if weaponSoundID in self.__so:
            return self.__so[weaponSoundID]
        else:
            return None

    def isGunsOverHeated(self, minTemp):
        for group in self.__guns.groups:
            if group.temperature >= minTemp:
                return True

        return False

    def clearGunsOverheat(self, prc):
        for group in self.__guns.groups:
            group.clearTemperature(prc)

    def reload(self):
        for group in self.__guns.groups:
            group.reload()

    def syncGunsWithClient(self):
        self._owner.syncGunsWithClient(self.__guns.getSyncData())

    @staticmethod
    @debugFunction
    def debug_setDrawBulletCollisionLines(state):
        Weapons.drawBulletCollision = state

    @staticmethod
    @debugFunction
    def debug_setBCE(state):
        Weapons.showBulletCollisionEffects = state

    @staticmethod
    @debugFunction
    def debug_clearBulletCollisionLines():
        BigWorld.clearGroup('debugBulletCollisionLines')

    @staticmethod
    @debugFunction
    def debug_drawBulletCollisionLines(colisionPosition):
        if Weapons.drawBulletCollision:
            player = BigWorld.player()
            BigWorld.addDrawLine('debugBulletCollisionLines', player.position, colisionPosition, 1996554018, True)

    @staticmethod
    @debugFunction
    def debug_addBulletCollisionEffects(effectName):
        if Weapons.showBulletCollisionEffects:
            from time import time
            Weapons.bulletCollisionEffectsQue.append((time(), 'ExplosionEffect: ' + effectName))

    @staticmethod
    @debugFunction
    def debug_showBulletCollisionEffects(lifeTime = 1.5):
        if Weapons.showBulletCollisionEffects:
            from time import time
            ct = time()
            toShow = []
            for t, ef in Weapons.bulletCollisionEffectsQue:
                if ct - t < lifeTime:
                    toShow.append(ef)

            BigWorld.clearGroup('bulletCollisionEffects')
            BigWorld.addText('bulletCollisionEffects', '\n\n'.join(toShow), 50, 50, 4289864226L, True)