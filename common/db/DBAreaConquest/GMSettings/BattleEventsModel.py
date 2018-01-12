# Embedded file name: scripts/common/db/DBAreaConquest/GMSettings/BattleEventsModel.py
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBListProperty, DBModelProperty, DBStringProperty, DBPropertyBase
from GameModeSettings import ACSettings as DEFAULT_SETTINGS

class _PredicateOptionsProperty(DBPropertyBase):

    def _doRead(self, section):
        options = {}
        if section.has_key('duration'):
            options['duration'] = section['duration'].asInt
        return options


class BattleEventProperty(DBPropertyBase):

    def _doRead(self, section):
        name = section.asString
        return DEFAULT_SETTINGS.BATTLE_EVENT_TYPE.getValue(name)


class PredicateModel(DBModelBase):
    type = DBStringProperty()
    options = _PredicateOptionsProperty()

    def read(self, section):
        super(PredicateModel, self).read(section)
        raise self.type in DEFAULT_SETTINGS.PREDICATE_TYPE.ALL or AssertionError('Wrong predicate type: {0}'.format(self.type))


class TriggerModel(DBModelBase):
    battleEvent = BattleEventProperty(sectionName='event')
    predicate = DBModelProperty(factory=PredicateModel)


class BattleEventsModel(DBModelBase):
    triggers = DBListProperty(elementType=DBModelProperty(factory=TriggerModel, sectionName='trigger'))