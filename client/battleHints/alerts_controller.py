# Embedded file name: scripts/client/battleHints/alerts_controller.py
import math
import MathExt
import BigWorld
import battleHints
from consts import PART_FLAGS, PART_TYPES_TO_ID, GUN_OVERHEATING_TEMPERATURE, WARNING_DISTANCE_TO_MAP_BORDER, UPDATABLE_TYPE, LOGICAL_PART, WORLD_SCALING
from Helpers.AvatarHelper import altitudeBombingZone
from gui.HUDconsts import LAUNCH_SHELL_RESULT_EMPTY, LAUNCH_SHELL_RESULT_INCORRECT_ANGLE
from EntityHelpers import EntityStates
from _preparedBattleData_db import preparedBattleData
from EntityHelpers import isAvatar, isDestructibleObject, canAimToEnemyEntity
import Settings
STALL_CFC = 1.2
REDUCTION_CFC = 2
OFFSET_CRASH_TIME = 1
ANGLE_TO_ENEMY_MAX_DANGER = math.radians(20)
ANGLE_TO_ENEMY_ZERO_DANGER = math.radians(60)
ENEMY_DIRECTION_MAX_DANGER = math.radians(10)
ENEMY_DIRECTION_ZERO_DANGER = math.radians(30)
DIST_TO_ENEMY_MAX_DANGER = 0.5
DIST_TO_ENEMY_ZERO_DANGER = 1.5
DANGER_MIN_INDICATED_LEVEL_YELLOW = 0.5
DANGER_MIN_INDICATED_LEVEL_RED = 0.85

class _PARTS:
    PILOT = 'Pilot'
    GUNNER = 'Gunner1'
    ENGINE = 'Engine'
    LEFT_WING = 'LeftWing'
    RIGHT_WING = 'RightWing'
    TAIL = 'Tail'


class AlertsController(object):
    PLAYERUAC_MAXPHASES = 3

    def __init__(self, gameEnv, messenger):
        self._messenger = messenger
        self._gameEnv = gameEnv
        self._partStates = {}
        self._arenaBounds = None
        self._updated = {self._stallSpeedCheck.__name__,
         self._updateBorderWarning.__name__,
         self._playerUnderAttackCheck.__name__,
         self._bomberAltitudeLimitation.__name__}
        self._setCollisionWarningSystem(Settings.g_instance.getGameUI().get('collisionWarningSystem'))
        Settings.g_instance.eCollisionWarningSystemEnabled += self._setCollisionWarningSystem
        self._playerUAC_phaseSize = 0
        self._playerUAC_currentPhase = 0
        self._playerUAC_entitiesIDs = []
        return

    def dispose(self):
        Settings.g_instance.eCollisionWarningSystemEnabled -= self._setCollisionWarningSystem
        self._gameEnv = None
        self._messenger = None
        return

    @property
    def _player(self):
        return self._gameEnv.playerAvatarProxy

    def _setCollisionWarningSystem(self, value):
        name = self._planeCrashCheck.__name__
        if value:
            self._updated.add(name)
        elif name in self._updated:
            self._updated.remove(name)

    def update(self, dt):
        if self._canPerformUpdate():
            map(lambda foo: getattr(self, foo)(), self._updated)
        else:
            self._partStates = {}

    def applyArenaData(self, arenaData):
        self._arenaBounds = arenaData['bounds']

    def onPartFlagSwitchedNotification(self, partID, flagID, flagValue):
        if flagID is PART_FLAGS.FIRE:
            hint = battleHints.ALERT_PLANE_IN_FIRE if flagValue else battleHints.ALERT_FIRE_STOPPED
            self._messenger.pushMessage(hint)

    def reportEngineOverheat(self):
        self._messenger.pushMessage(battleHints.ALERT_ENGINE_OVERHEAT)

    def onGunGroupFire(self, group):
        if self._player.getWeaponController().isGunsOverHeated(GUN_OVERHEATING_TEMPERATURE):
            self._messenger.pushMessage(battleHints.ALERT_WEAPON_OVERHEAT)

    def onPartStateChanging(self, partData):
        cType = partData.partTypeData.componentType
        if cType not in PART_TYPES_TO_ID:
            return
        isAlive = partData.isAlive

        def checkValue(part, value):
            if self._partStates.get(part, True) != value:
                self._partStates[part] = value
                return True
            return False

        if cType == _PARTS.PILOT and checkValue(cType, isAlive):
            hint = battleHints.ALERT_CRIT_PILOT if not isAlive else battleHints.ALERT_PILOT_FIXED
            self._messenger.pushMessage(hint)
        if cType == _PARTS.GUNNER and checkValue(cType, isAlive):
            hint = battleHints.ALERT_CRIT_GUNNER if not isAlive else battleHints.ALERT_GUNNER_FIXED
            self._messenger.pushMessage(hint)
        if cType == _PARTS.ENGINE and checkValue(cType, isAlive):
            hint = battleHints.ALERT_CRIT_ENGINE if not isAlive else battleHints.ALERT_ENGINE_FIXED
            self._messenger.pushMessage(hint)
        if cType == _PARTS.LEFT_WING and checkValue(cType, isAlive):
            hint = battleHints.ALERT_CRIT_LEFT_WING if not isAlive else battleHints.ALERT_LEFT_WING_FIXED
            self._messenger.pushMessage(hint)
        if cType == _PARTS.RIGHT_WING and checkValue(cType, isAlive):
            hint = battleHints.ALERT_CRIT_RIGHT_WING if not isAlive else battleHints.ALERT_RIGHT_WING_FIXED
            self._messenger.pushMessage(hint)
        if cType == _PARTS.TAIL and checkValue(cType, isAlive):
            hint = battleHints.ALERT_CRIT_TAIL if not isAlive else battleHints.ALERT_TAIL_FIXED
            self._messenger.pushMessage(hint)

    def tryUseFlaps(self, value):
        if not preparedBattleData[self._player.globalID].flaps:
            self._messenger.pushMessage(battleHints.ALERT_FLAPS_MISSING)
        elif value:
            self._messenger.pushMessage(battleHints.ALERT_FLAPS_USED)

    def reportNoShell(self, shellID, result):
        if shellID == UPDATABLE_TYPE.ROCKET:
            if result == LAUNCH_SHELL_RESULT_EMPTY:
                self._messenger.pushMessage(battleHints.ALERT_ROCKET_IS_MISSING)
        elif shellID == UPDATABLE_TYPE.BOMB:
            if result == LAUNCH_SHELL_RESULT_EMPTY:
                self._messenger.pushMessage(battleHints.ALERT_BOMB_IS_MISSING)
            elif result == LAUNCH_SHELL_RESULT_INCORRECT_ANGLE:
                self._messenger.pushMessage(battleHints.ALERT_BOMBING_ANGLE_INCORRECT)

    def autopilot(self, newValue, oldValue):
        if newValue and not oldValue:
            self._messenger.pushMessage(battleHints.ALERT_AUTOPILOT)

    def _bomberAltitudeLimitation(self):
        side = altitudeBombingZone(self._player)
        if side > 0:
            self._messenger.pushMessage(battleHints.ALERT_HIGH_ALTITUDE_FOR_BOMBING)
        elif side < 0:
            self._messenger.pushMessage(battleHints.ALERT_LOW_ALTITUDE_FOR_BOMBING)

    def _playerUnderAttackCheck(self):
        playerDir = self._player.getRotation().getAxisZ()
        playerPos = self._player.position

        def isEnemy(entity):
            return isAvatar(entity) and canAimToEnemyEntity(self._player, entity)

        def enemyDirectionDanger(entity):
            toPlayer = playerPos - entity.position
            angleToPlayer = entity.getRotation().getAxisZ().angle(toPlayer)
            enemyDirectionNorm = MathExt.clamp(0.0, (angleToPlayer - ENEMY_DIRECTION_MAX_DANGER) / (ENEMY_DIRECTION_ZERO_DANGER - ENEMY_DIRECTION_MAX_DANGER), 1.0)
            return MathExt.lerp(1.0, 0.0, enemyDirectionNorm)

        def angleToEnemyDanger(entity):
            toEnemy = entity.position - playerPos
            rearDir = -1 * playerDir
            angleToEnemy = rearDir.angle(toEnemy)
            angleToEnemyNorm = MathExt.clamp(0.0, (angleToEnemy - ANGLE_TO_ENEMY_MAX_DANGER) / (ANGLE_TO_ENEMY_ZERO_DANGER - ANGLE_TO_ENEMY_MAX_DANGER), 1.0)
            return MathExt.lerp(1.0, 0.0, angleToEnemyNorm)

        def distToEnemyDanger(entity):
            toEnemy = entity.position - playerPos
            enemyReduction = entity.settings.airplane.flightModel.weaponOptions.reductionPoint * WORLD_SCALING
            distToEnemy = toEnemy.length / enemyReduction
            distToEnemyNorm = MathExt.clamp(0.0, (distToEnemy - DIST_TO_ENEMY_MAX_DANGER) / (DIST_TO_ENEMY_ZERO_DANGER - DIST_TO_ENEMY_MAX_DANGER), 1.0)
            return MathExt.lerp(1.0, 0.0, distToEnemyNorm)

        def isDanger(entity):
            return angleToEnemyDanger(entity) * enemyDirectionDanger(entity) * distToEnemyDanger(entity) >= DANGER_MIN_INDICATED_LEVEL_YELLOW

        def isEnemyTurret(entity):
            return not isAvatar(entity) and isDestructibleObject(entity) and canAimToEnemyEntity(self._player, entity)

        def isTurretAttack(entity):
            return entity.turretTargetID == self._player.id and entity.isTurretFiring

        self._playerUAC_currentPhase += 1
        if self._playerUAC_currentPhase == 1:
            self._playerUAC_entitiesIDs = BigWorld.entities.keys()
            self._playerUAC_phaseSize = len(self._playerUAC_entitiesIDs) / self.PLAYERUAC_MAXPHASES
            self._playerUAC_currentRange = (1, self._playerUAC_phaseSize)
        else:
            maxVal = len(self._playerUAC_entitiesIDs)
            self._playerUAC_currentRange = (min(self._playerUAC_currentRange[1] + 1, maxVal), min(self._playerUAC_phaseSize * self._playerUAC_currentPhase, maxVal))
            if self._playerUAC_currentRange[1] == maxVal:
                self._playerUAC_currentPhase = 0
        for i in range(self._playerUAC_currentRange[0], self._playerUAC_currentRange[1]):
            e = BigWorld.entities.get(self._playerUAC_entitiesIDs[i - 1], None)
            if e is not None:
                if isEnemy(e) and isDanger(e):
                    self._messenger.pushMessage(battleHints.ALERT_ENEMY_IS_BEHIND)
                if isEnemyTurret(e) and isTurretAttack(e):
                    self._messenger.pushMessage(battleHints.ALERT_TURRET_FIRE)

        return

    def _stallSpeedCheck(self):
        player = self._player
        hullID = player.logicalParts[LOGICAL_PART.HULL]
        stallSpeed = player.settings.airplane.flightModel.hull[hullID].stallSpeed
        if player.getSpeed() <= STALL_CFC * stallSpeed:
            self._messenger.pushMessage(battleHints.ALERT_STALL_SPEED)

    def _planeCrashCheck(self):
        speed = self._player.getSpeed() * WORLD_SCALING
        planePos = self._player.position
        planeDir = self._player.getRotation().getAxisZ()
        crashTrackPoint1 = planePos + planeDir * speed * (OFFSET_CRASH_TIME - 1)
        crashTrackPoint2 = planePos + planeDir * speed * OFFSET_CRASH_TIME
        crashCollide = BigWorld.hm_collideSimple(self._player.spaceID, crashTrackPoint1, crashTrackPoint2)
        if crashCollide is not None:
            self._messenger.pushMessage(battleHints.ALERT_PLANE_CRASH)
        return

    def _updateBorderWarning(self):
        owner = self._player
        if self._arenaBounds and not owner.autopilot:
            left = 10000000000.0
            right = -10000000000.0
            top = 10000000000.0
            bottom = -10000000000.0
            for point in self._arenaBounds:
                left = min(left, point.x)
                right = max(right, point.x)
                top = min(top, point.z)
                bottom = max(bottom, point.z)

            yaw = math.degrees(owner.yaw)
            x, _, z = owner.position
            canRightBound = right - x < WARNING_DISTANCE_TO_MAP_BORDER and 0 < yaw < 180
            canLeftBound = x - left < WARNING_DISTANCE_TO_MAP_BORDER and -180 < yaw < 0
            canBottomBound = bottom - z < WARNING_DISTANCE_TO_MAP_BORDER and -90 < yaw < 90
            canTopBound = z - top < WARNING_DISTANCE_TO_MAP_BORDER and (yaw < -90 or yaw > 90)
            if canRightBound or canLeftBound or canBottomBound or canTopBound:
                self._messenger.pushMessage(battleHints.ALERT_WARNING_AUTOPILOT)

    def _canPerformUpdate(self):
        if not self._player.inWorld:
            return False
        if not EntityStates.inState(self._player, EntityStates.GAME):
            return False
        return True