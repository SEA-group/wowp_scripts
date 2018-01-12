# Embedded file name: scripts/client/adapters/IAchieveGroupsAdapter.py
from DefaultAdapter import DefaultAdapter
import _ge_achievements_settings as settings

class IAchieveGroupsAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        ob = super(IAchieveGroupsAdapter, self).__call__(account, ob, **kw)
        ob['groups'] = [ {'name': group.name,
         'order': group.order,
         'locale': group.locale} for group in settings.DB.achievements.client.group ]
        return ob