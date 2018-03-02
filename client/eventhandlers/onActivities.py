# Embedded file name: scripts/client/eventhandlers/onActivities.py
import BigWorld

def onActivitiesUpdate(event):
    player = BigWorld.player()
    if event.ob and event.ob['activities'] and player:
        player.activities.onUpdateActivities(event.ob['activities'])