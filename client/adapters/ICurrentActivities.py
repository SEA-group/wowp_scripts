# Embedded file name: scripts/client/adapters/ICurrentActivities.py
from adapters.DefaultAdapter import DefaultAdapter
from gui.WindowsManager import g_windowsManager
from Helpers.cache import getFromCache
from consts import EMPTY_IDTYPELIST
import BigWorld

class ICurrentActivitiesAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        ob = super(ICurrentActivitiesAdapter, self).__call__(account, ob, **kw)
        if ob is None:
            ob = {}
        ob.setdefault('activities', {})
        iface = 'IActivities'
        obAll = getFromCache(EMPTY_IDTYPELIST, iface)
        if not obAll:
            accountUI = g_windowsManager.getAccountUI()
            accountUI.viewIFace([[{iface: {}}, EMPTY_IDTYPELIST]])
            return
        else:
            player = BigWorld.player()
            if not player:
                return ob
            ob['activities'] = player.activities.currentActivities
            return ob

    def view(self, account, requestID, idTypeList, ob = None, **kw):
        return super(ICurrentActivitiesAdapter, self).view(account, requestID, idTypeList, ob, **kw)

    def edit(self, account, requestID, idTypeList, data, ob = None, **kw):
        self.view(account, requestID, idTypeList, None, **kw)
        return