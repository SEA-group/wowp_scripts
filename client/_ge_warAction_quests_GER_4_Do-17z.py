# Embedded file name: scripts/client/_ge_warAction_quests_GER_4_Do-17z.py
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
DB.header.condition = []
DB.header.count = []
DB.header.event = []
DB.header.group = 'warAction'
DB.header.modify = []
DB.header.nested = Dummy()
DB.header.nested.subscriber = []
DB.header.nested.subscriber.insert(0, None)
DB.header.nested.subscriber[0] = Dummy()
DB.header.nested.subscriber[0].condition = []
DB.header.nested.subscriber[0].count = []
DB.header.nested.subscriber[0].event = []
DB.header.nested.subscriber[0].group = 'warAction'
DB.header.nested.subscriber[0].modify = []
DB.header.nested.subscriber[0].operation = []
DB.header.nested.subscriber[0].send = []
DB.header.nested.subscriber[0].server = Dummy()
DB.header.nested.subscriber[0].server.active = false
DB.header.nested.subscriber[0].server.scope = []
DB.header.nested.subscriber[0].server.scope.insert(0, None)
DB.header.nested.subscriber[0].server.scope[0] = 'player'
DB.header.nested.subscriber[0].type = 'quest'
DB.header.operation = []
DB.header.send = []
DB.header.server = Dummy()
DB.header.server.active = false
DB.header.server.lifeTime = 86400
DB.header.server.price = Dummy()
DB.header.server.price.prolong = Dummy()
DB.header.server.price.prolong.tickets = 2
DB.header.server.price.prolong.time = 86400
DB.header.server.scope = []
DB.header.server.scope.insert(0, None)
DB.header.server.scope[0] = 'player'
DB.header.type = 'quest'
DB.include = Dummy()
DB.include.condition = []
DB.include.count = []
DB.include.event = []
DB.include.metadata = Dummy()
DB.include.metadata.doneCount = true
DB.include.metadata.event = []
DB.include.metadata.firstDoneTime = true
DB.include.metadata.lastDoneTime = true
DB.include.modify = []
DB.include.nested = Dummy()
DB.include.nested.subscriber = []
DB.include.nested.subscriber.insert(0, None)
DB.include.nested.subscriber[0] = Dummy()
DB.include.nested.subscriber[0].condition = []
DB.include.nested.subscriber[0].condition.insert(0, None)
DB.include.nested.subscriber[0].condition[0] = Dummy()
DB.include.nested.subscriber[0].condition[0].and_ = []
DB.include.nested.subscriber[0].condition[0].and_.insert(0, None)
DB.include.nested.subscriber[0].condition[0].and_[0] = Dummy()
DB.include.nested.subscriber[0].condition[0].and_[0].and_ = []
DB.include.nested.subscriber[0].condition[0].and_[0].contains = []
DB.include.nested.subscriber[0].condition[0].and_[0].equal = []
DB.include.nested.subscriber[0].condition[0].and_[0].equal.insert(0, None)
DB.include.nested.subscriber[0].condition[0].and_[0].equal[0] = Dummy()
DB.include.nested.subscriber[0].condition[0].and_[0].equal[0].context = []
DB.include.nested.subscriber[0].condition[0].and_[0].equal[0].context.insert(0, None)
DB.include.nested.subscriber[0].condition[0].and_[0].equal[0].context[0] = 'arena.type'
DB.include.nested.subscriber[0].condition[0].and_[0].equal[0].value_ = []
DB.include.nested.subscriber[0].condition[0].and_[0].equal[0].value_.insert(0, None)
DB.include.nested.subscriber[0].condition[0].and_[0].equal[0].value_[0] = 'normal'
DB.include.nested.subscriber[0].condition[0].and_[0].equal.insert(1, None)
DB.include.nested.subscriber[0].condition[0].and_[0].equal[1] = Dummy()
DB.include.nested.subscriber[0].condition[0].and_[0].equal[1].context = []
DB.include.nested.subscriber[0].condition[0].and_[0].equal[1].context.insert(0, None)
DB.include.nested.subscriber[0].condition[0].and_[0].equal[1].context[0] = 'arena.source'
DB.include.nested.subscriber[0].condition[0].and_[0].equal[1].value_ = []
DB.include.nested.subscriber[0].condition[0].and_[0].equal[1].value_.insert(0, None)
DB.include.nested.subscriber[0].condition[0].and_[0].equal[1].value_[0] = 'player'
DB.include.nested.subscriber[0].condition[0].and_[0].gt = []
DB.include.nested.subscriber[0].condition[0].and_[0].gte = []
DB.include.nested.subscriber[0].condition[0].and_[0].id = []
DB.include.nested.subscriber[0].condition[0].and_[0].in_ = []
DB.include.nested.subscriber[0].condition[0].and_[0].lt = []
DB.include.nested.subscriber[0].condition[0].and_[0].lte = []
DB.include.nested.subscriber[0].condition[0].and_[0].not_ = []
DB.include.nested.subscriber[0].condition[0].and_[0].or_ = []
DB.include.nested.subscriber[0].condition[0].contains = []
DB.include.nested.subscriber[0].condition[0].equal = []
DB.include.nested.subscriber[0].condition[0].gt = []
DB.include.nested.subscriber[0].condition[0].gte = []
DB.include.nested.subscriber[0].condition[0].id = []
DB.include.nested.subscriber[0].condition[0].in_ = []
DB.include.nested.subscriber[0].condition[0].lt = []
DB.include.nested.subscriber[0].condition[0].lte = []
DB.include.nested.subscriber[0].condition[0].not_ = []
DB.include.nested.subscriber[0].condition[0].or_ = []
DB.include.nested.subscriber[0].condition.insert(1, None)
DB.include.nested.subscriber[0].condition[1] = Dummy()
DB.include.nested.subscriber[0].condition[1].and_ = []
DB.include.nested.subscriber[0].condition[1].contains = []
DB.include.nested.subscriber[0].condition[1].equal = []
DB.include.nested.subscriber[0].condition[1].gt = []
DB.include.nested.subscriber[0].condition[1].gte = []
DB.include.nested.subscriber[0].condition[1].gte.insert(0, None)
DB.include.nested.subscriber[0].condition[1].gte[0] = Dummy()
DB.include.nested.subscriber[0].condition[1].gte[0].context = []
DB.include.nested.subscriber[0].condition[1].gte[0].context.insert(0, None)
DB.include.nested.subscriber[0].condition[1].gte[0].context[0] = 'player.plane.level'
DB.include.nested.subscriber[0].condition[1].gte[0].value_ = []
DB.include.nested.subscriber[0].condition[1].gte[0].value_.insert(0, None)
DB.include.nested.subscriber[0].condition[1].gte[0].value_[0] = '4'
DB.include.nested.subscriber[0].condition[1].id = []
DB.include.nested.subscriber[0].condition[1].in_ = []
DB.include.nested.subscriber[0].condition[1].lt = []
DB.include.nested.subscriber[0].condition[1].lte = []
DB.include.nested.subscriber[0].condition[1].not_ = []
DB.include.nested.subscriber[0].condition[1].or_ = []
DB.include.nested.subscriber[0].count = []
DB.include.nested.subscriber[0].event = []
DB.include.nested.subscriber[0].metadata = Dummy()
DB.include.nested.subscriber[0].metadata.doneCount = true
DB.include.nested.subscriber[0].metadata.event = []
DB.include.nested.subscriber[0].metadata.firstDoneTime = true
DB.include.nested.subscriber[0].metadata.lastDoneTime = true
DB.include.nested.subscriber[0].modify = []
DB.include.nested.subscriber[0].operation = []
DB.include.nested.subscriber[0].send = []
DB.include.operation = []
DB.include.send = []
DB.subscriber = []
DB.subscriber.insert(0, None)
DB.subscriber[0] = Dummy()
DB.subscriber[0].client = Dummy()
DB.subscriber[0].client.description = Dummy()
DB.subscriber[0].client.description.locale = 'LOBBY_JA_TR_COMPLETE_QUEST_IN_PIECETIME_GET_FREE_PLANE'
DB.subscriber[0].client.name = Dummy()
DB.subscriber[0].client.name.locale = 'LOBBY_REWARD_SPECIAL_QUEST_DO17Z'
DB.subscriber[0].client.order = 1
DB.subscriber[0].condition = []
DB.subscriber[0].count = []
DB.subscriber[0].event = []
DB.subscriber[0].modify = []
DB.subscriber[0].name = 'Do-17z-2'
DB.subscriber[0].nested = Dummy()
DB.subscriber[0].nested.complete = 'chain'
DB.subscriber[0].nested.display = true
DB.subscriber[0].nested.subscriber = []
DB.subscriber[0].nested.subscriber.insert(0, None)
DB.subscriber[0].nested.subscriber[0] = Dummy()
DB.subscriber[0].nested.subscriber[0].client = Dummy()
DB.subscriber[0].nested.subscriber[0].client.description = Dummy()
DB.subscriber[0].nested.subscriber[0].client.description.locale = 'LOBBY_QUESTS_2016_DAILY_069'
DB.subscriber[0].nested.subscriber[0].client.name = Dummy()
DB.subscriber[0].nested.subscriber[0].client.name.locale = 'LOBBY_QUESTS_2016_DAILY_069_NAME'
DB.subscriber[0].nested.subscriber[0].client.order = 1
DB.subscriber[0].nested.subscriber[0].condition = []
DB.subscriber[0].nested.subscriber[0].count = []
DB.subscriber[0].nested.subscriber[0].event = []
DB.subscriber[0].nested.subscriber[0].event.insert(0, None)
DB.subscriber[0].nested.subscriber[0].event[0] = Dummy()
DB.subscriber[0].nested.subscriber[0].event[0].condition = []
DB.subscriber[0].nested.subscriber[0].event[0].condition.insert(0, None)
DB.subscriber[0].nested.subscriber[0].event[0].condition[0] = Dummy()
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].and_ = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].contains = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].equal = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].equal.insert(0, None)
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].equal[0] = Dummy()
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].equal[0].context = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].equal[0].context.insert(0, None)
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].equal[0].context[0] = 'victim.type'
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].equal[0].value_ = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].equal[0].value_.insert(0, None)
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].equal[0].value_[0] = 'antiair'
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].gt = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].gte = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].id = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].in_ = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].lt = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].lte = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].not_ = []
DB.subscriber[0].nested.subscriber[0].event[0].condition[0].or_ = []
DB.subscriber[0].nested.subscriber[0].event[0].context = 'player'
DB.subscriber[0].nested.subscriber[0].event[0].count = []
DB.subscriber[0].nested.subscriber[0].event[0].count.insert(0, None)
DB.subscriber[0].nested.subscriber[0].event[0].count[0] = Dummy()
DB.subscriber[0].nested.subscriber[0].event[0].count[0].display = true
DB.subscriber[0].nested.subscriber[0].event[0].count[0].value_ = 12
DB.subscriber[0].nested.subscriber[0].event[0].name = 'part.destroy'
DB.subscriber[0].nested.subscriber[0].event[0].operation = []
DB.subscriber[0].nested.subscriber[0].event[0].type = 'battle'
DB.subscriber[0].nested.subscriber[0].event.insert(1, None)
DB.subscriber[0].nested.subscriber[0].event[1] = Dummy()
DB.subscriber[0].nested.subscriber[0].event[1].condition = []
DB.subscriber[0].nested.subscriber[0].event[1].context = 'player'
DB.subscriber[0].nested.subscriber[0].event[1].count = []
DB.subscriber[0].nested.subscriber[0].event[1].name = 'finish'
DB.subscriber[0].nested.subscriber[0].event[1].operation = []
DB.subscriber[0].nested.subscriber[0].event[1].operation.insert(0, None)
DB.subscriber[0].nested.subscriber[0].event[1].operation[0] = Dummy()
DB.subscriber[0].nested.subscriber[0].event[1].operation[0].event = []
DB.subscriber[0].nested.subscriber[0].event[1].operation[0].id = []
DB.subscriber[0].nested.subscriber[0].event[1].operation[0].rollback = true
DB.subscriber[0].nested.subscriber[0].event[1].operation[0].self = true
DB.subscriber[0].nested.subscriber[0].event[1].type = 'battle'
DB.subscriber[0].nested.subscriber[0].event.insert(2, None)
DB.subscriber[0].nested.subscriber[0].event[2] = Dummy()
DB.subscriber[0].nested.subscriber[0].event[2].condition = []
DB.subscriber[0].nested.subscriber[0].event[2].context = 'player'
DB.subscriber[0].nested.subscriber[0].event[2].count = []
DB.subscriber[0].nested.subscriber[0].event[2].name = 'finish'
DB.subscriber[0].nested.subscriber[0].event[2].operation = []
DB.subscriber[0].nested.subscriber[0].event[2].operation.insert(0, None)
DB.subscriber[0].nested.subscriber[0].event[2].operation[0] = Dummy()
DB.subscriber[0].nested.subscriber[0].event[2].operation[0].event = []
DB.subscriber[0].nested.subscriber[0].event[2].operation[0].id = []
DB.subscriber[0].nested.subscriber[0].event[2].operation[0].rollback = true
DB.subscriber[0].nested.subscriber[0].event[2].operation[0].self = true
DB.subscriber[0].nested.subscriber[0].event[2].type = 'battle'
DB.subscriber[0].nested.subscriber[0].modify = []
DB.subscriber[0].nested.subscriber[0].name = '1'
DB.subscriber[0].nested.subscriber[0].operation = []
DB.subscriber[0].nested.subscriber[0].send = []
DB.subscriber[0].nested.subscriber[0].server = Dummy()
DB.subscriber[0].nested.subscriber[0].server.price = Dummy()
DB.subscriber[0].nested.subscriber[0].server.price.buy = Dummy()
DB.subscriber[0].nested.subscriber[0].server.price.buy.tickets = 1
DB.subscriber[0].nested.subscriber[0].server.scope = []
DB.subscriber[0].nested.subscriber.insert(1, None)
DB.subscriber[0].nested.subscriber[1] = Dummy()
DB.subscriber[0].nested.subscriber[1].client = Dummy()
DB.subscriber[0].nested.subscriber[1].client.description = Dummy()
DB.subscriber[0].nested.subscriber[1].client.description.locale = 'LOBBY_QUESTS_2016_DAILY_057'
DB.subscriber[0].nested.subscriber[1].client.name = Dummy()
DB.subscriber[0].nested.subscriber[1].client.name.locale = 'LOBBY_QUESTS_2016_DAILY_057_NAME'
DB.subscriber[0].nested.subscriber[1].client.order = 2
DB.subscriber[0].nested.subscriber[1].condition = []
DB.subscriber[0].nested.subscriber[1].count = []
DB.subscriber[0].nested.subscriber[1].event = []
DB.subscriber[0].nested.subscriber[1].event.insert(0, None)
DB.subscriber[0].nested.subscriber[1].event[0] = Dummy()
DB.subscriber[0].nested.subscriber[1].event[0].condition = []
DB.subscriber[0].nested.subscriber[1].event[0].context = 'player'
DB.subscriber[0].nested.subscriber[1].event[0].count = []
DB.subscriber[0].nested.subscriber[1].event[0].count.insert(0, None)
DB.subscriber[0].nested.subscriber[1].event[0].count[0] = Dummy()
DB.subscriber[0].nested.subscriber[1].event[0].count[0].display = true
DB.subscriber[0].nested.subscriber[1].event[0].count[0].value_ = 250
DB.subscriber[0].nested.subscriber[1].event[0].name = 'destroy'
DB.subscriber[0].nested.subscriber[1].event[0].operation = []
DB.subscriber[0].nested.subscriber[1].event[0].type = 'battle'
DB.subscriber[0].nested.subscriber[1].modify = []
DB.subscriber[0].nested.subscriber[1].name = '2'
DB.subscriber[0].nested.subscriber[1].operation = []
DB.subscriber[0].nested.subscriber[1].send = []
DB.subscriber[0].nested.subscriber[1].server = Dummy()
DB.subscriber[0].nested.subscriber[1].server.price = Dummy()
DB.subscriber[0].nested.subscriber[1].server.price.buy = Dummy()
DB.subscriber[0].nested.subscriber[1].server.price.buy.tickets = 4
DB.subscriber[0].nested.subscriber[1].server.scope = []
DB.subscriber[0].nested.subscriber.insert(2, None)
DB.subscriber[0].nested.subscriber[2] = Dummy()
DB.subscriber[0].nested.subscriber[2].client = Dummy()
DB.subscriber[0].nested.subscriber[2].client.description = Dummy()
DB.subscriber[0].nested.subscriber[2].client.description.locale = 'LOBBY_QUESTS_2016_DAILY_059'
DB.subscriber[0].nested.subscriber[2].client.name = Dummy()
DB.subscriber[0].nested.subscriber[2].client.name.locale = 'LOBBY_QUESTS_2016_DAILY_059_NAME'
DB.subscriber[0].nested.subscriber[2].client.order = 3
DB.subscriber[0].nested.subscriber[2].condition = []
DB.subscriber[0].nested.subscriber[2].count = []
DB.subscriber[0].nested.subscriber[2].event = []
DB.subscriber[0].nested.subscriber[2].event.insert(0, None)
DB.subscriber[0].nested.subscriber[2].event[0] = Dummy()
DB.subscriber[0].nested.subscriber[2].event[0].condition = []
DB.subscriber[0].nested.subscriber[2].event[0].context = 'player'
DB.subscriber[0].nested.subscriber[2].event[0].count = []
DB.subscriber[0].nested.subscriber[2].event[0].count.insert(0, None)
DB.subscriber[0].nested.subscriber[2].event[0].count[0] = Dummy()
DB.subscriber[0].nested.subscriber[2].event[0].count[0].display = true
DB.subscriber[0].nested.subscriber[2].event[0].count[0].value_ = 20
DB.subscriber[0].nested.subscriber[2].event[0].name = 'destroy'
DB.subscriber[0].nested.subscriber[2].event[0].operation = []
DB.subscriber[0].nested.subscriber[2].event[0].type = 'battle'
DB.subscriber[0].nested.subscriber[2].event.insert(1, None)
DB.subscriber[0].nested.subscriber[2].event[1] = Dummy()
DB.subscriber[0].nested.subscriber[2].event[1].condition = []
DB.subscriber[0].nested.subscriber[2].event[1].context = 'player'
DB.subscriber[0].nested.subscriber[2].event[1].count = []
DB.subscriber[0].nested.subscriber[2].event[1].count.insert(0, None)
DB.subscriber[0].nested.subscriber[2].event[1].count[0] = Dummy()
DB.subscriber[0].nested.subscriber[2].event[1].count[0].value_ = 1
DB.subscriber[0].nested.subscriber[2].event[1].name = 'win'
DB.subscriber[0].nested.subscriber[2].event[1].operation = []
DB.subscriber[0].nested.subscriber[2].event[1].type = 'battle'
DB.subscriber[0].nested.subscriber[2].event.insert(2, None)
DB.subscriber[0].nested.subscriber[2].event[2] = Dummy()
DB.subscriber[0].nested.subscriber[2].event[2].condition = []
DB.subscriber[0].nested.subscriber[2].event[2].context = 'player'
DB.subscriber[0].nested.subscriber[2].event[2].count = []
DB.subscriber[0].nested.subscriber[2].event[2].name = 'finish'
DB.subscriber[0].nested.subscriber[2].event[2].operation = []
DB.subscriber[0].nested.subscriber[2].event[2].operation.insert(0, None)
DB.subscriber[0].nested.subscriber[2].event[2].operation[0] = Dummy()
DB.subscriber[0].nested.subscriber[2].event[2].operation[0].event = []
DB.subscriber[0].nested.subscriber[2].event[2].operation[0].id = []
DB.subscriber[0].nested.subscriber[2].event[2].operation[0].rollback = true
DB.subscriber[0].nested.subscriber[2].event[2].operation[0].self = true
DB.subscriber[0].nested.subscriber[2].event[2].type = 'battle'
DB.subscriber[0].nested.subscriber[2].modify = []
DB.subscriber[0].nested.subscriber[2].name = '3'
DB.subscriber[0].nested.subscriber[2].operation = []
DB.subscriber[0].nested.subscriber[2].send = []
DB.subscriber[0].nested.subscriber[2].server = Dummy()
DB.subscriber[0].nested.subscriber[2].server.price = Dummy()
DB.subscriber[0].nested.subscriber[2].server.price.buy = Dummy()
DB.subscriber[0].nested.subscriber[2].server.price.buy.tickets = 5
DB.subscriber[0].nested.subscriber[2].server.scope = []
DB.subscriber[0].operation = []
DB.subscriber[0].send = []
DB.subscriber[0].id = 1828517396
DB.subscriber[0].nested.subscriber[0].id = -998249729
DB.subscriber[0].nested.subscriber[1].id = 1570606334
DB.subscriber[0].nested.subscriber[2].id = -1676455106
DB.subscriber[0].nested.subscriber[0].eventIds = (151230433, 761754430, 761754430)
DB.subscriber[0].nested.subscriber[1].eventIds = (-1370837730,)
DB.subscriber[0].nested.subscriber[2].eventIds = (-1370837730, -218451730, 761754430)
DB.subscriber[0].nested.subscriber[0].parent = 1828517396
DB.subscriber[0].nested.subscriber[1].parent = 1828517396
DB.subscriber[0].nested.subscriber[2].parent = 1828517396
mapping = {'db': DB,
 'indexes': {'subscriber': {'id': {1828517396: (DB.subscriber[0],),
                                   -998249729: (DB.subscriber[0].nested.subscriber[0],),
                                   1570606334: (DB.subscriber[0].nested.subscriber[1],),
                                   -1676455106: (DB.subscriber[0].nested.subscriber[2],)},
                            'name': {'Do-17z-2': (DB.subscriber[0],),
                                     '1': (DB.subscriber[0].nested.subscriber[0],),
                                     '2': (DB.subscriber[0].nested.subscriber[1],),
                                     '3': (DB.subscriber[0].nested.subscriber[2],)},
                            'type': {'quest': (DB.subscriber[0],
                                               DB.subscriber[0].nested.subscriber[0],
                                               DB.subscriber[0].nested.subscriber[1],
                                               DB.subscriber[0].nested.subscriber[2])},
                            'group': {'warAction': (DB.subscriber[0],
                                                    DB.subscriber[0].nested.subscriber[0],
                                                    DB.subscriber[0].nested.subscriber[1],
                                                    DB.subscriber[0].nested.subscriber[2])},
                            'eventIds': {(151230433, 761754430, 761754430): (DB.subscriber[0].nested.subscriber[0],),
                                         (-1370837730,): (DB.subscriber[0].nested.subscriber[1],),
                                         (-1370837730, -218451730, 761754430): (DB.subscriber[0].nested.subscriber[2],)},
                            'parent': {1828517396: (DB.subscriber[0].nested.subscriber[0], DB.subscriber[0].nested.subscriber[1], DB.subscriber[0].nested.subscriber[2])}}},
 'nested': ('subscriber.nested',),
 'type': {'default': 'subscriber',
          'all': ['subscriber']}}