# Embedded file name: scripts/client/GameEvents/features/tutorial/model.py
from __future__ import absolute_import
from GameEventsCommon.db.backends import BundledBackend
from GameEventsCommon.db.model import Model
from GameEvents.model import GameEventObject

class TutorialObject(GameEventObject):

    @property
    def params(self):
        order = 1
        if getattr(self._attrs, 'parent', None):
            try:
                order = int(getattr(self._attrs, 'name', 1))
            except ValueError:
                pass

        client = getattr(self._attrs, 'client', None)
        order = getattr(client, 'order', order)
        return {'order': order,
         'tooltip': self.localized.tooltip}


TutorialModel = Model(backend=BundledBackend(modules=['_ge_tutorial_new', '_ge_tutorial_old']), instances=[(TutorialObject, {})])