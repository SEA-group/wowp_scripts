# Embedded file name: scripts/client/_ge_achievements_honorable.py
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
DB.header.client.place = 'left'
DB.header.condition = []
DB.header.count = []
DB.header.event = []
DB.header.group = 'honorable'
DB.header.markers = Dummy()
DB.header.markers.group = 'honorable'
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
DB.include.activity = []
DB.include.condition = []
DB.include.condition.insert(0, None)
DB.include.condition[0] = Dummy()
DB.include.condition[0].and_ = []
DB.include.condition[0].and_.insert(0, None)
DB.include.condition[0].and_[0] = Dummy()
DB.include.condition[0].and_[0].and_ = []
DB.include.condition[0].and_[0].contains = []
DB.include.condition[0].and_[0].equal = []
DB.include.condition[0].and_[0].equal.insert(0, None)
DB.include.condition[0].and_[0].equal[0] = Dummy()
DB.include.condition[0].and_[0].equal[0].context = []
DB.include.condition[0].and_[0].equal[0].context.insert(0, None)
DB.include.condition[0].and_[0].equal[0].context[0] = 'arena.type'
DB.include.condition[0].and_[0].equal[0].value_ = []
DB.include.condition[0].and_[0].equal[0].value_.insert(0, None)
DB.include.condition[0].and_[0].equal[0].value_[0] = 'normal'
DB.include.condition[0].and_[0].equal.insert(1, None)
DB.include.condition[0].and_[0].equal[1] = Dummy()
DB.include.condition[0].and_[0].equal[1].context = []
DB.include.condition[0].and_[0].equal[1].context.insert(0, None)
DB.include.condition[0].and_[0].equal[1].context[0] = 'arena.source'
DB.include.condition[0].and_[0].equal[1].value_ = []
DB.include.condition[0].and_[0].equal[1].value_.insert(0, None)
DB.include.condition[0].and_[0].equal[1].value_[0] = 'player'
DB.include.condition[0].and_[0].gt = []
DB.include.condition[0].and_[0].gte = []
DB.include.condition[0].and_[0].id = []
DB.include.condition[0].and_[0].in_ = []
DB.include.condition[0].and_[0].lt = []
DB.include.condition[0].and_[0].lte = []
DB.include.condition[0].and_[0].not_ = []
DB.include.condition[0].and_[0].or_ = []
DB.include.condition[0].contains = []
DB.include.condition[0].equal = []
DB.include.condition[0].gt = []
DB.include.condition[0].gte = []
DB.include.condition[0].id = []
DB.include.condition[0].in_ = []
DB.include.condition[0].lt = []
DB.include.condition[0].lte = []
DB.include.condition[0].not_ = []
DB.include.condition[0].or_ = []
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
DB.subscriber[0].event[0].operation[0].id[0].group = 'honorable'
DB.subscriber[0].event[0].operation[0].id[0].name = '*'
DB.subscriber[0].event[0].operation[0].id[0].type = 'achievement'
DB.subscriber[0].event[0].operation[0].rollback = true
DB.subscriber[0].event[0].operation[0].set = Dummy()
DB.subscriber[0].event[0].operation[0].set.completed = false
DB.subscriber[0].event[0].type = 'battle'
DB.subscriber[0].group = 'honorable'
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
DB.subscriber[1].client.description.locale = 'MEDAL_DESCRIPTION_ROCKETEER'
DB.subscriber[1].client.icon = Dummy()
DB.subscriber[1].client.icon.big = 'icons/awards/achievementsInfo/acHonoraryRocketeer.dds'
DB.subscriber[1].client.icon.faded = 'icons/awards/achievements/acHonoraryRocketeer_Outline.dds'
DB.subscriber[1].client.icon.small = 'icons/awards/achievements/acHonoraryRocketeer.dds'
DB.subscriber[1].client.multiple = true
DB.subscriber[1].client.name = Dummy()
DB.subscriber[1].client.name.locale = 'MEDAL_NAME_ROCKETEER'
DB.subscriber[1].client.order = 0
DB.subscriber[1].client.page = 0
DB.subscriber[1].condition = []
DB.subscriber[1].count = []
DB.subscriber[1].event = []
DB.subscriber[1].event.insert(0, None)
DB.subscriber[1].event[0] = Dummy()
DB.subscriber[1].event[0].condition = []
DB.subscriber[1].event[0].condition.insert(0, None)
DB.subscriber[1].event[0].condition[0] = Dummy()
DB.subscriber[1].event[0].condition[0].and_ = []
DB.subscriber[1].event[0].condition[0].contains = []
DB.subscriber[1].event[0].condition[0].equal = []
DB.subscriber[1].event[0].condition[0].equal.insert(0, None)
DB.subscriber[1].event[0].condition[0].equal[0] = Dummy()
DB.subscriber[1].event[0].condition[0].equal[0].context = []
DB.subscriber[1].event[0].condition[0].equal[0].context.insert(0, None)
DB.subscriber[1].event[0].condition[0].equal[0].context[0] = 'by'
DB.subscriber[1].event[0].condition[0].equal[0].value_ = []
DB.subscriber[1].event[0].condition[0].equal[0].value_.insert(0, None)
DB.subscriber[1].event[0].condition[0].equal[0].value_[0] = 'rocket'
DB.subscriber[1].event[0].condition[0].gt = []
DB.subscriber[1].event[0].condition[0].gte = []
DB.subscriber[1].event[0].condition[0].id = []
DB.subscriber[1].event[0].condition[0].in_ = []
DB.subscriber[1].event[0].condition[0].lt = []
DB.subscriber[1].event[0].condition[0].lte = []
DB.subscriber[1].event[0].condition[0].not_ = []
DB.subscriber[1].event[0].condition[0].or_ = []
DB.subscriber[1].event[0].context = 'player'
DB.subscriber[1].event[0].count = []
DB.subscriber[1].event[0].count.insert(0, None)
DB.subscriber[1].event[0].count[0] = Dummy()
DB.subscriber[1].event[0].count[0].id = 0
DB.subscriber[1].event[0].count[0].value_ = 1
DB.subscriber[1].event[0].name = 'kill'
DB.subscriber[1].event[0].operation = []
DB.subscriber[1].event[0].type = 'battle'
DB.subscriber[1].modify = []
DB.subscriber[1].name = 'rocketeer'
DB.subscriber[1].operation = []
DB.subscriber[1].send = []
DB.subscriber.insert(2, None)
DB.subscriber[2] = Dummy()
DB.subscriber[2].activity = []
DB.subscriber[2].client = Dummy()
DB.subscriber[2].client.description = Dummy()
DB.subscriber[2].client.description.locale = 'MEDAL_DESCRIPTION_RELIABLE_REAR'
DB.subscriber[2].client.icon = Dummy()
DB.subscriber[2].client.icon.big = 'icons/awards/achievementsInfo/acHonoraryReliableRear.dds'
DB.subscriber[2].client.icon.faded = 'icons/awards/achievements/acHonoraryReliableRear_Outline.dds'
DB.subscriber[2].client.icon.small = 'icons/awards/achievements/acHonoraryReliableRear.dds'
DB.subscriber[2].client.multiple = true
DB.subscriber[2].client.name = Dummy()
DB.subscriber[2].client.name.locale = 'MEDAL_NAME_RELIABLE_REAR'
DB.subscriber[2].client.order = 1
DB.subscriber[2].client.page = 0
DB.subscriber[2].condition = []
DB.subscriber[2].count = []
DB.subscriber[2].event = []
DB.subscriber[2].event.insert(0, None)
DB.subscriber[2].event[0] = Dummy()
DB.subscriber[2].event[0].condition = []
DB.subscriber[2].event[0].condition.insert(0, None)
DB.subscriber[2].event[0].condition[0] = Dummy()
DB.subscriber[2].event[0].condition[0].and_ = []
DB.subscriber[2].event[0].condition[0].contains = []
DB.subscriber[2].event[0].condition[0].equal = []
DB.subscriber[2].event[0].condition[0].equal.insert(0, None)
DB.subscriber[2].event[0].condition[0].equal[0] = Dummy()
DB.subscriber[2].event[0].condition[0].equal[0].context = []
DB.subscriber[2].event[0].condition[0].equal[0].context.insert(0, None)
DB.subscriber[2].event[0].condition[0].equal[0].context[0] = 'by'
DB.subscriber[2].event[0].condition[0].equal[0].value_ = []
DB.subscriber[2].event[0].condition[0].equal[0].value_.insert(0, None)
DB.subscriber[2].event[0].condition[0].equal[0].value_[0] = 'gunner'
DB.subscriber[2].event[0].condition[0].gt = []
DB.subscriber[2].event[0].condition[0].gte = []
DB.subscriber[2].event[0].condition[0].id = []
DB.subscriber[2].event[0].condition[0].in_ = []
DB.subscriber[2].event[0].condition[0].lt = []
DB.subscriber[2].event[0].condition[0].lte = []
DB.subscriber[2].event[0].condition[0].not_ = []
DB.subscriber[2].event[0].condition[0].or_ = []
DB.subscriber[2].event[0].context = 'player'
DB.subscriber[2].event[0].count = []
DB.subscriber[2].event[0].count.insert(0, None)
DB.subscriber[2].event[0].count[0] = Dummy()
DB.subscriber[2].event[0].count[0].id = 0
DB.subscriber[2].event[0].count[0].value_ = 1
DB.subscriber[2].event[0].name = 'kill'
DB.subscriber[2].event[0].operation = []
DB.subscriber[2].event[0].type = 'battle'
DB.subscriber[2].modify = []
DB.subscriber[2].name = 'reliablerear'
DB.subscriber[2].operation = []
DB.subscriber[2].send = []
DB.subscriber[0].id = -2018297589
DB.subscriber[1].id = -1381324868
DB.subscriber[2].id = 793762997
DB.subscriber[0].eventIds = (761754430,)
DB.subscriber[1].eventIds = (-104890988,)
DB.subscriber[2].eventIds = (-104890988,)
mapping = {'db': DB,
 'indexes': {'subscriber': {'id': {-2018297589: (DB.subscriber[0],),
                                   -1381324868: (DB.subscriber[1],),
                                   793762997: (DB.subscriber[2],)},
                            'name': {'reset': (DB.subscriber[0],),
                                     'rocketeer': (DB.subscriber[1],),
                                     'reliablerear': (DB.subscriber[2],)},
                            'type': {'achievement.reset': (DB.subscriber[0],),
                                     'achievement': (DB.subscriber[1], DB.subscriber[2])},
                            'group': {'honorable': (DB.subscriber[0], DB.subscriber[1], DB.subscriber[2])},
                            'eventIds': {(761754430,): (DB.subscriber[0],),
                                         (-104890988,): (DB.subscriber[1], DB.subscriber[2])},
                            'parent': {}}},
 'nested': ('subscriber.nested',),
 'type': {'default': 'subscriber',
          'all': ['subscriber']}}