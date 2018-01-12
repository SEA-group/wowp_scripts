# Embedded file name: scripts/client/_ge_achievements_coach.py
"""
This module is autogenerated don't modify any params,
after bundling they will be lost
"""
import Math
import math
import consts
import datetime
true = True
false = False

class Dummy:
    pass


isServerDatabase = False

class AMMO_TYPE:
    BALL = 0
    AP = 1
    APC = 2
    I = 3
    APHC = 4
    API = 5
    HEI = 6
    APHE = 7
    ALL_TYPES = (BALL,
     AP,
     APC,
     I,
     APHC,
     API,
     HEI,
     APHE)


class OperationModifyBy:
    add = 0
    multiply = 1
    ALL_TYPES = (add, multiply)


class OperationModifyType:
    exp = 0
    freeExp = 1
    credits = 2
    crewExp = 3
    ALL_TYPES = (exp,
     freeExp,
     credits,
     crewExp)


class SHELL_TYPE:
    BOMBS = 0
    ROCKETS = 1
    ALL_TYPES = (BOMBS, ROCKETS)


class WEAPON_AIM_TYPE:
    empty = 0
    smg = 1
    assault = 2
    shotgun = 3
    sniper = 4
    ALL_TYPES = (empty,
     smg,
     assault,
     shotgun,
     sniper)


DB = Dummy()
DB.header = Dummy()
DB.header.client = Dummy()
DB.header.client.place = 'right'
DB.header.condition = []
DB.header.count = []
DB.header.event = []
DB.header.group = 'heroic.coach'
DB.header.markers = Dummy()
DB.header.markers.group = 'heroic'
DB.header.modify = []
DB.header.operation = []
DB.header.send = []
DB.header.server = Dummy()
DB.header.server.active = true
DB.header.server.scope = []
DB.header.server.scope.insert(0, None)
DB.header.server.scope[0] = 'player'
DB.header.type = 'achievement'
DB.include = Dummy()
DB.include.condition = []
DB.include.condition.insert(0, None)
DB.include.condition[0] = Dummy()
DB.include.condition[0].and_ = []
DB.include.condition[0].contains = []
DB.include.condition[0].equal = []
DB.include.condition[0].gt = []
DB.include.condition[0].gte = []
DB.include.condition[0].gte.insert(0, None)
DB.include.condition[0].gte[0] = Dummy()
DB.include.condition[0].gte[0].context = []
DB.include.condition[0].gte[0].context.insert(0, None)
DB.include.condition[0].gte[0].context[0] = 'player.plane.level'
DB.include.condition[0].gte[0].value_ = []
DB.include.condition[0].gte[0].value_.insert(0, None)
DB.include.condition[0].gte[0].value_[0] = '4'
DB.include.condition[0].id = []
DB.include.condition[0].in_ = []
DB.include.condition[0].lt = []
DB.include.condition[0].lte = []
DB.include.condition[0].not_ = []
DB.include.condition[0].or_ = []
DB.include.condition.insert(1, None)
DB.include.condition[1] = Dummy()
DB.include.condition[1].and_ = []
DB.include.condition[1].contains = []
DB.include.condition[1].equal = []
DB.include.condition[1].gt = []
DB.include.condition[1].gte = []
DB.include.condition[1].id = []
DB.include.condition[1].in_ = []
DB.include.condition[1].lt = []
DB.include.condition[1].lte = []
DB.include.condition[1].not_ = []
DB.include.condition[1].or_ = []
DB.include.condition[1].or_.insert(0, None)
DB.include.condition[1].or_[0] = Dummy()
DB.include.condition[1].or_[0].and_ = []
DB.include.condition[1].or_[0].and_.insert(0, None)
DB.include.condition[1].or_[0].and_[0] = Dummy()
DB.include.condition[1].or_[0].and_[0].and_ = []
DB.include.condition[1].or_[0].and_[0].contains = []
DB.include.condition[1].or_[0].and_[0].equal = []
DB.include.condition[1].or_[0].and_[0].equal.insert(0, None)
DB.include.condition[1].or_[0].and_[0].equal[0] = Dummy()
DB.include.condition[1].or_[0].and_[0].equal[0].context = []
DB.include.condition[1].or_[0].and_[0].equal[0].context.insert(0, None)
DB.include.condition[1].or_[0].and_[0].equal[0].context[0] = 'arena.type'
DB.include.condition[1].or_[0].and_[0].equal[0].value_ = []
DB.include.condition[1].or_[0].and_[0].equal[0].value_.insert(0, None)
DB.include.condition[1].or_[0].and_[0].equal[0].value_[0] = 'normal'
DB.include.condition[1].or_[0].and_[0].equal.insert(1, None)
DB.include.condition[1].or_[0].and_[0].equal[1] = Dummy()
DB.include.condition[1].or_[0].and_[0].equal[1].context = []
DB.include.condition[1].or_[0].and_[0].equal[1].context.insert(0, None)
DB.include.condition[1].or_[0].and_[0].equal[1].context[0] = 'arena.source'
DB.include.condition[1].or_[0].and_[0].equal[1].value_ = []
DB.include.condition[1].or_[0].and_[0].equal[1].value_.insert(0, None)
DB.include.condition[1].or_[0].and_[0].equal[1].value_[0] = 'player'
DB.include.condition[1].or_[0].and_[0].gt = []
DB.include.condition[1].or_[0].and_[0].gte = []
DB.include.condition[1].or_[0].and_[0].id = []
DB.include.condition[1].or_[0].and_[0].in_ = []
DB.include.condition[1].or_[0].and_[0].lt = []
DB.include.condition[1].or_[0].and_[0].lte = []
DB.include.condition[1].or_[0].and_[0].not_ = []
DB.include.condition[1].or_[0].and_[0].or_ = []
DB.include.condition[1].or_[0].and_.insert(1, None)
DB.include.condition[1].or_[0].and_[1] = Dummy()
DB.include.condition[1].or_[0].and_[1].and_ = []
DB.include.condition[1].or_[0].and_[1].contains = []
DB.include.condition[1].or_[0].and_[1].equal = []
DB.include.condition[1].or_[0].and_[1].equal.insert(0, None)
DB.include.condition[1].or_[0].and_[1].equal[0] = Dummy()
DB.include.condition[1].or_[0].and_[1].equal[0].context = []
DB.include.condition[1].or_[0].and_[1].equal[0].context.insert(0, None)
DB.include.condition[1].or_[0].and_[1].equal[0].context[0] = 'self.event.type'
DB.include.condition[1].or_[0].and_[1].equal[0].value_ = []
DB.include.condition[1].or_[0].and_[1].equal[0].value_.insert(0, None)
DB.include.condition[1].or_[0].and_[1].equal[0].value_[0] = 'hangar'
DB.include.condition[1].or_[0].and_[1].gt = []
DB.include.condition[1].or_[0].and_[1].gte = []
DB.include.condition[1].or_[0].and_[1].id = []
DB.include.condition[1].or_[0].and_[1].in_ = []
DB.include.condition[1].or_[0].and_[1].lt = []
DB.include.condition[1].or_[0].and_[1].lte = []
DB.include.condition[1].or_[0].and_[1].not_ = []
DB.include.condition[1].or_[0].and_[1].or_ = []
DB.include.condition[1].or_[0].contains = []
DB.include.condition[1].or_[0].equal = []
DB.include.condition[1].or_[0].gt = []
DB.include.condition[1].or_[0].gte = []
DB.include.condition[1].or_[0].id = []
DB.include.condition[1].or_[0].in_ = []
DB.include.condition[1].or_[0].lt = []
DB.include.condition[1].or_[0].lte = []
DB.include.condition[1].or_[0].not_ = []
DB.include.condition[1].or_[0].or_ = []
DB.include.count = []
DB.include.event = []
DB.include.metadata = Dummy()
DB.include.metadata.doneCount = true
DB.include.metadata.event = []
DB.include.metadata.firstDoneTime = true
DB.include.metadata.lastDoneTime = true
DB.include.modify = []
DB.include.operation = []
DB.include.send = []
DB.subscriber = []
DB.subscriber.insert(0, None)
DB.subscriber[0] = Dummy()
DB.subscriber[0].condition = []
DB.subscriber[0].count = []
DB.subscriber[0].event = []
DB.subscriber[0].event.insert(0, None)
DB.subscriber[0].event[0] = Dummy()
DB.subscriber[0].event[0].condition = []
DB.subscriber[0].event[0].context = 'player'
DB.subscriber[0].event[0].count = []
DB.subscriber[0].event[0].name = 'finish'
DB.subscriber[0].event[0].operation = []
DB.subscriber[0].event[0].operation.insert(0, None)
DB.subscriber[0].event[0].operation[0] = Dummy()
DB.subscriber[0].event[0].operation[0].event = []
DB.subscriber[0].event[0].operation[0].id = []
DB.subscriber[0].event[0].operation[0].id.insert(0, None)
DB.subscriber[0].event[0].operation[0].id[0] = Dummy()
DB.subscriber[0].event[0].operation[0].id[0].group = 'heroic.coach'
DB.subscriber[0].event[0].operation[0].id[0].name = '*'
DB.subscriber[0].event[0].operation[0].id[0].type = 'achievement'
DB.subscriber[0].event[0].operation[0].rollback = true
DB.subscriber[0].event[0].operation[0].set = Dummy()
DB.subscriber[0].event[0].operation[0].set.completed = false
DB.subscriber[0].event[0].type = 'battle'
DB.subscriber[0].event.insert(1, None)
DB.subscriber[0].event[1] = Dummy()
DB.subscriber[0].event[1].condition = []
DB.subscriber[0].event[1].context = 'player'
DB.subscriber[0].event[1].count = []
DB.subscriber[0].event[1].name = 'day.changed'
DB.subscriber[0].event[1].operation = []
DB.subscriber[0].event[1].operation.insert(0, None)
DB.subscriber[0].event[1].operation[0] = Dummy()
DB.subscriber[0].event[1].operation[0].event = []
DB.subscriber[0].event[1].operation[0].id = []
DB.subscriber[0].event[1].operation[0].id.insert(0, None)
DB.subscriber[0].event[1].operation[0].id[0] = Dummy()
DB.subscriber[0].event[1].operation[0].id[0].group = 'heroic.coach'
DB.subscriber[0].event[1].operation[0].id[0].name = '*'
DB.subscriber[0].event[1].operation[0].id[0].type = 'achievement'
DB.subscriber[0].event[1].operation[0].processors = Dummy()
DB.subscriber[0].event[1].operation[0].processors.count = []
DB.subscriber[0].event[1].operation[0].processors.event = []
DB.subscriber[0].event[1].operation[0].processors.transaction = []
DB.subscriber[0].event[1].operation[0].processors.transaction.insert(0, None)
DB.subscriber[0].event[1].operation[0].processors.transaction[0] = 0
DB.subscriber[0].event[1].operation[0].reset_ = true
DB.subscriber[0].event[1].type = 'hangar'
DB.subscriber[0].group = 'heroic.coach'
DB.subscriber[0].modify = []
DB.subscriber[0].name = 'reset'
DB.subscriber[0].operation = []
DB.subscriber[0].send = []
DB.subscriber[0].server = Dummy()
DB.subscriber[0].server.overwrite = true
DB.subscriber[0].server.repeat = true
DB.subscriber[0].server.scope = []
DB.subscriber[0].type = 'achievement.reset'
DB.subscriber.insert(1, None)
DB.subscriber[1] = Dummy()
DB.subscriber[1].client = Dummy()
DB.subscriber[1].client.description = Dummy()
DB.subscriber[1].client.description.locale = 'MEDAL_DESCRIPTION_TEAMWORK_GURU'
DB.subscriber[1].client.icon = Dummy()
DB.subscriber[1].client.icon.big = 'icons/awards/achievementsInfo/acServiceTeamworkGuru.dds'
DB.subscriber[1].client.icon.faded = 'icons/awards/achievements/acServiceTeamworkGuru_Outline.dds'
DB.subscriber[1].client.icon.small = 'icons/awards/achievements/acServiceTeamworkGuru.dds'
DB.subscriber[1].client.level = Dummy()
DB.subscriber[1].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[1].client.multiple = true
DB.subscriber[1].client.name = Dummy()
DB.subscriber[1].client.name.locale = 'MEDAL_NAME_TEAMWORK_GURU'
DB.subscriber[1].client.order = 1
DB.subscriber[1].client.page = 0
DB.subscriber[1].condition = []
DB.subscriber[1].count = []
DB.subscriber[1].count.insert(0, None)
DB.subscriber[1].count[0] = Dummy()
DB.subscriber[1].count[0].value_ = 1
DB.subscriber[1].event = []
DB.subscriber[1].event.insert(0, None)
DB.subscriber[1].event[0] = Dummy()
DB.subscriber[1].event[0].condition = []
DB.subscriber[1].event[0].context = 'rank'
DB.subscriber[1].event[0].count = []
DB.subscriber[1].event[0].name = 'rank.1.for.fighter.completed'
DB.subscriber[1].event[0].operation = []
DB.subscriber[1].event[0].type = 'coach'
DB.subscriber[1].event.insert(1, None)
DB.subscriber[1].event[1] = Dummy()
DB.subscriber[1].event[1].condition = []
DB.subscriber[1].event[1].context = 'rank'
DB.subscriber[1].event[1].count = []
DB.subscriber[1].event[1].name = 'rank.1.for.navy.completed'
DB.subscriber[1].event[1].operation = []
DB.subscriber[1].event[1].type = 'coach'
DB.subscriber[1].event.insert(2, None)
DB.subscriber[1].event[2] = Dummy()
DB.subscriber[1].event[2].condition = []
DB.subscriber[1].event[2].context = 'rank'
DB.subscriber[1].event[2].count = []
DB.subscriber[1].event[2].name = 'rank.1.for.heavy.completed'
DB.subscriber[1].event[2].operation = []
DB.subscriber[1].event[2].type = 'coach'
DB.subscriber[1].event.insert(3, None)
DB.subscriber[1].event[3] = Dummy()
DB.subscriber[1].event[3].condition = []
DB.subscriber[1].event[3].context = 'rank'
DB.subscriber[1].event[3].count = []
DB.subscriber[1].event[3].name = 'rank.1.for.bomber.completed'
DB.subscriber[1].event[3].operation = []
DB.subscriber[1].event[3].type = 'coach'
DB.subscriber[1].event.insert(4, None)
DB.subscriber[1].event[4] = Dummy()
DB.subscriber[1].event[4].condition = []
DB.subscriber[1].event[4].context = 'rank'
DB.subscriber[1].event[4].count = []
DB.subscriber[1].event[4].name = 'rank.1.for.assault.completed'
DB.subscriber[1].event[4].operation = []
DB.subscriber[1].event[4].type = 'coach'
DB.subscriber[1].modify = []
DB.subscriber[1].name = 'teamworkguru'
DB.subscriber[1].operation = []
DB.subscriber[1].send = []
DB.subscriber.insert(2, None)
DB.subscriber[2] = Dummy()
DB.subscriber[2].client = Dummy()
DB.subscriber[2].client.description = Dummy()
DB.subscriber[2].client.description.locale = 'MEDAL_DESCRIPTION_FIGHTER_INTERCEPTOR'
DB.subscriber[2].client.icon = Dummy()
DB.subscriber[2].client.icon.big = 'icons/awards/achievementsInfo/acServiceFighterInterceptor.dds'
DB.subscriber[2].client.icon.faded = 'icons/awards/achievements/acServiceFighterInterceptor_Outline.dds'
DB.subscriber[2].client.icon.small = 'icons/awards/achievements/acServiceFighterInterceptor.dds'
DB.subscriber[2].client.level = Dummy()
DB.subscriber[2].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[2].client.multiple = true
DB.subscriber[2].client.name = Dummy()
DB.subscriber[2].client.name.locale = 'MEDAL_NAME_FIGHTER_INTERCEPTOR'
DB.subscriber[2].client.order = 2
DB.subscriber[2].client.page = 0
DB.subscriber[2].condition = []
DB.subscriber[2].count = []
DB.subscriber[2].count.insert(0, None)
DB.subscriber[2].count[0] = Dummy()
DB.subscriber[2].count[0].value_ = 1
DB.subscriber[2].event = []
DB.subscriber[2].event.insert(0, None)
DB.subscriber[2].event[0] = Dummy()
DB.subscriber[2].event[0].condition = []
DB.subscriber[2].event[0].context = 'objective'
DB.subscriber[2].event[0].count = []
DB.subscriber[2].event[0].name = 'destroyPlanes.for.fighter.completed'
DB.subscriber[2].event[0].operation = []
DB.subscriber[2].event[0].type = 'coach'
DB.subscriber[2].event.insert(1, None)
DB.subscriber[2].event[1] = Dummy()
DB.subscriber[2].event[1].condition = []
DB.subscriber[2].event[1].context = 'objective'
DB.subscriber[2].event[1].count = []
DB.subscriber[2].event[1].name = 'destroyPlanes.for.heavy.fighter.completed'
DB.subscriber[2].event[1].operation = []
DB.subscriber[2].event[1].type = 'coach'
DB.subscriber[2].modify = []
DB.subscriber[2].name = 'fighterinterceptor'
DB.subscriber[2].operation = []
DB.subscriber[2].send = []
DB.subscriber.insert(3, None)
DB.subscriber[3] = Dummy()
DB.subscriber[3].client = Dummy()
DB.subscriber[3].client.description = Dummy()
DB.subscriber[3].client.description.locale = 'MEDAL_DESCRIPTION_FIGHTER_DEFENDER'
DB.subscriber[3].client.icon = Dummy()
DB.subscriber[3].client.icon.big = 'icons/awards/achievementsInfo/acServiceFighterDefender.dds'
DB.subscriber[3].client.icon.faded = 'icons/awards/achievements/acServiceFighterDefender_Outline.dds'
DB.subscriber[3].client.icon.small = 'icons/awards/achievements/acServiceFighterDefender.dds'
DB.subscriber[3].client.level = Dummy()
DB.subscriber[3].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[3].client.multiple = true
DB.subscriber[3].client.name = Dummy()
DB.subscriber[3].client.name.locale = 'MEDAL_NAME_FIGHTER_DEFENDER'
DB.subscriber[3].client.order = 3
DB.subscriber[3].client.page = 0
DB.subscriber[3].condition = []
DB.subscriber[3].count = []
DB.subscriber[3].count.insert(0, None)
DB.subscriber[3].count[0] = Dummy()
DB.subscriber[3].count[0].value_ = 1
DB.subscriber[3].event = []
DB.subscriber[3].event.insert(0, None)
DB.subscriber[3].event[0] = Dummy()
DB.subscriber[3].event[0].condition = []
DB.subscriber[3].event[0].context = 'objective'
DB.subscriber[3].event[0].count = []
DB.subscriber[3].event[0].name = 'defenceSectors.for.fighter.completed'
DB.subscriber[3].event[0].operation = []
DB.subscriber[3].event[0].type = 'coach'
DB.subscriber[3].event.insert(1, None)
DB.subscriber[3].event[1] = Dummy()
DB.subscriber[3].event[1].condition = []
DB.subscriber[3].event[1].context = 'objective'
DB.subscriber[3].event[1].count = []
DB.subscriber[3].event[1].name = 'defenceSectors.for.navy.completed'
DB.subscriber[3].event[1].operation = []
DB.subscriber[3].event[1].type = 'coach'
DB.subscriber[3].modify = []
DB.subscriber[3].name = 'fighterdefender'
DB.subscriber[3].operation = []
DB.subscriber[3].send = []
DB.subscriber.insert(4, None)
DB.subscriber[4] = Dummy()
DB.subscriber[4].client = Dummy()
DB.subscriber[4].client.description = Dummy()
DB.subscriber[4].client.description.locale = 'MEDAL_DESCRIPTION_FIGHTER_DOMINATOR'
DB.subscriber[4].client.icon = Dummy()
DB.subscriber[4].client.icon.big = 'icons/awards/achievementsInfo/acServiceFighterDominator.dds'
DB.subscriber[4].client.icon.faded = 'icons/awards/achievements/acServiceFighterDominator_Outline.dds'
DB.subscriber[4].client.icon.small = 'icons/awards/achievements/acServiceFighterDominator.dds'
DB.subscriber[4].client.level = Dummy()
DB.subscriber[4].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[4].client.multiple = true
DB.subscriber[4].client.name = Dummy()
DB.subscriber[4].client.name.locale = 'MEDAL_NAME_FIGHTER_DOMINATOR'
DB.subscriber[4].client.order = 4
DB.subscriber[4].client.page = 0
DB.subscriber[4].condition = []
DB.subscriber[4].count = []
DB.subscriber[4].event = []
DB.subscriber[4].event.insert(0, None)
DB.subscriber[4].event[0] = Dummy()
DB.subscriber[4].event[0].condition = []
DB.subscriber[4].event[0].context = 'objective'
DB.subscriber[4].event[0].count = []
DB.subscriber[4].event[0].count.insert(0, None)
DB.subscriber[4].event[0].count[0] = Dummy()
DB.subscriber[4].event[0].count[0].value_ = 1
DB.subscriber[4].event[0].name = 'dogfightForSectors.for.fighter.completed'
DB.subscriber[4].event[0].operation = []
DB.subscriber[4].event[0].type = 'coach'
DB.subscriber[4].modify = []
DB.subscriber[4].name = 'fighterdominator'
DB.subscriber[4].operation = []
DB.subscriber[4].send = []
DB.subscriber.insert(5, None)
DB.subscriber[5] = Dummy()
DB.subscriber[5].client = Dummy()
DB.subscriber[5].client.description = Dummy()
DB.subscriber[5].client.description.locale = 'MEDAL_DESCRIPTION_FIGHTER_OF_ALL_LIFE'
DB.subscriber[5].client.icon = Dummy()
DB.subscriber[5].client.icon.big = 'icons/awards/achievementsInfo/acServiceFighterOfAllLife.dds'
DB.subscriber[5].client.icon.faded = 'icons/awards/achievements/acServiceFighterOfAllLife_Outline.dds'
DB.subscriber[5].client.icon.small = 'icons/awards/achievements/acServiceFighterOfAllLife.dds'
DB.subscriber[5].client.level = Dummy()
DB.subscriber[5].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[5].client.multiple = true
DB.subscriber[5].client.name = Dummy()
DB.subscriber[5].client.name.locale = 'MEDAL_NAME_FIGHTER_OF_ALL_LIFE'
DB.subscriber[5].client.order = 5
DB.subscriber[5].client.page = 0
DB.subscriber[5].condition = []
DB.subscriber[5].count = []
DB.subscriber[5].count.insert(0, None)
DB.subscriber[5].count[0] = Dummy()
DB.subscriber[5].count[0].value_ = 1
DB.subscriber[5].event = []
DB.subscriber[5].event.insert(0, None)
DB.subscriber[5].event[0] = Dummy()
DB.subscriber[5].event[0].condition = []
DB.subscriber[5].event[0].context = 'objective'
DB.subscriber[5].event[0].count = []
DB.subscriber[5].event[0].name = 'attackSectors.for.heavy.fighter.completed'
DB.subscriber[5].event[0].operation = []
DB.subscriber[5].event[0].type = 'coach'
DB.subscriber[5].event.insert(1, None)
DB.subscriber[5].event[1] = Dummy()
DB.subscriber[5].event[1].condition = []
DB.subscriber[5].event[1].context = 'objective'
DB.subscriber[5].event[1].count = []
DB.subscriber[5].event[1].name = 'attackSectors.for.navy.completed'
DB.subscriber[5].event[1].operation = []
DB.subscriber[5].event[1].type = 'coach'
DB.subscriber[5].modify = []
DB.subscriber[5].name = 'fighterofalllife'
DB.subscriber[5].operation = []
DB.subscriber[5].send = []
DB.subscriber.insert(6, None)
DB.subscriber[6] = Dummy()
DB.subscriber[6].client = Dummy()
DB.subscriber[6].client.description = Dummy()
DB.subscriber[6].client.description.locale = 'MEDAL_DESCRIPTION_CONTROLLER'
DB.subscriber[6].client.icon = Dummy()
DB.subscriber[6].client.icon.big = 'icons/awards/achievementsInfo/acServiceController.dds'
DB.subscriber[6].client.icon.faded = 'icons/awards/achievements/acServiceController_Outline.dds'
DB.subscriber[6].client.icon.small = 'icons/awards/achievements/acServiceController.dds'
DB.subscriber[6].client.level = Dummy()
DB.subscriber[6].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[6].client.multiple = true
DB.subscriber[6].client.name = Dummy()
DB.subscriber[6].client.name.locale = 'MEDAL_NAME_CONTROLLER'
DB.subscriber[6].client.order = 6
DB.subscriber[6].client.page = 0
DB.subscriber[6].condition = []
DB.subscriber[6].count = []
DB.subscriber[6].count.insert(0, None)
DB.subscriber[6].count[0] = Dummy()
DB.subscriber[6].count[0].value_ = 1
DB.subscriber[6].event = []
DB.subscriber[6].event.insert(0, None)
DB.subscriber[6].event[0] = Dummy()
DB.subscriber[6].event[0].condition = []
DB.subscriber[6].event[0].context = 'objective'
DB.subscriber[6].event[0].count = []
DB.subscriber[6].event[0].name = 'captureSectors.for.heavy.fighter.completed'
DB.subscriber[6].event[0].operation = []
DB.subscriber[6].event[0].type = 'coach'
DB.subscriber[6].event.insert(1, None)
DB.subscriber[6].event[1] = Dummy()
DB.subscriber[6].event[1].condition = []
DB.subscriber[6].event[1].context = 'objective'
DB.subscriber[6].event[1].count = []
DB.subscriber[6].event[1].name = 'captureSectors.for.navy.completed'
DB.subscriber[6].event[1].operation = []
DB.subscriber[6].event[1].type = 'coach'
DB.subscriber[6].event.insert(2, None)
DB.subscriber[6].event[2] = Dummy()
DB.subscriber[6].event[2].condition = []
DB.subscriber[6].event[2].context = 'objective'
DB.subscriber[6].event[2].count = []
DB.subscriber[6].event[2].name = 'captureSectors.for.assault.completed'
DB.subscriber[6].event[2].operation = []
DB.subscriber[6].event[2].type = 'coach'
DB.subscriber[6].event.insert(3, None)
DB.subscriber[6].event[3] = Dummy()
DB.subscriber[6].event[3].condition = []
DB.subscriber[6].event[3].context = 'objective'
DB.subscriber[6].event[3].count = []
DB.subscriber[6].event[3].name = 'captureSectors.for.bomber.completed'
DB.subscriber[6].event[3].operation = []
DB.subscriber[6].event[3].type = 'coach'
DB.subscriber[6].modify = []
DB.subscriber[6].name = 'controller'
DB.subscriber[6].operation = []
DB.subscriber[6].send = []
DB.subscriber.insert(7, None)
DB.subscriber[7] = Dummy()
DB.subscriber[7].client = Dummy()
DB.subscriber[7].client.description = Dummy()
DB.subscriber[7].client.description.locale = 'MEDAL_DESCRIPTION_EXTERMINATOR'
DB.subscriber[7].client.icon = Dummy()
DB.subscriber[7].client.icon.big = 'icons/awards/achievementsInfo/acServiceExterminator.dds'
DB.subscriber[7].client.icon.faded = 'icons/awards/achievements/acServiceExterminator_Outline.dds'
DB.subscriber[7].client.icon.small = 'icons/awards/achievements/acServiceExterminator.dds'
DB.subscriber[7].client.level = Dummy()
DB.subscriber[7].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[7].client.multiple = true
DB.subscriber[7].client.name = Dummy()
DB.subscriber[7].client.name.locale = 'MEDAL_NAME_EXTERMINATOR'
DB.subscriber[7].client.order = 7
DB.subscriber[7].client.page = 0
DB.subscriber[7].condition = []
DB.subscriber[7].count = []
DB.subscriber[7].count.insert(0, None)
DB.subscriber[7].count[0] = Dummy()
DB.subscriber[7].count[0].value_ = 1
DB.subscriber[7].event = []
DB.subscriber[7].event.insert(0, None)
DB.subscriber[7].event[0] = Dummy()
DB.subscriber[7].event[0].condition = []
DB.subscriber[7].event[0].context = 'objective'
DB.subscriber[7].event[0].count = []
DB.subscriber[7].event[0].name = 'attackGroundObjects.for.assault.completed'
DB.subscriber[7].event[0].operation = []
DB.subscriber[7].event[0].type = 'coach'
DB.subscriber[7].event.insert(1, None)
DB.subscriber[7].event[1] = Dummy()
DB.subscriber[7].event[1].condition = []
DB.subscriber[7].event[1].context = 'objective'
DB.subscriber[7].event[1].count = []
DB.subscriber[7].event[1].name = 'attackGroundObjects.for.bomber.completed'
DB.subscriber[7].event[1].operation = []
DB.subscriber[7].event[1].type = 'coach'
DB.subscriber[7].modify = []
DB.subscriber[7].name = 'exterminator'
DB.subscriber[7].operation = []
DB.subscriber[7].send = []
DB.subscriber.insert(8, None)
DB.subscriber[8] = Dummy()
DB.subscriber[8].client = Dummy()
DB.subscriber[8].client.description = Dummy()
DB.subscriber[8].client.description.locale = 'MEDAL_DESCRIPTION_DESTROYER'
DB.subscriber[8].client.icon = Dummy()
DB.subscriber[8].client.icon.big = 'icons/awards/achievementsInfo/acServiceDestroyer.dds'
DB.subscriber[8].client.icon.faded = 'icons/awards/achievements/acServiceDestroyer_Outline.dds'
DB.subscriber[8].client.icon.small = 'icons/awards/achievements/acServiceDestroyer.dds'
DB.subscriber[8].client.level = Dummy()
DB.subscriber[8].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[8].client.multiple = true
DB.subscriber[8].client.name = Dummy()
DB.subscriber[8].client.name.locale = 'MEDAL_NAME_DESTROYER'
DB.subscriber[8].client.order = 8
DB.subscriber[8].client.page = 0
DB.subscriber[8].condition = []
DB.subscriber[8].count = []
DB.subscriber[8].count.insert(0, None)
DB.subscriber[8].count[0] = Dummy()
DB.subscriber[8].count[0].value_ = 1
DB.subscriber[8].event = []
DB.subscriber[8].event.insert(0, None)
DB.subscriber[8].event[0] = Dummy()
DB.subscriber[8].event[0].condition = []
DB.subscriber[8].event[0].context = 'objective'
DB.subscriber[8].event[0].count = []
DB.subscriber[8].event[0].name = 'destroyObjectParts.for.assault.completed'
DB.subscriber[8].event[0].operation = []
DB.subscriber[8].event[0].type = 'coach'
DB.subscriber[8].event.insert(1, None)
DB.subscriber[8].event[1] = Dummy()
DB.subscriber[8].event[1].condition = []
DB.subscriber[8].event[1].context = 'objective'
DB.subscriber[8].event[1].count = []
DB.subscriber[8].event[1].name = 'destroyObjectParts.for.bomber.completed'
DB.subscriber[8].event[1].operation = []
DB.subscriber[8].event[1].type = 'coach'
DB.subscriber[8].modify = []
DB.subscriber[8].name = 'destroyer'
DB.subscriber[8].operation = []
DB.subscriber[8].send = []
DB.subscriber[0].id = 391156213
DB.subscriber[1].id = 1139684885
DB.subscriber[2].id = 420116408
DB.subscriber[3].id = -1320718250
DB.subscriber[4].id = 2129354326
DB.subscriber[5].id = 609147450
DB.subscriber[6].id = 1445898632
DB.subscriber[7].id = 376865783
DB.subscriber[8].id = -628072840
DB.subscriber[0].eventIds = (761754430, 35456563)
DB.subscriber[1].eventIds = (1505878768, -1458310531, 1005655320, 1640610640, -1559939534)
DB.subscriber[2].eventIds = (-2138774230, -251903565)
DB.subscriber[3].eventIds = (877979666, 623333830)
DB.subscriber[4].eventIds = (-554780299,)
DB.subscriber[5].eventIds = (-1382442359, -1492408551)
DB.subscriber[6].eventIds = (-1293764618, -953903409, -588048498, -35275748)
DB.subscriber[7].eventIds = (-1633037042, 364859445)
DB.subscriber[8].eventIds = (325781352, -547306710)
mapping = {'db': DB,
 'indexes': {'subscriber': {'id': {391156213: (DB.subscriber[0],),
                                   1139684885: (DB.subscriber[1],),
                                   420116408: (DB.subscriber[2],),
                                   -1320718250: (DB.subscriber[3],),
                                   2129354326: (DB.subscriber[4],),
                                   609147450: (DB.subscriber[5],),
                                   1445898632: (DB.subscriber[6],),
                                   376865783: (DB.subscriber[7],),
                                   -628072840: (DB.subscriber[8],)},
                            'name': {'reset': (DB.subscriber[0],),
                                     'teamworkguru': (DB.subscriber[1],),
                                     'fighterinterceptor': (DB.subscriber[2],),
                                     'fighterdefender': (DB.subscriber[3],),
                                     'fighterdominator': (DB.subscriber[4],),
                                     'fighterofalllife': (DB.subscriber[5],),
                                     'controller': (DB.subscriber[6],),
                                     'exterminator': (DB.subscriber[7],),
                                     'destroyer': (DB.subscriber[8],)},
                            'type': {'achievement.reset': (DB.subscriber[0],),
                                     'achievement': (DB.subscriber[1],
                                                     DB.subscriber[2],
                                                     DB.subscriber[3],
                                                     DB.subscriber[4],
                                                     DB.subscriber[5],
                                                     DB.subscriber[6],
                                                     DB.subscriber[7],
                                                     DB.subscriber[8])},
                            'group': {'heroic.coach': (DB.subscriber[0],
                                                       DB.subscriber[1],
                                                       DB.subscriber[2],
                                                       DB.subscriber[3],
                                                       DB.subscriber[4],
                                                       DB.subscriber[5],
                                                       DB.subscriber[6],
                                                       DB.subscriber[7],
                                                       DB.subscriber[8])},
                            'eventIds': {(761754430, 35456563): (DB.subscriber[0],),
                                         (1505878768, -1458310531, 1005655320, 1640610640, -1559939534): (DB.subscriber[1],),
                                         (-2138774230, -251903565): (DB.subscriber[2],),
                                         (877979666, 623333830): (DB.subscriber[3],),
                                         (-554780299,): (DB.subscriber[4],),
                                         (-1382442359, -1492408551): (DB.subscriber[5],),
                                         (-1293764618, -953903409, -588048498, -35275748): (DB.subscriber[6],),
                                         (-1633037042, 364859445): (DB.subscriber[7],),
                                         (325781352, -547306710): (DB.subscriber[8],)},
                            'parent': {}}},
 'nested': ('subscriber.nested',),
 'type': {'default': 'subscriber',
          'all': ['subscriber']}}