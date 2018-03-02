# Embedded file name: scripts/client/GameEvents/features/quests/model.py
from __future__ import absolute_import
from GameEventsCommon.db.backends import BundledBackend
from GameEventsCommon.db.model import Model
from GameEvents.model import GameEventObject

class QuestObject(GameEventObject):

    @property
    def params(self):
        if self.group == 'warAction':
            return {}
        else:
            order = 1
            if getattr(self._attrs, 'parent', None):
                try:
                    order = int(getattr(self._attrs, 'name', 1))
                except ValueError:
                    pass

            client = getattr(self._attrs, 'client', None)
            order = getattr(client, 'order', order)
            return {'order': order}


QuestModel = Model(backend=BundledBackend(modules=['_ge_quests_daily_assist',
 '_ge_quests_daily_battle_points',
 '_ge_quests_daily_defend_points',
 '_ge_quests_daily_experience',
 '_ge_quests_daily_gain_medals',
 '_ge_quests_daily_gain_sector',
 '_ge_quests_daily_kill_plane_object',
 '_ge_quests_daily_kill_plane',
 '_ge_quests_daily_top']), instances=[(QuestObject, {})])