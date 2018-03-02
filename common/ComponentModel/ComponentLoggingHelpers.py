# Embedded file name: scripts/common/ComponentModel/ComponentLoggingHelpers.py
from debug_utils import LOG_ERROR

def logError(component, message):
    LOG_ERROR('[VSE][{}] {}'.format(component.__class__.__name__, message))


def logNotSupportedEntityError(e, component):
    logError(component, 'This type of entity is not supported: {}'.format(e.className))


def logEntityDoesNotExistError(entityId, component):
    logError(component, 'Entity does not exist: {}'.format(entityId))