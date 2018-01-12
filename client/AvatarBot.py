# Embedded file name: scripts/client/AvatarBot.py
from debug_utils import LOG_DEBUG_DEV
from Avatar import Avatar
import BigWorld
from config_consts import IS_DEVELOPMENT
from consts import DEFENDER_TYPE, TEAM_ID
from HelperFunctions import enumToString
try:
    if __debug__ and IS_DEVELOPMENT:
        import sys
        from os.path import dirname, join
        cd = dirname(__file__)
        sys.path.append(join(cd, '..', 'server_common', 'Bot'))
        sys.path.append(join(cd, '..', 'server_common', 'Bot', 'Agent', 'DecisionSystem'))
        from AIStateMachineData import AIState
        from BotConsts import BOTS_DEVELOPMENT_MODE, COMBAT_MODE, STRATEGY_TARGET_TYPE
    else:
        raise
except:
    BOTS_DEVELOPMENT_MODE = False

    class COMBAT_MODE:
        pass


    class STRATEGY_TARGET_TYPE:
        pass


    class AIState:

        def __getattr__(self, key):
            return 0

        def getStateName(self, *kargs, **kwargs):
            pass


class AvatarBot(Avatar):
    _DEBUG = False
    _ENTITIES = []

    @property
    def isDefender(self):
        """Indicates if bot is defender or just regular bot
        @rtype: bool
        """
        return bool(self.defendSector)

    @staticmethod
    def setDebug(value):
        LOG_DEBUG_DEV('AvatarBot.setDebug', value)
        AvatarBot._DEBUG = value
        if not AvatarBot._DEBUG:
            for e in AvatarBot._ENTITIES:
                AvatarBot.clearDebugInfo(e)

    def onEnterWorld(self, prereqs):
        Avatar.onEnterWorld(self, prereqs)
        AvatarBot._ENTITIES.append(self)
        if not BOTS_DEVELOPMENT_MODE:
            return
        else:
            self.__updateDebugCallBack = None
            self.__updateDebug()
            return

    def onLeaveWorld(self):
        Avatar.onLeaveWorld(self)
        AvatarBot._ENTITIES.remove(self)
        if not BOTS_DEVELOPMENT_MODE:
            return
        elif self.__updateDebugCallBack is None:
            return
        else:
            BigWorld.cancelCallback(self.__updateDebugCallBack)
            self.__updateDebugCallBack = None
            AvatarBot.clearDebugInfo(self)
            return

    @staticmethod
    def clearDebugInfo(self):
        BigWorld.clearGroup('targetLine_' + str(self.id))
        BigWorld.clearGroup('movementLine_' + str(self.id))

    def __updateDebug(self):
        self.__updateDebugCallBack = BigWorld.callback(0.001, self.__updateDebug)
        AvatarBot.clearDebugInfo(self)
        if not self._DEBUG:
            return
        AvatarBot.renderDebugLines(self)

    @staticmethod
    def renderDebugLines(self):
        BigWorld.clearGroup('targetLine_' + str(self.id))
        BigWorld.clearGroup('movementLine_' + str(self.id))
        if hasattr(self, 'targetPoint') and self.targetPoint and self.targetPoint.length > 0:
            colors = {AIState.inState(self.AIState, AIState.ATTACK): 4294901760L,
             AIState.inState(self.AIState, AIState.IDLE): 4278190335L,
             AIState.inState(self.AIState, AIState.SURVIVE): 4278255360L}
            BigWorld.addDrawLine('targetLine_' + str(self.id), self.position, self.targetPoint, colors.get(True, 4294967295L), 2)
        if hasattr(self, 'movementDirection') and self.movementDirection and self.movementDirection.length > 0:
            BigWorld.addDrawLine('movementLine_' + str(self.id), self.position, self.position + self.movementDirection * 50, 4294967040L, 2)
        if hasattr(self, 'movePoint') and self.movePoint and self.movePoint.length > 0:
            BigWorld.addDrawLine('movementLine_' + str(self.id), self.position, self.movePoint, 4278255360L, 2)
        if hasattr(self, 'navigationPathData') and self.navigationPathData:
            AvatarBot.debugDrawSpline(self, self.navigationPathData)
        if hasattr(self, 'subTargetPoint') and self.subTargetPoint:
            AvatarBot.debugDrawDottedLine(self, self.position, self.subTargetPoint)
        if hasattr(self, 'strategyTargetPosition') and self.strategyTargetPosition is not None:
            BigWorld.addDrawLine('movementLine_' + str(self.id), self.position, self.strategyTargetPosition, 4294941183L, 2)
        return

    @staticmethod
    def debugDrawSpline(self, data):
        for A, B in zip(data[:-1], data[1:]):
            BigWorld.addDrawLine('movementLine_{}'.format(self.id), A, B, 1996554018, True)

    @staticmethod
    def debugDrawDottedLine(self, start, end, size = 1, space = 0.3):
        """
        :type start: Vector3
        :type end: Vector3
        """
        length = (end - start).length
        direction = (end - start).getNormalized()
        for i in xrange(int(length / (size + space)) - 1):
            A = start + direction * i * (size + space)
            B = A + direction * size
            BigWorld.addDrawLine('movementLine_{}'.format(self.id), A, B, 124780544, False)

    def getDebugInfo(self):
        data = Avatar.getDebugInfo(self)

        def safeAppend(attrName, prettyPrint = None):
            if hasattr(self, attrName):
                data.append((attrName, getattr(self, attrName) if prettyPrint is None else prettyPrint(getattr(self, attrName))))
            return

        safeAppend('AIState', prettyPrint=lambda x: AIState.getStateName(x))
        safeAppend('profile')
        if hasattr(self, 'defendSector') and getattr(self, 'defendSector'):
            safeAppend('defenderType', prettyPrint=lambda x: enumToString(DEFENDER_TYPE, x))
            safeAppend('isPatrolLeader', prettyPrint=bool)
        else:
            safeAppend('strategyTargetType', prettyPrint=lambda x: enumToString(STRATEGY_TARGET_TYPE, x))
            safeAppend('combatMode', prettyPrint=lambda x: enumToString(COMBAT_MODE, x))
            safeAppend('bombsCount')
            safeAppend('rocketsCount')
        return data

    def getDebugMarkerCaption(self):
        botType = 'Defender' if self.isDefender else 'Bot'
        healthText = '{health}/{maxHealth}'.format(health=int(self.health), maxHealth=int(self.maxHealth))
        if self.teamIndex == BigWorld.player().teamIndex:
            return '\\c0000FFCC; Friendly {botType}\n {id}\n{health}'.format(id=self.id, botType=botType, health=healthText)
        elif self.teamIndex == TEAM_ID.TEAM_2:
            return '\\cAA9900CC; Neutral {botType}\n {id}\n{health}'.format(id=self.id, botType=botType, health=healthText)
        else:
            return '\\cFF0000CC; Enemy {botType}\n {id}\n{health}'.format(id=self.id, botType=botType, health=healthText)