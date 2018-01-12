# Embedded file name: scripts/client/_ge_modifiers_perday.py
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
DB.subscriber = []
DB.subscriber.insert(0, None)
DB.subscriber[0] = Dummy()
DB.subscriber[0].condition = []
DB.subscriber[0].condition.insert(0, None)
DB.subscriber[0].condition[0] = Dummy()
DB.subscriber[0].condition[0].and_ = []
DB.subscriber[0].condition[0].and_.insert(0, None)
DB.subscriber[0].condition[0].and_[0] = Dummy()
DB.subscriber[0].condition[0].and_[0].and_ = []
DB.subscriber[0].condition[0].and_[0].contains = []
DB.subscriber[0].condition[0].and_[0].equal = []
DB.subscriber[0].condition[0].and_[0].equal.insert(0, None)
DB.subscriber[0].condition[0].and_[0].equal[0] = Dummy()
DB.subscriber[0].condition[0].and_[0].equal[0].context = []
DB.subscriber[0].condition[0].and_[0].equal[0].context.insert(0, None)
DB.subscriber[0].condition[0].and_[0].equal[0].context[0] = 'arena.source'
DB.subscriber[0].condition[0].and_[0].equal[0].value_ = []
DB.subscriber[0].condition[0].and_[0].equal[0].value_.insert(0, None)
DB.subscriber[0].condition[0].and_[0].equal[0].value_[0] = 'player'
DB.subscriber[0].condition[0].and_[0].gt = []
DB.subscriber[0].condition[0].and_[0].gte = []
DB.subscriber[0].condition[0].and_[0].id = []
DB.subscriber[0].condition[0].and_[0].in_ = []
DB.subscriber[0].condition[0].and_[0].in_.insert(0, None)
DB.subscriber[0].condition[0].and_[0].in_[0] = Dummy()
DB.subscriber[0].condition[0].and_[0].in_[0].context = []
DB.subscriber[0].condition[0].and_[0].in_[0].context.insert(0, None)
DB.subscriber[0].condition[0].and_[0].in_[0].context[0] = 'arena.type'
DB.subscriber[0].condition[0].and_[0].in_[0].value_ = []
DB.subscriber[0].condition[0].and_[0].in_[0].value_.insert(0, None)
DB.subscriber[0].condition[0].and_[0].in_[0].value_[0] = 'normal'
DB.subscriber[0].condition[0].and_[0].in_[0].value_.insert(1, None)
DB.subscriber[0].condition[0].and_[0].in_[0].value_[1] = 'warAction'
DB.subscriber[0].condition[0].and_[0].lt = []
DB.subscriber[0].condition[0].and_[0].lte = []
DB.subscriber[0].condition[0].and_[0].not_ = []
DB.subscriber[0].condition[0].and_[0].or_ = []
DB.subscriber[0].condition[0].contains = []
DB.subscriber[0].condition[0].equal = []
DB.subscriber[0].condition[0].gt = []
DB.subscriber[0].condition[0].gte = []
DB.subscriber[0].condition[0].id = []
DB.subscriber[0].condition[0].in_ = []
DB.subscriber[0].condition[0].lt = []
DB.subscriber[0].condition[0].lte = []
DB.subscriber[0].condition[0].not_ = []
DB.subscriber[0].condition[0].or_ = []
DB.subscriber[0].count = []
DB.subscriber[0].event = []
DB.subscriber[0].event.insert(0, None)
DB.subscriber[0].event[0] = Dummy()
DB.subscriber[0].event[0].condition = []
DB.subscriber[0].event[0].context = 'player'
DB.subscriber[0].event[0].count = []
DB.subscriber[0].event[0].count.insert(0, None)
DB.subscriber[0].event[0].count[0] = Dummy()
DB.subscriber[0].event[0].count[0].valueFrom = '_economics:Economics.dailyBonus.dailyWinBonusRemains'
DB.subscriber[0].event[0].name = 'before.result.win'
DB.subscriber[0].event[0].operation = []
DB.subscriber[0].event[0].type = 'battle'
DB.subscriber[0].group = 'day.bonus'
DB.subscriber[0].modify = []
DB.subscriber[0].modify.insert(0, None)
DB.subscriber[0].modify[0] = Dummy()
DB.subscriber[0].modify[0].by = OperationModifyBy.multiply
DB.subscriber[0].modify[0].type = OperationModifyType.exp
DB.subscriber[0].modify[0].valueFrom = '_economics:Economics.dailyBonus.firstWinBonus.xpCoeff'
DB.subscriber[0].name = 'first.win'
DB.subscriber[0].operation = []
DB.subscriber[0].send = []
DB.subscriber[0].server = Dummy()
DB.subscriber[0].server.active = true
DB.subscriber[0].server.scope = []
DB.subscriber[0].server.scope.insert(0, None)
DB.subscriber[0].server.scope[0] = 'plane'
DB.subscriber[0].type = 'modifiers'
DB.subscriber.insert(1, None)
DB.subscriber[1] = Dummy()
DB.subscriber[1].condition = []
DB.subscriber[1].count = []
DB.subscriber[1].event = []
DB.subscriber[1].event.insert(0, None)
DB.subscriber[1].event[0] = Dummy()
DB.subscriber[1].event[0].condition = []
DB.subscriber[1].event[0].context = 'player'
DB.subscriber[1].event[0].count = []
DB.subscriber[1].event[0].name = 'day.changed'
DB.subscriber[1].event[0].operation = []
DB.subscriber[1].event[0].operation.insert(0, None)
DB.subscriber[1].event[0].operation[0] = Dummy()
DB.subscriber[1].event[0].operation[0].event = []
DB.subscriber[1].event[0].operation[0].id = []
DB.subscriber[1].event[0].operation[0].id.insert(0, None)
DB.subscriber[1].event[0].operation[0].id[0] = Dummy()
DB.subscriber[1].event[0].operation[0].id[0].group = 'day.bonus'
DB.subscriber[1].event[0].operation[0].id[0].name = 'first.win'
DB.subscriber[1].event[0].operation[0].id[0].type = 'modifiers'
DB.subscriber[1].event[0].operation[0].reset_ = true
DB.subscriber[1].event[0].operation[0].scope = 'plane'
DB.subscriber[1].event[0].operation[0].set = Dummy()
DB.subscriber[1].event[0].operation[0].set.completed = false
DB.subscriber[1].event[0].type = 'hangar'
DB.subscriber[1].group = 'day.bonus'
DB.subscriber[1].modify = []
DB.subscriber[1].name = 'reset'
DB.subscriber[1].operation = []
DB.subscriber[1].send = []
DB.subscriber[1].server = Dummy()
DB.subscriber[1].server.active = true
DB.subscriber[1].server.overwrite = true
DB.subscriber[1].server.repeat = true
DB.subscriber[1].server.scope = []
DB.subscriber[1].server.scope.insert(0, None)
DB.subscriber[1].server.scope[0] = 'player'
DB.subscriber[1].type = 'modifiers'
DB.subscriber[0].id = -1216274312
DB.subscriber[1].id = -918543081
DB.subscriber[0].eventIds = (652423421,)
DB.subscriber[1].eventIds = (35456563,)
mapping = {'db': DB,
 'indexes': {'subscriber': {'id': {-1216274312: (DB.subscriber[0],),
                                   -918543081: (DB.subscriber[1],)},
                            'name': {'first.win': (DB.subscriber[0],),
                                     'reset': (DB.subscriber[1],)},
                            'type': {'modifiers': (DB.subscriber[0], DB.subscriber[1])},
                            'group': {'day.bonus': (DB.subscriber[0], DB.subscriber[1])},
                            'eventIds': {(652423421,): (DB.subscriber[0],),
                                         (35456563,): (DB.subscriber[1],)},
                            'parent': {}}},
 'nested': ('subscriber.nested',),
 'type': {'default': 'subscriber',
          'all': ['subscriber']}}