# Embedded file name: scripts/client/eventhandlers/onRepair.py
import BWPersonality
from functools import partial

def onRepair(event):
    planeID = next((iD for iD, typ in event.idTypeList if typ == 'plane'), None)
    if event.prevob and event.ob['curHealth'] != event.prevob['curHealth']:
        lch = BWPersonality.g_lobbyCarouselHelper
        lch.updateCarouselAirplane(planeID, partial(lambda carousel, planeID: carousel.onGetUpgradesList(callbacksList=[partial(lch.updateInBattleButton, True)]), lch), False, True, False)
    return