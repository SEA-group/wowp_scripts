# Embedded file name: scripts/common/GameEventsCommon/helpers/bigworld.py


def isNotRealEntity(entity):
    """Checks entity is real or mailbox"""
    return entity.__class__.__name__ == 'BaseEntityMailBox'