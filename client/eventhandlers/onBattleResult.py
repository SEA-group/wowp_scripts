# Embedded file name: scripts/client/eventhandlers/onBattleResult.py
import BigWorld
from exchangeapi.AdapterUtils import getAdapter
from exchangeapi.ErrorCodes import SUCCESS
from consts import EMPTY_IDTYPELIST

def onBattleResultShort(event):
    player = BigWorld.player()
    for team in event.ob['teams'].itervalues():
        for member in team.itervalues():
            if member['id'] == event.ob['playerID']:
                for planeStats in member['planes']:
                    player.responseSender([[planeStats['planeID'], 'plane']], 'IExperience', {}, SUCCESS)

                break

    getAdapter('IBattleResultShort', [event.idTypeList[0][1]]).add(None, None, event.ob, reportID=event.idTypeList[0][0])
    return


def onSessionBattleResults(event):
    getAdapter('ISessionBattleResults', ['account']).edit(None, None, EMPTY_IDTYPELIST, event.idTypeList[0][0], reportID=None)
    return