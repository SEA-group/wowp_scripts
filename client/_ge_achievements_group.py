# Embedded file name: scripts/client/_ge_achievements_group.py
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
DB.header.activity = []
DB.header.client = Dummy()
DB.header.client.place = 'right'
DB.header.condition = []
DB.header.count = []
DB.header.event = []
DB.header.group = 'group'
DB.header.markers = Dummy()
DB.header.markers.group = 'group'
DB.header.modify = []
DB.header.operation = []
DB.header.send = []
DB.header.server = Dummy()
DB.header.server.active = true
DB.header.server.scope = []
DB.header.server.scope.insert(0, None)
DB.header.server.scope[0] = 'squad'
DB.header.type = 'achievement'
DB.include = Dummy()
DB.include.activity = []
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
DB.include.condition[1].or_[0].and_[0].equal.insert(2, None)
DB.include.condition[1].or_[0].and_[0].equal[2] = Dummy()
DB.include.condition[1].or_[0].and_[0].equal[2].context = []
DB.include.condition[1].or_[0].and_[0].equal[2].context.insert(0, None)
DB.include.condition[1].or_[0].and_[0].equal[2].context[0] = 'player.squad.active'
DB.include.condition[1].or_[0].and_[0].equal[2].value_ = []
DB.include.condition[1].or_[0].and_[0].equal[2].value_.insert(0, None)
DB.include.condition[1].or_[0].and_[0].equal[2].value_[0] = 'yes'
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
DB.subscriber[0].activity = []
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
DB.subscriber[0].event[0].operation[0].id[0].group = 'group'
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
DB.subscriber[0].event[1].operation[0].id[0].group = 'group'
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
DB.subscriber[0].group = 'group'
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
DB.subscriber[1].activity = []
DB.subscriber[1].client = Dummy()
DB.subscriber[1].client.description = Dummy()
DB.subscriber[1].client.description.locale = 'MEDAL_DESCRIPTION_MASTERS_OF_SKY'
DB.subscriber[1].client.icon = Dummy()
DB.subscriber[1].client.icon.big = 'icons/awards/achievementsInfo/acGroupMastersOfSky.dds'
DB.subscriber[1].client.icon.faded = 'icons/awards/achievements/acGroupMastersOfSky_Outline.dds'
DB.subscriber[1].client.icon.small = 'icons/awards/achievements/acGroupMastersOfSky.dds'
DB.subscriber[1].client.level = Dummy()
DB.subscriber[1].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[1].client.multiple = true
DB.subscriber[1].client.name = Dummy()
DB.subscriber[1].client.name.locale = 'MEDAL_NAME_MASTERS_OF_SKY'
DB.subscriber[1].client.order = 1
DB.subscriber[1].client.page = 0
DB.subscriber[1].condition = []
DB.subscriber[1].count = []
DB.subscriber[1].event = []
DB.subscriber[1].event.insert(0, None)
DB.subscriber[1].event[0] = Dummy()
DB.subscriber[1].event[0].condition = []
DB.subscriber[1].event[0].context = 'player'
DB.subscriber[1].event[0].count = []
DB.subscriber[1].event[0].count.insert(0, None)
DB.subscriber[1].event[0].count[0] = Dummy()
DB.subscriber[1].event[0].count[0].id = 0
DB.subscriber[1].event[0].count[0].value_ = 25
DB.subscriber[1].event[0].name = 'kill'
DB.subscriber[1].event[0].operation = []
DB.subscriber[1].event[0].type = 'battle'
DB.subscriber[1].event.insert(1, None)
DB.subscriber[1].event[1] = Dummy()
DB.subscriber[1].event[1].condition = []
DB.subscriber[1].event[1].context = 'player'
DB.subscriber[1].event[1].count = []
DB.subscriber[1].event[1].name = 'death'
DB.subscriber[1].event[1].operation = []
DB.subscriber[1].event[1].operation.insert(0, None)
DB.subscriber[1].event[1].operation[0] = Dummy()
DB.subscriber[1].event[1].operation[0].event = []
DB.subscriber[1].event[1].operation[0].id = []
DB.subscriber[1].event[1].operation[0].rollback = true
DB.subscriber[1].event[1].operation[0].self = true
DB.subscriber[1].event[1].type = 'battle'
DB.subscriber[1].modify = []
DB.subscriber[1].name = 'mastersofsky'
DB.subscriber[1].operation = []
DB.subscriber[1].send = []
DB.subscriber.insert(2, None)
DB.subscriber[2] = Dummy()
DB.subscriber[2].activity = []
DB.subscriber[2].client = Dummy()
DB.subscriber[2].client.description = Dummy()
DB.subscriber[2].client.description.locale = 'MEDAL_DESCRIPTION_PREDATORY_DUET'
DB.subscriber[2].client.icon = Dummy()
DB.subscriber[2].client.icon.big = 'icons/awards/achievementsInfo/acGroupPredatoryDuet.dds'
DB.subscriber[2].client.icon.faded = 'icons/awards/achievements/acGroupPredatoryDuet_Outline.dds'
DB.subscriber[2].client.icon.small = 'icons/awards/achievements/acGroupPredatoryDuet.dds'
DB.subscriber[2].client.level = Dummy()
DB.subscriber[2].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[2].client.multiple = true
DB.subscriber[2].client.name = Dummy()
DB.subscriber[2].client.name.locale = 'MEDAL_NAME_PREDATORY_DUET'
DB.subscriber[2].client.order = 2
DB.subscriber[2].client.page = 0
DB.subscriber[2].condition = []
DB.subscriber[2].count = []
DB.subscriber[2].event = []
DB.subscriber[2].event.insert(0, None)
DB.subscriber[2].event[0] = Dummy()
DB.subscriber[2].event[0].condition = []
DB.subscriber[2].event[0].context = 'player'
DB.subscriber[2].event[0].count = []
DB.subscriber[2].event[0].count.insert(0, None)
DB.subscriber[2].event[0].count[0] = Dummy()
DB.subscriber[2].event[0].count[0].id = 0
DB.subscriber[2].event[0].count[0].value_ = 15
DB.subscriber[2].event[0].name = 'kill'
DB.subscriber[2].event[0].operation = []
DB.subscriber[2].event[0].type = 'battle'
DB.subscriber[2].event.insert(1, None)
DB.subscriber[2].event[1] = Dummy()
DB.subscriber[2].event[1].condition = []
DB.subscriber[2].event[1].context = 'player'
DB.subscriber[2].event[1].count = []
DB.subscriber[2].event[1].count.insert(0, None)
DB.subscriber[2].event[1].count[0] = Dummy()
DB.subscriber[2].event[1].count[0].context = 'points.capture'
DB.subscriber[2].event[1].count[0].id = 1
DB.subscriber[2].event[1].count[0].value_ = 500
DB.subscriber[2].event[1].name = 'gain'
DB.subscriber[2].event[1].operation = []
DB.subscriber[2].event[1].type = 'battle'
DB.subscriber[2].event.insert(2, None)
DB.subscriber[2].event[2] = Dummy()
DB.subscriber[2].event[2].condition = []
DB.subscriber[2].event[2].context = 'player'
DB.subscriber[2].event[2].count = []
DB.subscriber[2].event[2].name = 'death'
DB.subscriber[2].event[2].operation = []
DB.subscriber[2].event[2].operation.insert(0, None)
DB.subscriber[2].event[2].operation[0] = Dummy()
DB.subscriber[2].event[2].operation[0].event = []
DB.subscriber[2].event[2].operation[0].id = []
DB.subscriber[2].event[2].operation[0].rollback = true
DB.subscriber[2].event[2].operation[0].self = true
DB.subscriber[2].event[2].type = 'battle'
DB.subscriber[2].modify = []
DB.subscriber[2].name = 'predatoryduet'
DB.subscriber[2].operation = []
DB.subscriber[2].send = []
DB.subscriber.insert(3, None)
DB.subscriber[3] = Dummy()
DB.subscriber[3].activity = []
DB.subscriber[3].client = Dummy()
DB.subscriber[3].client.description = Dummy()
DB.subscriber[3].client.description.locale = 'MEDAL_DESCRIPTION_END_OF_SPEAR'
DB.subscriber[3].client.icon = Dummy()
DB.subscriber[3].client.icon.big = 'icons/awards/achievementsInfo/acGroupEndOfSpear.dds'
DB.subscriber[3].client.icon.faded = 'icons/awards/achievements/acGroupEndOfSpear_Outline.dds'
DB.subscriber[3].client.icon.small = 'icons/awards/achievements/acGroupEndOfSpear.dds'
DB.subscriber[3].client.level = Dummy()
DB.subscriber[3].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[3].client.multiple = true
DB.subscriber[3].client.name = Dummy()
DB.subscriber[3].client.name.locale = 'MEDAL_NAME_END_OF_SPEAR'
DB.subscriber[3].client.order = 3
DB.subscriber[3].client.page = 0
DB.subscriber[3].condition = []
DB.subscriber[3].count = []
DB.subscriber[3].event = []
DB.subscriber[3].event.insert(0, None)
DB.subscriber[3].event[0] = Dummy()
DB.subscriber[3].event[0].condition = []
DB.subscriber[3].event[0].context = 'player'
DB.subscriber[3].event[0].count = []
DB.subscriber[3].event[0].count.insert(0, None)
DB.subscriber[3].event[0].count[0] = Dummy()
DB.subscriber[3].event[0].count[0].context = 'points.battle'
DB.subscriber[3].event[0].count[0].id = 0
DB.subscriber[3].event[0].count[0].value_ = 22000
DB.subscriber[3].event[0].name = 'gain'
DB.subscriber[3].event[0].operation = []
DB.subscriber[3].event[0].type = 'battle'
DB.subscriber[3].event.insert(1, None)
DB.subscriber[3].event[1] = Dummy()
DB.subscriber[3].event[1].condition = []
DB.subscriber[3].event[1].context = 'player'
DB.subscriber[3].event[1].count = []
DB.subscriber[3].event[1].name = 'death'
DB.subscriber[3].event[1].operation = []
DB.subscriber[3].event[1].operation.insert(0, None)
DB.subscriber[3].event[1].operation[0] = Dummy()
DB.subscriber[3].event[1].operation[0].event = []
DB.subscriber[3].event[1].operation[0].id = []
DB.subscriber[3].event[1].operation[0].rollback = true
DB.subscriber[3].event[1].operation[0].self = true
DB.subscriber[3].event[1].type = 'battle'
DB.subscriber[3].modify = []
DB.subscriber[3].name = 'endofspear'
DB.subscriber[3].operation = []
DB.subscriber[3].send = []
DB.subscriber.insert(4, None)
DB.subscriber[4] = Dummy()
DB.subscriber[4].activity = []
DB.subscriber[4].client = Dummy()
DB.subscriber[4].client.description = Dummy()
DB.subscriber[4].client.description.locale = 'MEDAL_DESCRIPTION_INDEPENDENT'
DB.subscriber[4].client.icon = Dummy()
DB.subscriber[4].client.icon.big = 'icons/awards/achievementsInfo/acGroupIndependent.dds'
DB.subscriber[4].client.icon.faded = 'icons/awards/achievements/acGroupIndependent_Outline.dds'
DB.subscriber[4].client.icon.small = 'icons/awards/achievements/acGroupIndependent.dds'
DB.subscriber[4].client.level = Dummy()
DB.subscriber[4].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[4].client.multiple = true
DB.subscriber[4].client.name = Dummy()
DB.subscriber[4].client.name.locale = 'MEDAL_NAME_INDEPENDENT'
DB.subscriber[4].client.order = 4
DB.subscriber[4].client.page = 0
DB.subscriber[4].condition = []
DB.subscriber[4].count = []
DB.subscriber[4].event = []
DB.subscriber[4].event.insert(0, None)
DB.subscriber[4].event[0] = Dummy()
DB.subscriber[4].event[0].condition = []
DB.subscriber[4].event[0].condition.insert(0, None)
DB.subscriber[4].event[0].condition[0] = Dummy()
DB.subscriber[4].event[0].condition[0].and_ = []
DB.subscriber[4].event[0].condition[0].and_.insert(0, None)
DB.subscriber[4].event[0].condition[0].and_[0] = Dummy()
DB.subscriber[4].event[0].condition[0].and_[0].and_ = []
DB.subscriber[4].event[0].condition[0].and_[0].contains = []
DB.subscriber[4].event[0].condition[0].and_[0].equal = []
DB.subscriber[4].event[0].condition[0].and_[0].equal.insert(0, None)
DB.subscriber[4].event[0].condition[0].and_[0].equal[0] = Dummy()
DB.subscriber[4].event[0].condition[0].and_[0].equal[0].context = []
DB.subscriber[4].event[0].condition[0].and_[0].equal[0].context.insert(0, None)
DB.subscriber[4].event[0].condition[0].and_[0].equal[0].context[0] = 'victim.type'
DB.subscriber[4].event[0].condition[0].and_[0].equal[0].value_ = []
DB.subscriber[4].event[0].condition[0].and_[0].equal[0].value_.insert(0, None)
DB.subscriber[4].event[0].condition[0].and_[0].equal[0].value_[0] = 'player'
DB.subscriber[4].event[0].condition[0].and_[0].gt = []
DB.subscriber[4].event[0].condition[0].and_[0].gte = []
DB.subscriber[4].event[0].condition[0].and_[0].id = []
DB.subscriber[4].event[0].condition[0].and_[0].in_ = []
DB.subscriber[4].event[0].condition[0].and_[0].lt = []
DB.subscriber[4].event[0].condition[0].and_[0].lte = []
DB.subscriber[4].event[0].condition[0].and_[0].not_ = []
DB.subscriber[4].event[0].condition[0].and_[0].or_ = []
DB.subscriber[4].event[0].condition[0].contains = []
DB.subscriber[4].event[0].condition[0].equal = []
DB.subscriber[4].event[0].condition[0].gt = []
DB.subscriber[4].event[0].condition[0].gte = []
DB.subscriber[4].event[0].condition[0].id = []
DB.subscriber[4].event[0].condition[0].in_ = []
DB.subscriber[4].event[0].condition[0].lt = []
DB.subscriber[4].event[0].condition[0].lte = []
DB.subscriber[4].event[0].condition[0].not_ = []
DB.subscriber[4].event[0].condition[0].or_ = []
DB.subscriber[4].event[0].context = 'player'
DB.subscriber[4].event[0].count = []
DB.subscriber[4].event[0].count.insert(0, None)
DB.subscriber[4].event[0].count[0] = Dummy()
DB.subscriber[4].event[0].count[0].id = 0
DB.subscriber[4].event[0].count[0].value_ = 6
DB.subscriber[4].event[0].name = 'kill'
DB.subscriber[4].event[0].operation = []
DB.subscriber[4].event[0].type = 'battle'
DB.subscriber[4].event.insert(1, None)
DB.subscriber[4].event[1] = Dummy()
DB.subscriber[4].event[1].condition = []
DB.subscriber[4].event[1].context = 'player'
DB.subscriber[4].event[1].count = []
DB.subscriber[4].event[1].count.insert(0, None)
DB.subscriber[4].event[1].count[0] = Dummy()
DB.subscriber[4].event[1].count[0].value_ = 1
DB.subscriber[4].event[1].name = 'stormfront'
DB.subscriber[4].event[1].operation = []
DB.subscriber[4].event[1].operation.insert(0, None)
DB.subscriber[4].event[1].operation[0] = Dummy()
DB.subscriber[4].event[1].operation[0].event = []
DB.subscriber[4].event[1].operation[0].id = []
DB.subscriber[4].event[1].operation[0].processors = Dummy()
DB.subscriber[4].event[1].operation[0].processors.count = []
DB.subscriber[4].event[1].operation[0].processors.count.insert(0, None)
DB.subscriber[4].event[1].operation[0].processors.count[0] = 0
DB.subscriber[4].event[1].operation[0].processors.event = []
DB.subscriber[4].event[1].operation[0].processors.transaction = []
DB.subscriber[4].event[1].operation[0].rollback = true
DB.subscriber[4].event[1].operation[0].self = true
DB.subscriber[4].event[1].type = 'battle'
DB.subscriber[4].event.insert(2, None)
DB.subscriber[4].event[2] = Dummy()
DB.subscriber[4].event[2].condition = []
DB.subscriber[4].event[2].context = 'player'
DB.subscriber[4].event[2].count = []
DB.subscriber[4].event[2].count.insert(0, None)
DB.subscriber[4].event[2].count[0] = Dummy()
DB.subscriber[4].event[2].count[0].value_ = 1
DB.subscriber[4].event[2].name = 'win'
DB.subscriber[4].event[2].operation = []
DB.subscriber[4].event[2].type = 'battle'
DB.subscriber[4].modify = []
DB.subscriber[4].name = 'independent'
DB.subscriber[4].operation = []
DB.subscriber[4].send = []
DB.subscriber.insert(5, None)
DB.subscriber[5] = Dummy()
DB.subscriber[5].activity = []
DB.subscriber[5].client = Dummy()
DB.subscriber[5].client.description = Dummy()
DB.subscriber[5].client.description.locale = 'MEDAL_DESCRIPTION_SKY_WOLVES'
DB.subscriber[5].client.icon = Dummy()
DB.subscriber[5].client.icon.big = 'icons/awards/achievementsInfo/acGroupSkyWolves.dds'
DB.subscriber[5].client.icon.faded = 'icons/awards/achievements/acGroupSkyWolves_Outline.dds'
DB.subscriber[5].client.icon.small = 'icons/awards/achievements/acGroupSkyWolves.dds'
DB.subscriber[5].client.level = Dummy()
DB.subscriber[5].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[5].client.multiple = true
DB.subscriber[5].client.name = Dummy()
DB.subscriber[5].client.name.locale = 'MEDAL_NAME_SKY_WOLVES'
DB.subscriber[5].client.order = 5
DB.subscriber[5].client.page = 0
DB.subscriber[5].condition = []
DB.subscriber[5].count = []
DB.subscriber[5].event = []
DB.subscriber[5].event.insert(0, None)
DB.subscriber[5].event[0] = Dummy()
DB.subscriber[5].event[0].condition = []
DB.subscriber[5].event[0].context = 'player'
DB.subscriber[5].event[0].count = []
DB.subscriber[5].event[0].count.insert(0, None)
DB.subscriber[5].event[0].count[0] = Dummy()
DB.subscriber[5].event[0].count[0].id = 0
DB.subscriber[5].event[0].count[0].value_ = 10
DB.subscriber[5].event[0].name = 'kill'
DB.subscriber[5].event[0].operation = []
DB.subscriber[5].event[0].type = 'battle'
DB.subscriber[5].event.insert(1, None)
DB.subscriber[5].event[1] = Dummy()
DB.subscriber[5].event[1].condition = []
DB.subscriber[5].event[1].condition.insert(0, None)
DB.subscriber[5].event[1].condition[0] = Dummy()
DB.subscriber[5].event[1].condition[0].and_ = []
DB.subscriber[5].event[1].condition[0].contains = []
DB.subscriber[5].event[1].condition[0].equal = []
DB.subscriber[5].event[1].condition[0].equal.insert(0, None)
DB.subscriber[5].event[1].condition[0].equal[0] = Dummy()
DB.subscriber[5].event[1].condition[0].equal[0].context = []
DB.subscriber[5].event[1].condition[0].equal[0].context.insert(0, None)
DB.subscriber[5].event[1].condition[0].equal[0].context[0] = 'victim.object'
DB.subscriber[5].event[1].condition[0].equal[0].value_ = []
DB.subscriber[5].event[1].condition[0].equal[0].value_.insert(0, None)
DB.subscriber[5].event[1].condition[0].equal[0].value_[0] = 'ground'
DB.subscriber[5].event[1].condition[0].gt = []
DB.subscriber[5].event[1].condition[0].gte = []
DB.subscriber[5].event[1].condition[0].id = []
DB.subscriber[5].event[1].condition[0].in_ = []
DB.subscriber[5].event[1].condition[0].lt = []
DB.subscriber[5].event[1].condition[0].lte = []
DB.subscriber[5].event[1].condition[0].not_ = []
DB.subscriber[5].event[1].condition[0].or_ = []
DB.subscriber[5].event[1].context = 'player'
DB.subscriber[5].event[1].count = []
DB.subscriber[5].event[1].count.insert(0, None)
DB.subscriber[5].event[1].count[0] = Dummy()
DB.subscriber[5].event[1].count[0].context = 'points.capture'
DB.subscriber[5].event[1].count[0].id = 1
DB.subscriber[5].event[1].count[0].value_ = 300
DB.subscriber[5].event[1].name = 'gain'
DB.subscriber[5].event[1].operation = []
DB.subscriber[5].event[1].type = 'battle'
DB.subscriber[5].event.insert(2, None)
DB.subscriber[5].event[2] = Dummy()
DB.subscriber[5].event[2].condition = []
DB.subscriber[5].event[2].context = 'player'
DB.subscriber[5].event[2].count = []
DB.subscriber[5].event[2].count.insert(0, None)
DB.subscriber[5].event[2].count[0] = Dummy()
DB.subscriber[5].event[2].count[0].value_ = 1
DB.subscriber[5].event[2].name = 'win'
DB.subscriber[5].event[2].operation = []
DB.subscriber[5].event[2].type = 'battle'
DB.subscriber[5].modify = []
DB.subscriber[5].name = 'skywolves'
DB.subscriber[5].operation = []
DB.subscriber[5].send = []
DB.subscriber.insert(6, None)
DB.subscriber[6] = Dummy()
DB.subscriber[6].activity = []
DB.subscriber[6].client = Dummy()
DB.subscriber[6].client.description = Dummy()
DB.subscriber[6].client.description.locale = 'MEDAL_DESCRIPTION_HUNGRY_FLOCK'
DB.subscriber[6].client.icon = Dummy()
DB.subscriber[6].client.icon.big = 'icons/awards/achievementsInfo/acGroupHungryFlock.dds'
DB.subscriber[6].client.icon.faded = 'icons/awards/achievements/acGroupHungryFlock_Outline.dds'
DB.subscriber[6].client.icon.small = 'icons/awards/achievements/acGroupHungryFlock.dds'
DB.subscriber[6].client.level = Dummy()
DB.subscriber[6].client.level.locale = 'MEDAL_LEVEL_LIMIT'
DB.subscriber[6].client.multiple = true
DB.subscriber[6].client.name = Dummy()
DB.subscriber[6].client.name.locale = 'MEDAL_NAME_HUNGRY_FLOCK'
DB.subscriber[6].client.order = 6
DB.subscriber[6].client.page = 0
DB.subscriber[6].condition = []
DB.subscriber[6].count = []
DB.subscriber[6].event = []
DB.subscriber[6].event.insert(0, None)
DB.subscriber[6].event[0] = Dummy()
DB.subscriber[6].event[0].condition = []
DB.subscriber[6].event[0].context = 'player'
DB.subscriber[6].event[0].count = []
DB.subscriber[6].event[0].count.insert(0, None)
DB.subscriber[6].event[0].count[0] = Dummy()
DB.subscriber[6].event[0].count[0].id = 0
DB.subscriber[6].event[0].count[0].value_ = 13
DB.subscriber[6].event[0].name = 'kill'
DB.subscriber[6].event[0].operation = []
DB.subscriber[6].event[0].type = 'battle'
DB.subscriber[6].event.insert(1, None)
DB.subscriber[6].event[1] = Dummy()
DB.subscriber[6].event[1].condition = []
DB.subscriber[6].event[1].condition.insert(0, None)
DB.subscriber[6].event[1].condition[0] = Dummy()
DB.subscriber[6].event[1].condition[0].and_ = []
DB.subscriber[6].event[1].condition[0].contains = []
DB.subscriber[6].event[1].condition[0].equal = []
DB.subscriber[6].event[1].condition[0].equal.insert(0, None)
DB.subscriber[6].event[1].condition[0].equal[0] = Dummy()
DB.subscriber[6].event[1].condition[0].equal[0].context = []
DB.subscriber[6].event[1].condition[0].equal[0].context.insert(0, None)
DB.subscriber[6].event[1].condition[0].equal[0].context[0] = 'victim.object'
DB.subscriber[6].event[1].condition[0].equal[0].value_ = []
DB.subscriber[6].event[1].condition[0].equal[0].value_.insert(0, None)
DB.subscriber[6].event[1].condition[0].equal[0].value_[0] = 'ground'
DB.subscriber[6].event[1].condition[0].gt = []
DB.subscriber[6].event[1].condition[0].gte = []
DB.subscriber[6].event[1].condition[0].id = []
DB.subscriber[6].event[1].condition[0].in_ = []
DB.subscriber[6].event[1].condition[0].lt = []
DB.subscriber[6].event[1].condition[0].lte = []
DB.subscriber[6].event[1].condition[0].not_ = []
DB.subscriber[6].event[1].condition[0].or_ = []
DB.subscriber[6].event[1].context = 'player'
DB.subscriber[6].event[1].count = []
DB.subscriber[6].event[1].count.insert(0, None)
DB.subscriber[6].event[1].count[0] = Dummy()
DB.subscriber[6].event[1].count[0].context = 'points.capture'
DB.subscriber[6].event[1].count[0].id = 1
DB.subscriber[6].event[1].count[0].value_ = 400
DB.subscriber[6].event[1].name = 'gain'
DB.subscriber[6].event[1].operation = []
DB.subscriber[6].event[1].type = 'battle'
DB.subscriber[6].event.insert(2, None)
DB.subscriber[6].event[2] = Dummy()
DB.subscriber[6].event[2].condition = []
DB.subscriber[6].event[2].context = 'player'
DB.subscriber[6].event[2].count = []
DB.subscriber[6].event[2].count.insert(0, None)
DB.subscriber[6].event[2].count[0] = Dummy()
DB.subscriber[6].event[2].count[0].value_ = 1
DB.subscriber[6].event[2].name = 'win'
DB.subscriber[6].event[2].operation = []
DB.subscriber[6].event[2].type = 'battle'
DB.subscriber[6].modify = []
DB.subscriber[6].name = 'hungryflock'
DB.subscriber[6].operation = []
DB.subscriber[6].send = []
DB.subscriber[0].id = -2039960399
DB.subscriber[1].id = 676639726
DB.subscriber[2].id = 1231771857
DB.subscriber[3].id = 285160729
DB.subscriber[4].id = 1879578363
DB.subscriber[5].id = -2037438654
DB.subscriber[6].id = -1831553329
DB.subscriber[0].eventIds = (761754430, 35456563)
DB.subscriber[1].eventIds = (-104890988, 615894436)
DB.subscriber[2].eventIds = (-104890988, 771950333, 615894436)
DB.subscriber[3].eventIds = (771950333, 615894436)
DB.subscriber[4].eventIds = (-104890988, -1789343170, -218451730)
DB.subscriber[5].eventIds = (-104890988, 771950333, -218451730)
DB.subscriber[6].eventIds = (-104890988, 771950333, -218451730)
mapping = {'db': DB,
 'indexes': {'subscriber': {'id': {-2039960399: (DB.subscriber[0],),
                                   676639726: (DB.subscriber[1],),
                                   1231771857: (DB.subscriber[2],),
                                   285160729: (DB.subscriber[3],),
                                   1879578363: (DB.subscriber[4],),
                                   -2037438654: (DB.subscriber[5],),
                                   -1831553329: (DB.subscriber[6],)},
                            'name': {'reset': (DB.subscriber[0],),
                                     'mastersofsky': (DB.subscriber[1],),
                                     'predatoryduet': (DB.subscriber[2],),
                                     'endofspear': (DB.subscriber[3],),
                                     'independent': (DB.subscriber[4],),
                                     'skywolves': (DB.subscriber[5],),
                                     'hungryflock': (DB.subscriber[6],)},
                            'type': {'achievement.reset': (DB.subscriber[0],),
                                     'achievement': (DB.subscriber[1],
                                                     DB.subscriber[2],
                                                     DB.subscriber[3],
                                                     DB.subscriber[4],
                                                     DB.subscriber[5],
                                                     DB.subscriber[6])},
                            'group': {'group': (DB.subscriber[0],
                                                DB.subscriber[1],
                                                DB.subscriber[2],
                                                DB.subscriber[3],
                                                DB.subscriber[4],
                                                DB.subscriber[5],
                                                DB.subscriber[6])},
                            'eventIds': {(761754430, 35456563): (DB.subscriber[0],),
                                         (-104890988, 615894436): (DB.subscriber[1],),
                                         (-104890988, 771950333, 615894436): (DB.subscriber[2],),
                                         (771950333, 615894436): (DB.subscriber[3],),
                                         (-104890988, -1789343170, -218451730): (DB.subscriber[4],),
                                         (-104890988, 771950333, -218451730): (DB.subscriber[5], DB.subscriber[6])},
                            'parent': {}}},
 'nested': ('subscriber.nested',),
 'type': {'default': 'subscriber',
          'all': ['subscriber']}}