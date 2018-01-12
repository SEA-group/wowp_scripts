# Embedded file name: scripts/common/GameEventsCommon/db/tests.py
from __future__ import absolute_import
import zlib
import copy
from .helpers import setInDummyInstance, addToDummyInstance
from .mapper import BundledDatabase, findInindex, filterByAttrsAndValues
from .storage import LinkedDatabase
from .model import Model
from .backends import BundledBackend

class Dummy:
    pass


DB = Dummy()
DB.include = Dummy()
DB.include.condition = []
DB.include.condition.insert(0, None)
DB.include.condition[0] = Dummy()
DB.include.condition[0].and_ = []
DB.include.condition[0].equal = []
DB.include.condition[0].equal.insert(0, None)
DB.include.condition[0].equal[0] = Dummy()
DB.include.condition[0].equal[0].context = []
DB.include.condition[0].equal[0].context.insert(0, None)
DB.include.condition[0].equal[0].context[0] = 'arena.type'
DB.include.condition[0].equal[0].value_ = []
DB.include.condition[0].equal[0].value_.insert(0, None)
DB.include.condition[0].equal[0].value_[0] = 'normal'
DB.include.condition[0].equal.insert(1, None)
DB.include.condition[0].equal[1] = Dummy()
DB.include.condition[0].equal[1].context = []
DB.include.condition[0].equal[1].context.insert(0, None)
DB.include.condition[0].equal[1].context[0] = 'arena.source'
DB.include.condition[0].equal[1].value_ = []
DB.include.condition[0].equal[1].value_.insert(0, None)
DB.include.condition[0].equal[1].value_[0] = 'player'
DB.include.condition[0].event = []
DB.include.condition[0].gt = []
DB.include.condition[0].gte = []
DB.include.condition[0].in_ = []
DB.include.condition[0].lt = []
DB.include.condition[0].lte = []
DB.include.condition[0].not_ = []
DB.include.condition[0].or_ = []
DB.include.count = []
DB.include.event = []
DB.include.modify = []
DB.include.nested = Dummy()
DB.include.nested.subscriber = []
DB.include.nested.subscriber.insert(0, None)
DB.include.nested.subscriber[0] = Dummy()
DB.include.nested.subscriber[0].condition = []
DB.include.nested.subscriber[0].condition.insert(0, None)
DB.include.nested.subscriber[0].condition[0] = Dummy()
DB.include.nested.subscriber[0].condition[0].and_ = []
DB.include.nested.subscriber[0].condition[0].equal = []
DB.include.nested.subscriber[0].condition[0].equal.insert(0, None)
DB.include.nested.subscriber[0].condition[0].equal[0] = Dummy()
DB.include.nested.subscriber[0].condition[0].equal[0].context = []
DB.include.nested.subscriber[0].condition[0].equal[0].context.insert(0, None)
DB.include.nested.subscriber[0].condition[0].equal[0].context[0] = 'arena.type'
DB.include.nested.subscriber[0].condition[0].equal[0].value_ = []
DB.include.nested.subscriber[0].condition[0].equal[0].value_.insert(0, None)
DB.include.nested.subscriber[0].condition[0].equal[0].value_[0] = 'normal'
DB.include.nested.subscriber[0].condition[0].equal.insert(1, None)
DB.include.nested.subscriber[0].condition[0].equal[1] = Dummy()
DB.include.nested.subscriber[0].condition[0].equal[1].context = []
DB.include.nested.subscriber[0].condition[0].equal[1].context.insert(0, None)
DB.include.nested.subscriber[0].condition[0].equal[1].context[0] = 'arena.source'
DB.include.nested.subscriber[0].condition[0].equal[1].value_ = []
DB.include.nested.subscriber[0].condition[0].equal[1].value_.insert(0, None)
DB.include.nested.subscriber[0].condition[0].equal[1].value_[0] = 'player'
DB.include.nested.subscriber[0].condition[0].event = []
DB.include.nested.subscriber[0].condition[0].gt = []
DB.include.nested.subscriber[0].condition[0].gte = []
DB.include.nested.subscriber[0].condition[0].in_ = []
DB.include.nested.subscriber[0].condition[0].lt = []
DB.include.nested.subscriber[0].condition[0].lte = []
DB.include.nested.subscriber[0].condition[0].not_ = []
DB.include.nested.subscriber[0].condition[0].or_ = []
DB.include.nested.subscriber[0].count = []
DB.include.nested.subscriber[0].event = []
DB.include.nested.subscriber[0].modify = []
DB.include.nested.subscriber[0].operation = []
DB.include.nested.subscriber[0].send = []
DB.include.nested.subscriber[0].transaction = []
DB.include.operation = []
DB.include.send = []
DB.include.transaction = []
DB.header = Dummy()
DB.header.condition = []
DB.header.count = []
DB.header.event = []
DB.header.markers = Dummy()
DB.header.markers.group = 'battle.points'
DB.header.group = 'honorable'
DB.header.modify = []
DB.header.nested = Dummy()
DB.header.nested.subscriber = []
DB.header.nested.subscriber.insert(0, None)
DB.header.nested.subscriber[0] = Dummy()
DB.header.nested.subscriber[0].condition = []
DB.header.nested.subscriber[0].count = []
DB.header.nested.subscriber[0].event = []
DB.header.nested.subscriber[0].group = 'some'
DB.header.nested.subscriber[0].modify = []
DB.header.nested.subscriber[0].operation = []
DB.header.nested.subscriber[0].send = []
DB.header.nested.subscriber[0].transaction = []
DB.header.nested.subscriber[0].type = 'achievement'
DB.header.operation = []
DB.header.send = []
DB.header.transaction = []
DB.header.type = 'achievement'
DB.subscriber = []
DB.subscriber.insert(0, None)
DB.subscriber[0] = Dummy()
DB.subscriber[0].group = 'bomber'
DB.subscriber[0].name = '5304'
DB.subscriber[0].markers = Dummy()
DB.subscriber[0].markers.difficulty = 'easy'
DB.subscriber[0].nested = Dummy()
DB.subscriber[0].nested.complete = 'all'
DB.subscriber[0].nested.subscriber = []
DB.subscriber[0].nested.subscriber.insert(0, None)
DB.subscriber[0].nested.subscriber[0] = Dummy()
DB.subscriber[0].nested.subscriber[0].client = Dummy()
DB.subscriber[0].nested.subscriber[0].client.description = Dummy()
DB.subscriber[0].nested.subscriber[0].client.description.locale = 'TOOLTIPS_ENGINE_DESCRIPTION'
DB.subscriber[0].nested.subscriber[0].client.icon = Dummy()
DB.subscriber[0].nested.subscriber[0].client.icon.big = 'icons/modules/max/bomber/blenheim4_engines.png'
DB.subscriber[0].nested.subscriber[0].client.icon.small = 'icons/modules/bomber/blenheim4_engines.png'
DB.subscriber[0].nested.subscriber[0].client.name = Dummy()
DB.subscriber[0].nested.subscriber[0].client.name.locale = 'LOBBY_SHOP_HEADER_ENGINES_LIST'
DB.subscriber[0].nested.subscriber[0].client.place = 'ENGINES_LIST'
DB.subscriber[0].nested.subscriber[0].group = 'part'
DB.subscriber[0].nested.subscriber[0].name = '1'
DB.subscriber[0].nested.subscriber[0].server = Dummy()
DB.subscriber[0].nested.subscriber[0].server.price = Dummy()
DB.subscriber[0].nested.subscriber[0].server.price.tickets = 4
DB.subscriber[0].nested.subscriber[0].type = 'hangar'
DB.subscriber[0].nested.subscriber.insert(1, None)
DB.subscriber[0].nested.subscriber[1] = Dummy()
DB.subscriber[0].nested.subscriber[1].client = Dummy()
DB.subscriber[0].nested.subscriber[1].client.description = Dummy()
DB.subscriber[0].nested.subscriber[1].client.description.locale = 'TOOLTIPS_FUEL_TANKS_DESCRIPTION'
DB.subscriber[0].nested.subscriber[1].client.icon = Dummy()
DB.subscriber[0].nested.subscriber[1].client.icon.big = 'icons/modules/max/bomber/common_fuelTanks.png'
DB.subscriber[0].nested.subscriber[1].client.icon.small = 'icons/modules/bomber/common_fuelTanks.png'
DB.subscriber[0].nested.subscriber[1].client.name = Dummy()
DB.subscriber[0].nested.subscriber[1].client.name.locale = 'LOBBY_FUEL_TANKS'
DB.subscriber[0].nested.subscriber[1].client.place = 'FUEL_TANKS'
DB.subscriber[0].nested.subscriber[1].group = 'partSpecial'
DB.subscriber[0].nested.subscriber[1].name = '1'
DB.subscriber[0].nested.subscriber[1].server = Dummy()
DB.subscriber[0].nested.subscriber[1].server.price = Dummy()
DB.subscriber[0].nested.subscriber[1].server.price.tickets = 4
DB.subscriber[0].nested.subscriber[1].type = 'hangar'
DB.subscriber[0].nested.subscriber.insert(2, None)
DB.subscriber[0].nested.subscriber[2] = Dummy()
DB.subscriber[0].nested.subscriber[2].client = Dummy()
DB.subscriber[0].nested.subscriber[2].client.description = Dummy()
DB.subscriber[0].nested.subscriber[2].client.description.locale = 'TOOLTIPS_PILOT_EQUIPMENT_DESCRIPTION'
DB.subscriber[0].nested.subscriber[2].client.icon = Dummy()
DB.subscriber[0].nested.subscriber[2].client.icon.big = 'icons/modules/max/bomber/common_pilotEquipment.png'
DB.subscriber[0].nested.subscriber[2].client.icon.small = 'icons/modules/bomber/common_pilotEquipment.png'
DB.subscriber[0].nested.subscriber[2].client.name = Dummy()
DB.subscriber[0].nested.subscriber[2].client.name.locale = 'LOBBY_PILOT_EQUIPMENT'
DB.subscriber[0].nested.subscriber[2].client.place = 'PILOT_EQUIPMENT'
DB.subscriber[0].nested.subscriber[2].name = '3'
DB.subscriber[0].nested.subscriber[2].server = Dummy()
DB.subscriber[0].nested.subscriber[2].server.price = Dummy()
DB.subscriber[0].nested.subscriber[2].server.price.tickets = 4
DB.subscriber[0].nested.subscriber.insert(3, None)
DB.subscriber[0].nested.subscriber[3] = Dummy()
DB.subscriber[0].nested.subscriber[3].client = Dummy()
DB.subscriber[0].nested.subscriber[3].client.description = Dummy()
DB.subscriber[0].nested.subscriber[3].client.description.locale = 'TOOLTIPS_PILOT_CABIN_DESCRIPTION'
DB.subscriber[0].nested.subscriber[3].client.icon = Dummy()
DB.subscriber[0].nested.subscriber[3].client.icon.big = 'icons/modules/max/bomber/blenheim4_pilotCabin.png'
DB.subscriber[0].nested.subscriber[3].client.icon.small = 'icons/modules/bomber/blenheim4_pilotCabin.png'
DB.subscriber[0].nested.subscriber[3].client.name = Dummy()
DB.subscriber[0].nested.subscriber[3].client.name.locale = 'LOBBY_PILOT_CABIN'
DB.subscriber[0].nested.subscriber[3].client.place = 'PILOT_CABIN'
DB.subscriber[0].nested.subscriber[3].group = 'part'
DB.subscriber[0].nested.subscriber[3].name = '4'
DB.subscriber[0].nested.subscriber[3].server = Dummy()
DB.subscriber[0].nested.subscriber[3].server.price = Dummy()
DB.subscriber[0].nested.subscriber[3].server.price.tickets = 5
DB.subscriber[0].nested.subscriber[3].type = 'hangar'
DB.subscriber[0].nested.subscriber[3].condition = []
DB.subscriber[0].nested.subscriber[3].condition.insert(0, None)
DB.subscriber[0].nested.subscriber[3].condition[0] = Dummy()
DB.subscriber[0].nested.subscriber[3].condition[0].and_ = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_.insert(0, None)
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0] = Dummy()
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].and_ = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal.insert(0, None)
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[0] = Dummy()
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[0].context = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[0].context.insert(0, None)
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[0].context[0] = 'arena.type'
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[0].value_ = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[0].value_.insert(0, None)
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[0].value_[0] = 'normal'
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal.insert(1, None)
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[1] = Dummy()
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[1].context = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[1].context.insert(0, None)
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[1].context[0] = 'arena.source'
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[1].value_ = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[1].value_.insert(0, None)
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].equal[1].value_[0] = 'player'
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].event = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].gt = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].gte = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].in_ = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].lt = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].lte = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].not_ = []
DB.subscriber[0].nested.subscriber[3].condition[0].and_[0].or_ = []
DB.subscriber[0].nested.subscriber[3].condition[0].equal = []
DB.subscriber[0].nested.subscriber[3].condition[0].event = []
DB.subscriber[0].nested.subscriber[3].condition[0].gt = []
DB.subscriber[0].nested.subscriber[3].condition[0].gte = []
DB.subscriber[0].nested.subscriber[3].condition[0].in_ = []
DB.subscriber[0].nested.subscriber[3].condition[0].lt = []
DB.subscriber[0].nested.subscriber[3].condition[0].lte = []
DB.subscriber[0].nested.subscriber[3].condition[0].not_ = []
DB.subscriber[0].nested.subscriber[3].condition[0].or_ = []
DB.subscriber[0].type = 'hangar'
mapping = {'db': DB,
 'type': {'default': 'subscriber',
          'all': ['subscriber']},
 'nested': ('subscriber.nested',),
 'indexes': {'subscriber': {'name': {'5304': (DB.subscriber[0],),
                                     '1': (DB.subscriber[0].nested.subscriber[0], DB.subscriber[0].nested.subscriber[1]),
                                     '3': (DB.subscriber[0].nested.subscriber[2],),
                                     '4': (DB.subscriber[0].nested.subscriber[3],)},
                            'group': {'part': (DB.subscriber[0].nested.subscriber[0], DB.subscriber[0].nested.subscriber[2], DB.subscriber[0].nested.subscriber[3]),
                                      'partSpecial': (DB.subscriber[0].nested.subscriber[1],)}}}}

def hashFunc(name, type_, group = ''):
    return zlib.adler32('_'.join((name, type_, group)))


for subscriber in DB.subscriber:
    subscriber.hash = hashFunc(subscriber.name, subscriber.type, getattr(subscriber, 'group', ''))

bomberDB = BundledDatabase(mapping, applyMerge=False)

def test_indexedFilterById():
    bomber = bomberDB.filter(name='5304')
    raise bomber == [DB.subscriber[0]] or AssertionError


def test_findInindex():
    items = list(findInindex(mapping['indexes']['subscriber'], {'name': '1'}))
    raise set(items) == set([DB.subscriber[0].nested.subscriber[0], DB.subscriber[0].nested.subscriber[1]]) or AssertionError


def test_multipleFilters():
    items = bomberDB.filter(group='part', name='1')
    raise items == [DB.subscriber[0].nested.subscriber[0]] or AssertionError
    items = bomberDB.filter(name='1')
    raise set(items) == set([DB.subscriber[0].nested.subscriber[0], DB.subscriber[0].nested.subscriber[1]]) or AssertionError


def test_getOneObjectByFilter():
    item = bomberDB.get(name='5304')
    raise item == DB.subscriber[0] or AssertionError


def test_allItems():
    raise set(bomberDB.all()) == set(DB.subscriber) or AssertionError
    raise set(bomberDB.all(includeNested=True)) == set(DB.subscriber) | set(DB.subscriber[0].nested.subscriber) or AssertionError


def test_bomberModel():
    BomberModel = Model(backend=BundledBackend(modules=['_ge_bomber_db'], applyMerge=False))
    raise set(BomberModel.has('nested')) == set(BomberModel.all(includeNested=False)) or AssertionError
    with BomberModel.use({'items': [1, 2, 3]}) as model:
        raise model._context == {'items': [1, 2, 3]} or AssertionError
    raise BomberModel._context is None or AssertionError
    return


def test_registeredModel():

    class MyModel(Model):
        pass

    BomberModel = MyModel(backend=BundledBackend(modules=['_ge_bomber_db']))
    for model in MyModel.registered:
        model.has('nested') == set(BomberModel.all())


def test_applyHeaderToAllSubscribers():
    newDB = copy.deepcopy(DB)
    mapping['db'] = newDB
    bundled = BundledDatabase(mapping)
    for subscriber in bundled.all():
        raise subscriber.type == 'hangar' or AssertionError
        raise subscriber.group == 'bomber' or AssertionError
        raise newDB.include.condition[0] in subscriber.condition or AssertionError
        for index, nested in enumerate(subscriber.nested.subscriber):
            if not (index == 2 and nested.type == 'achievement'):
                raise AssertionError
                if not nested.group == 'some':
                    raise AssertionError
                else:
                    raise nested.type == 'hangar' or AssertionError
                    raise nested.group in ('part', 'partSpecial') or AssertionError
                raise newDB.include.nested.subscriber[0].condition[0] in nested.condition or AssertionError
                raise nested.name == '4' and (len(nested.condition) == 2 or AssertionError)
            else:
                raise len(nested.condition) == 1 or AssertionError