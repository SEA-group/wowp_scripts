# Embedded file name: scripts/common/ComponentModel/AIComponents.py
import sys
import inspect
import BigWorld
from consts import IS_EDITOR
if IS_EDITOR:
    import db.DBLogic
    from os.path import dirname, join
    cd = dirname(__file__)
    sys.path.append(join(cd, '..', '..', 'server_common'))
from EntityHelpers import isAvatarBot, isSector
from Component import Component, InputSlot, OutputSlot
from ComponentLoggingHelpers import logEntityDoesNotExistError, logNotSupportedEntityError, logError

class SetStrategyTargetAsPoint(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'AI'

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, SetStrategyTargetAsPoint._execute),
         InputSlot('bot_entity', Component.SLOT_ENTITY, None),
         InputSlot('position', Component.SLOT_VECTOR3, None),
         OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, entityId, position):
        from Bot.BotConsts import STRATEGY_TARGET_TYPE, StrategyTargetPointData
        e = BigWorld.entities.get(entityId)
        if e is None:
            logEntityDoesNotExistError(entityId, self)
            return
        elif not isAvatarBot(e):
            logNotSupportedEntityError(e, self)
            return
        else:
            e.updateStrategyTarget(STRATEGY_TARGET_TYPE.POINT, StrategyTargetPointData(position))
            return 'out'


class SetStrategyTargetAsSector(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'AI'

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, SetStrategyTargetAsSector._execute),
         InputSlot('bot_entity', Component.SLOT_ENTITY, None),
         InputSlot('sector_entity', Component.SLOT_ENTITY, None),
         OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, entityId, sectorId):
        from Bot.BotConsts import STRATEGY_TARGET_TYPE, StrategyTargetSectorData
        e = BigWorld.entities.get(entityId)
        s = BigWorld.entities.get(sectorId)
        if e is None:
            logEntityDoesNotExistError(entityId, self)
            return
        elif s is None:
            logEntityDoesNotExistError(sectorId, self)
            return
        elif not isAvatarBot(e):
            logNotSupportedEntityError(e, self)
            return
        elif not isSector(s):
            logNotSupportedEntityError(s, self)
            return
        else:
            e.updateStrategyTarget(STRATEGY_TARGET_TYPE.SECTOR, StrategyTargetSectorData(position=s.position, sectorID=s.ident, sectorEntityID=sectorId))
            return 'out'


class SetStrategyTargetAsEntity(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'AI'

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, SetStrategyTargetAsEntity._execute),
         InputSlot('bot_entity', Component.SLOT_ENTITY, None),
         InputSlot('target_entity', Component.SLOT_ENTITY, None),
         OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, entityId, targetId):
        from Bot.BotConsts import STRATEGY_TARGET_TYPE, StrategyTargetEntityData
        e = BigWorld.entities.get(entityId)
        t = BigWorld.entities.get(targetId)
        if e is None:
            logEntityDoesNotExistError(entityId, self)
            return
        elif t is None:
            logEntityDoesNotExistError(targetId, self)
            return
        elif not isAvatarBot(e):
            logNotSupportedEntityError(e, self)
            return
        else:
            e.updateStrategyTarget(STRATEGY_TARGET_TYPE.ENTITY, StrategyTargetEntityData(position=t.position, entityID=targetId))
            return 'out'


class SetStrategyTargetAsAirStrikeWave(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'AI'

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, SetStrategyTargetAsAirStrikeWave._execute),
         InputSlot('bot_entity', Component.SLOT_ENTITY, None),
         InputSlot('position', Component.SLOT_VECTOR3, None),
         InputSlot('air_strike_wave_id', Component.SLOT_STR, None),
         OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, entityId, position, waveId):
        from Bot.BotConsts import STRATEGY_TARGET_TYPE, StrategyTargetAirStrikeData
        e = BigWorld.entities.get(entityId)
        if e is None:
            logEntityDoesNotExistError(entityId, self)
            return
        elif not isAvatarBot(e):
            logNotSupportedEntityError(e, self)
            return
        else:
            e.updateStrategyTarget(STRATEGY_TARGET_TYPE.AIR_STRIKE, StrategyTargetAirStrikeData(position=position, waveID=waveId))
            return 'out'


class SectorBotFocusCount(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'AI'

    def slotDefinitions(self):
        return [InputSlot('sector', Component.SLOT_ENTITY, None), InputSlot('team_id', Component.SLOT_TEAM_ID, None), OutputSlot('res', Component.SLOT_INT, SectorBotFocusCount._execute)]

    def _execute(self, sectorId, teamId):
        s = BigWorld.entities.get(sectorId)
        if s is None:
            logEntityDoesNotExistError(sectorId, self)
            return 0
        elif 0 <= teamId < len(s.botFocusCount):
            return s.botFocusCount[teamId]
        else:
            logError(self, 'Input team id is invalid')
            return 0


class AirStrikeWaveBotFocusCount(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'AI'

    def slotDefinitions(self):
        return [InputSlot('air_strike_wave_id', Component.SLOT_STR, None), InputSlot('team_id', Component.SLOT_TEAM_ID, None), OutputSlot('res', Component.SLOT_INT, AirStrikeWaveBotFocusCount._execute)]

    def _execute(self, waveId, teamId):
        from CellEntityHelpers import getGameActionsManager
        mgr = getGameActionsManager(self)
        if mgr is None:
            return 0
        else:
            return mgr.getASWaveBotFocusCount(teamId, waveId)


def getModuleComponents():
    return list((value for key, value in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(value, Component) and value is not Component))