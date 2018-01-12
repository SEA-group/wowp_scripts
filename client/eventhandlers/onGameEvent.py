# Embedded file name: scripts/client/eventhandlers/onGameEvent.py
import BWLogging
logger = BWLogging.getLogger(__name__)

def onGameEvent(event):
    logger.debug('Game event received: {0}'.format(event.ob))