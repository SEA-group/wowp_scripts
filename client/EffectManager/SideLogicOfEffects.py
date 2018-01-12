# Embedded file name: scripts/client/EffectManager/SideLogicOfEffects.py
import BigWorld
import db.DBLogic
import Math
import math
import MapEffectsSettings
import time
from GunsController.Gun import Gun
from random import choice
from MathExt import km_to_m, sign
from consts import ACTION_DEALER, DAMAGE_REASON, WORLD_SCALING, IS_EDITOR
from EffectManager.ScreenCracksGenerator import ScreenCracksGenerator
if not IS_EDITOR:
    import CameraEffect

    def onCameraEffect(*args, **kwargs):
        if CameraEffect.g_instance is not None:
            CameraEffect.g_instance.onCameraEffect(*args, **kwargs)
        return


else:

    def onCameraEffect(*args, **kwargs):
        pass


_flyIdleLevelSpeed = tuple(reversed((km_to_m(0),
 km_to_m(30),
 km_to_m(150),
 km_to_m(300),
 km_to_m(400),
 km_to_m(500),
 km_to_m(600),
 km_to_m(700),
 km_to_m(800),
 km_to_m(900))))

class SideLogicOfEffects(object):

    def __init__(self, emInst):
        self._emInst = emInst
        self._isInForsageState = False
        self._isInSniperState = False
        self._freeCameraState = False
        self.__lowHealth = False
        self._bomber_idle_effect = None
        self.__brusUillisEffects = set()
        self.__lastFlyIdleLevelEffectData = ('', None)
        self.__screenCracksGenerator = ScreenCracksGenerator()
        self.__shotFeedbackTimers = {}
        if not IS_EDITOR:
            self.playerDeathEffect(False)
        return

    def destroy(self):
        _, lfe = self.__lastFlyIdleLevelEffectData
        self.__lastFlyIdleLevelEffectData = ('', None)
        if lfe is not None:
            lfe.destroy()
        if self._bomber_idle_effect is not None:
            self._bomber_idle_effect.destroy()
            self._bomber_idle_effect = None
        self.__brusUillisEffects.clear()
        self._emInst = None
        return

    @staticmethod
    def getDamageAngle(authorID):
        import gui.HUDconsts as hudConst
        author = BigWorld.entities.get(authorID)
        if author:
            screenPos = BigWorld.worldToScreen(author.position)
            screenCenterPos = Math.Vector3(BigWorld.screenWidth() / 2, BigWorld.screenHeight() / 2, 0)
            deltaPos = screenPos - screenCenterPos
            side = deltaPos.z
            deltaPos.z = 0
            deltaPos.normalise()
            pos = deltaPos * hudConst.CIRCLE_HUD_DAMAGE_DIRECTION_R
            if side < 0:
                pos *= -1
            angle = math.atan2(pos.x, pos.y) - hudConst.CIRCLE_HUD_DAMAGE_DIRECTION_PICTURE_ROTATION + math.pi
            angle = 2 * math.pi - angle
            return angle
        return 0

    def trySpawnScreenCrack(self, lastDamagerID, currHp, dHp):
        spawnAngle = SideLogicOfEffects.getDamageAngle(lastDamagerID)
        self.__screenCracksGenerator.isCracksAclive(self._emInst.isScreenParticlesActive)
        self._emInst.setScreenParticle(self.__screenCracksGenerator.trySpawnCrackWithCD(spawnAngle, dHp))
        self._emInst.setScreenParticle(self.__screenCracksGenerator.trySpawnCrackOnLossHP(spawnAngle, currHp))

    def flyIdleLevel(self, translationMatrix, speed):

        def getNewParticle(effectName):
            return self._emInst.createModelTargetEffect(db.DBLogic.g_instance.getEffectId(effectName), {'variant': 'OWN',
             'matrix': translationMatrix,
             'setVisible': True})

        for n, fixedSpeed in enumerate(_flyIdleLevelSpeed):
            if speed >= fixedSpeed:
                currEffectName = 'fly_idle_level_0' + str(len(_flyIdleLevelSpeed) - n - 1)
                lastEffectName, lastEffect = self.__lastFlyIdleLevelEffectData
                if currEffectName != lastEffectName:
                    if lastEffect is not None:
                        lastEffect.setVisible(False)
                    self.__lastFlyIdleLevelEffectData = (currEffectName, getNewParticle(currEffectName))
                break

        return

    def updateForsageEffects(self, state):
        self._isInForsageState = state
        if self._freeCameraState:
            state = False
        arenaData = db.DBLogic.g_instance.getArenaData(BigWorld.player().arenaType)
        mapEffects = MapEffectsSettings.EFFECTS.get(arenaData.geometryName, {})
        if mapEffects:
            forsage_effect = mapEffects[MapEffectsSettings.Groups.SPEED][MapEffectsSettings.SpeedWiseEffects.FORSAGE]
            sniper_forsage_effect = mapEffects[MapEffectsSettings.Groups.SPEED][MapEffectsSettings.SpeedWiseEffects.FORSAGE_SNIPER]
            if state:
                self._emInst.setScreenParticle('screen_forsage_vinetka', active=False)
                self._emInst.setScreenParticle('screen_forsage_vinetka', active=True)
                if self._isInSniperState:
                    self._emInst.showScreenParticle(sniper_forsage_effect)
                    self._emInst.hideScreenParticle(forsage_effect)
                else:
                    self._emInst.hideScreenParticle(sniper_forsage_effect)
                    self._emInst.showScreenParticle(forsage_effect)
            else:
                self._emInst.hideScreenParticle(sniper_forsage_effect)
                self._emInst.hideScreenParticle(forsage_effect)

    def setSniperMode(self, state):
        self._isInSniperState = state
        self.updateForsageEffects(self._isInForsageState)

    def onFreeCameraStateChange(self, state):
        self._freeCameraState = state
        self.updateForsageEffects(self._isInForsageState)

    def brusUillisInAction(self, curr_health, max_health):
        effects = {'screen_damage_overlife_01',
         'screen_damage_overlife_02',
         'screen_damage_overlife_03',
         'screen_damage_overlife_04',
         'screen_damage_overlife_05',
         'screen_damage_overlife_06',
         'screen_damage_overlife_07',
         'screen_damage_overlife_08'}
        pr_cfc = 0.1 * max_health
        if curr_health <= max_health * 0.01:
            return
        range_effects = int((max_health - curr_health) / pr_cfc) - len(self.__brusUillisEffects)
        progress = sign(range_effects) > 0
        for _ in xrange(abs(range_effects)):
            can_be_use = list(effects - self.__brusUillisEffects) if progress else list(self.__brusUillisEffects)
            if len(can_be_use):
                curr_effect = choice(can_be_use)
                if progress:
                    self.__brusUillisEffects.add(curr_effect)
                else:
                    self.__brusUillisEffects.remove(curr_effect)
                self._emInst.setScreenParticle(curr_effect, active=progress)

    def bomberCloudEffectVisible(self, value):
        from CommonSettings import BOMBER_EFFECTS
        if self._bomber_idle_effect is None:
            om = Math.Matrix()
            om.translation = BOMBER_EFFECTS.idleClouds.params['offset']
            m = Math.MatrixProduct()
            m.a = BigWorld.player().realMatrix
            m.b = om
            effectID = db.DBLogic.g_instance.getEffectId(BOMBER_EFFECTS.idleClouds.name)
            self._bomber_idle_effect = self._emInst.createModelTargetEffect(effectID, {'matrix': m})
        self._bomber_idle_effect.setVisible(value)
        return

    def updateHealthEffects(self, currHealth, maxHealth, lastDamage):
        from GameModeSettings.ACSettings import LOW_HEALTH_STATE_PER_TYPE
        lhs = LOW_HEALTH_STATE_PER_TYPE.get(BigWorld.player().planeType, 0.0)
        lowHp = currHealth / maxHealth <= lhs and currHealth > 0.0
        if not self.__lowHealth == lowHp:
            if lowHp:
                if not self.__lowHealth:
                    self._emInst.showScreenParticle('screen_near_death')
                    self._emInst.showScreenParticle('screen_blood_near_death')
            elif self.__lowHealth:
                self._emInst.hideScreenParticle('screen_near_death', clearPixie=True)
                self._emInst.hideScreenParticle('screen_blood_near_death', clearPixie=True)
            self.__lowHealth = lowHp
        if currHealth <= 0:
            self.playerDeathEffect()

    def playerDeathEffect(self, status = True):
        onCameraEffect('PLAYER_DEATH', status)
        self._emInst.setScreenParticle('player_death', active=True)

    def playerCritEffect(self):
        self._emInst.setScreenParticle('screen_player_crit')
        onCameraEffect('PLAYER_CRITICAL_HIT')

    def enemyCritEffect(self):
        self._emInst.setScreenParticle('screen_enemy_crit_flash')

    def enemyKillEffect(self, killingInfo, distance = 500 * WORLD_SCALING):
        killer = killingInfo['lastDamageType']
        actionDealer = killer is ACTION_DEALER.PILOT or killer is ACTION_DEALER.GUNNER and BigWorld.player().controlledGunner.isClientInAction
        if actionDealer and killingInfo['damageReason'] == DAMAGE_REASON.BULLET:
            onCameraEffect('ENEMY_KILL')
        distEffects = {0: 'screen_enemy_death_flash_close',
         300: 'screen_enemy_death_flash',
         600: 'screen_enemy_death_flash_far'}
        for dk in (600, 300, 0):
            if distance >= dk * WORLD_SCALING:
                self._emInst.setScreenParticle(distEffects[dk])
                break

    def shotFeedback(self, gunID, gun):
        isMainWeapon = type(gun) is Gun
        isGunnerWeapon = BigWorld.player().controlledGunner.isActiveGun(gunID)
        if isMainWeapon or isGunnerWeapon:
            effectId = 'SHOT_FEEDBACK_{}'.format(gun.gunProfileName)
            curr_time = time.time()
            if self.__shotFeedbackTimers.get(effectId, 0) < curr_time:
                onCameraEffect(effectId)
                self.__shotFeedbackTimers[effectId] = curr_time + 1.0 / (max(float(gun.RPM), 0.01) / 60.0)