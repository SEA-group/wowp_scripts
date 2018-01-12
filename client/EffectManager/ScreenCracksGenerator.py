# Embedded file name: scripts/client/EffectManager/ScreenCracksGenerator.py
import BigWorld
import db.DBLogic
import math
from random import choice

class ScreenCracksGenerator(object):
    minHitCfc = 0.01
    cdTime = 0.35
    dHpCfc = 0.02
    cracksPos = dict(enumerate(['screen_hit_top_center',
     'screen_hit_top_center_right',
     'screen_hit_top_right',
     'screen_hit_right_top',
     'screen_hit_right',
     'screen_hit_right_bott',
     'screen_hit_bott_right',
     'screen_hit_bott_center_right',
     'screen_hit_bott_center',
     'screen_hit_bott_center_left',
     'screen_hit_bott_left',
     'screen_hit_left_bott',
     'screen_hit_left',
     'screen_hit_left_top',
     'screen_hit_top_left',
     'screen_hit_top_center_left']))

    def __init__(self):
        self.__zoneNumber = len(self.cracksPos)
        self.__spawnedZone = []
        self.__lastSpawnTime = -1
        self.__maxHp = -1
        self.__lastHp = -1

    def __calcHitZone(self, angle):
        step = 2 * math.pi / self.__zoneNumber
        zoneAngle = angle + 0.5 * step
        if zoneAngle > 2 * math.pi:
            zoneAngle -= 2 * math.pi
        return int(zoneAngle / step)

    def __calcSpawnZone(self, angle):
        spawnZone = self.__calcHitZone(angle)
        if spawnZone in self.__spawnedZone:
            for n in xrange(int(self.__zoneNumber / 2) + 1):
                spawnZoneL = spawnZone - n
                spawnZoneL = spawnZoneL if spawnZoneL >= 0 else self.__zoneNumber + spawnZoneL
                spawnZoneR = spawnZone + n
                spawnZoneR = spawnZoneR if spawnZoneR < self.__zoneNumber else spawnZoneR - self.__zoneNumber
                lNotIn = spawnZoneL not in self.__spawnedZone
                rNotIn = spawnZoneR not in self.__spawnedZone
                if lNotIn and rNotIn:
                    return choice([spawnZoneL, spawnZoneR])
                if lNotIn:
                    return spawnZoneL
                if rNotIn:
                    return spawnZoneR

            return -1
        return spawnZone

    def __firstHitInit(self):
        if self.__maxHp < 0:
            self.__maxHp = BigWorld.player().maxHealth
            self.__lastHp = self.__maxHp

    def __spawnCrack(self, spawnAngle):
        zone = self.__calcSpawnZone(spawnAngle)
        self.__spawnedZone.append(zone)
        return self.cracksPos.get(zone)

    def trySpawnCrackOnLossHP(self, spawnAngle, currHp):
        if self.__lastHp - currHp >= self.__maxHp * self.dHpCfc:
            self.__lastHp = currHp
            return self.__spawnCrack(spawnAngle)
        else:
            return None

    def trySpawnCrackWithCD(self, spawnAngle, dHp):
        t = BigWorld.time()
        if t - self.__lastSpawnTime > self.cdTime and dHp > self.minHitCfc * self.__maxHp:
            self.__lastSpawnTime = t
            return self.__spawnCrack(spawnAngle)
        else:
            return None

    def isCracksAclive(self, screenParticles):
        self.__firstHitInit()
        for n, p in self.cracksPos.iteritems():
            effectID = db.DBLogic.g_instance.getEffectId(p)
            if n in self.__spawnedZone and not screenParticles(effectID):
                self.__spawnedZone.remove(n)