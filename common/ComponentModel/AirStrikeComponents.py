# Embedded file name: scripts/common/ComponentModel/AirStrikeComponents.py
import sys
import inspect
import BigWorld
from Component import Component, InputSlot, OutputSlot, ArrayConnection
from consts import TEAM_ID, IS_CELLAPP
if IS_CELLAPP:
    import CellEntityHelpers

class AirStrikeWavesInBattle(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'AirStrike'

    @classmethod
    def arrayConnections(cls):
        return [ArrayConnection('Destination', Component.SLOT_STR)]

    def slotDefinitions(self):
        return [InputSlot('in', Component.SLOT_EVENT, AirStrikeWavesInBattle._execute), OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, dst):
        del dst[:]
        manager = CellEntityHelpers.getGameActionsManager(self)
        if manager is None:
            return
        else:
            dst.extend((wave['waveID'] for wave in manager.activeASWaves))
            return 'out'


class AirStrikePlanesByWaveId(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'AirStrike'

    @classmethod
    def arrayConnections(cls):
        return [ArrayConnection('Destination', Component.SLOT_ENTITY)]

    def slotDefinitions(self):
        return [InputSlot('in', Component.SLOT_EVENT, AirStrikePlanesByWaveId._execute), InputSlot('air_strike_wave_id', Component.SLOT_STR, None), OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, dst, air_strike_wave_id):
        del dst[:]
        manager = CellEntityHelpers.getGameActionsManager(self)
        if manager is None:
            return
        else:
            wave = manager.getWaveByID(air_strike_wave_id)
            if wave is None:
                return
            dst.extend((bomberRecord['id'] for bomberRecord in wave['bomberIDsStates'] if bool(BigWorld.entities.get(bomberRecord['id']))))
            return 'out'


class AirStrikeTeamId(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'AirStrike'

    def slotDefinitions(self):
        return [InputSlot('air_strike_wave_id', Component.SLOT_STR, None), OutputSlot('res', Component.SLOT_TEAM_ID, AirStrikeTeamId._execute)]

    def _execute(self, air_strike_wave_id):
        manager = CellEntityHelpers.getGameActionsManager(self)
        if manager is None:
            return TEAM_ID.UNDEFINED
        else:
            wave = manager.getWaveByID(air_strike_wave_id)
            if wave is None:
                return TEAM_ID.UNDEFINED
            return wave['teamIndex']


def getModuleComponents():
    return list((value for key, value in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(value, Component) and value is not Component))