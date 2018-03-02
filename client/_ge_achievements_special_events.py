# Embedded file name: scripts/client/_ge_achievements_special_events.py
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
DB.header.group = 'memorable'
DB.header.markers = Dummy()
DB.header.markers.group = 'memorable'
DB.header.modify = []
DB.header.operation = []
DB.header.send = []
DB.header.server = Dummy()
DB.header.server.active = true
DB.header.server.hidden = true
DB.header.server.scope = []
DB.header.server.scope.insert(0, None)
DB.header.server.scope[0] = 'player'
DB.header.type = 'achievement'
DB.include = Dummy()
DB.include.activity = []
DB.include.condition = []
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
DB.subscriber[0].client = Dummy()
DB.subscriber[0].client.description = Dummy()
DB.subscriber[0].client.description.locale = 'MEDAL_DESCRIPTION_WG_FEST_2017'
DB.subscriber[0].client.icon = Dummy()
DB.subscriber[0].client.icon.big = 'icons/awards/achievementsInfo/signsWGFest2017.dds'
DB.subscriber[0].client.icon.faded = 'icons/awards/achievements/signsWGFest2017_Outline.dds'
DB.subscriber[0].client.icon.small = 'icons/awards/achievements/signsWGFest2017.dds'
DB.subscriber[0].client.multiple = false
DB.subscriber[0].client.name = Dummy()
DB.subscriber[0].client.name.locale = 'MEDAL_NAME_WG_FEST_2017'
DB.subscriber[0].client.order = 18
DB.subscriber[0].client.page = 0
DB.subscriber[0].condition = []
DB.subscriber[0].count = []
DB.subscriber[0].event = []
DB.subscriber[0].modify = []
DB.subscriber[0].name = 'wg_fest_2017'
DB.subscriber[0].operation = []
DB.subscriber[0].send = []
DB.subscriber[0].id = 386542884
mapping = {'db': DB,
 'indexes': {'subscriber': {'id': {386542884: (DB.subscriber[0],)},
                            'name': {'wg_fest_2017': (DB.subscriber[0],)},
                            'type': {'achievement': (DB.subscriber[0],)},
                            'group': {'memorable': (DB.subscriber[0],)},
                            'eventIds': {},
                            'parent': {}}},
 'nested': ('subscriber.nested',),
 'type': {'default': 'subscriber',
          'all': ['subscriber']}}