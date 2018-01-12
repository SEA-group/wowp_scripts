# Embedded file name: scripts/client/adapters/IAwardsListAdapter.py
from DefaultAdapter import DefaultAdapter
from GameEvents.features.achievements.model import AchievementModel

class IAwardsListAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        ob = {'achievements': [ item.id for item in AchievementModel.filter(type='achievement') ]}
        return ob