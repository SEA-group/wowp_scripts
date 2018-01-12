# Embedded file name: scripts/client/GameEvents/features/achievements/model.py
from __future__ import absolute_import
from Helpers.i18n import localizeAchievements
from GameEventsCommon.db.backends import BundledBackend
from GameEventsCommon.db.model import Model
from GameEvents.model import GameEventObject

class AchievementObject(GameEventObject):

    def __init__(self, *args, **kwargs):
        kwargs['localeFunc'] = localizeAchievements
        super(AchievementObject, self).__init__(*args, **kwargs)

    @property
    def steps(self):
        return getattr(getattr(self.client, 'steps', None), 'value_', [])

    @property
    def levelConditionLocale(self):
        return getattr(getattr(self.client, 'level', None), 'locale', '')


AchievementModel = Model(backend=BundledBackend(modules=['_ge_achievements_coach',
 '_ge_achievements_distinguished',
 '_ge_achievements_group',
 '_ge_achievements_heroic',
 '_ge_achievements_honorable',
 '_ge_achievements_memorable',
 '_ge_achievements_old',
 '_ge_achievements_series',
 '_ge_achievements_stage',
 '_ge_achievements_epic',
 '_ge_achievements_special_events',
 '_ge_achievements_new_year',
 '_ge_achievements_albion']), instance=AchievementObject)