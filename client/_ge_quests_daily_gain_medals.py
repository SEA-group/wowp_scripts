# Embedded file name: scripts/client/_ge_quests_daily_gain_medals.py
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
DB.header.group = 'daily'
DB.header.markers = Dummy()
DB.header.markers.group = 'gain_medals'
DB.header.modify = []
DB.header.nested = Dummy()
DB.header.nested.subscriber = []
DB.header.nested.subscriber.insert(0, None)
DB.header.nested.subscriber[0] = Dummy()
DB.header.nested.subscriber[0].condition = []
DB.header.nested.subscriber[0].count = []
DB.header.nested.subscriber[0].event = []
DB.header.nested.subscriber[0].group = 'daily.tier'
DB.header.nested.subscriber[0].modify = []
DB.header.nested.subscriber[0].operation = []
DB.header.nested.subscriber[0].send = []
DB.header.nested.subscriber[0].type = 'quest'
DB.header.operation = []
DB.header.send = []
DB.header.server = Dummy()
DB.header.server.active = false
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
mapping = {'db': DB,
 'indexes': {'subscriber': {'id': {},
                            'name': {},
                            'type': {},
                            'group': {},
                            'eventIds': {},
                            'parent': {}}},
 'nested': ('subscriber.nested',),
 'type': {'default': 'subscriber',
          'all': ['subscriber']}}