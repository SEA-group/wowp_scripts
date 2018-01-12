# Embedded file name: scripts/client/clientEconomics/ClientDamageProcessor.py
import BigWorld
import EntityHelpers
import db.DBLogic
from Event import Event
from economics.EconomicsConfigParser import REWARD_FIELD, PARAMS_FIELD, ID_FIELD, PREDICATES_FIELD, PROGRESS_STEP_FIELD
from economics.DamageHelpers import getRewardableProgress
from GameModeSettings.ACSettings import GROUND_OBJECT_TYPE
from debug_utils import LOG_WARNING

class ClientDamageProcessor(object):
    ATTACK_TIMEOUT = 3.5

    def __init__(self, config, gameEnvironment):
        self.PREDICATES = {'teammate': self._teammatePredicate,
         'type': self._typePredicate,
         'ACType': self._acTypePredicate}
        params = config[PARAMS_FIELD]
        self._reward = params[REWARD_FIELD]
        self._eventId = params[ID_FIELD]
        self._progressStep = params[PROGRESS_STEP_FIELD]
        self.eDamage = Event()
        self._gameEnvironment = gameEnvironment
        self._linkEvents(gameEnvironment)
        self._avatarsDamageRemainders = dict()
        self._currentTarget = 0
        self._targetWithAccumulatedDamage = 0
        self._targetAccumulator = 0
        self._createPredicates(params)

    def _createPredicates(self, config):
        self._predicates = []
        predicates = config[PREDICATES_FIELD]
        if predicates is not None:
            for pId in predicates:
                self._predicates.append((self.PREDICATES[pId], predicates[pId]))

        return

    def _processDamage(self, avatarId, health, lastDamagerId, oldHealth, maxHealth):
        damage = oldHealth - health
        if not (lastDamagerId == BigWorld.player().id and all((predicate(avatarId, result) for predicate, result in self._predicates))) or damage <= 0:
            return
        nowTime = BigWorld.time()
        savedTargetDamageInfo = self._avatarsDamageRemainders.get(avatarId, (0, nowTime))
        accumulatedDamage = damage + savedTargetDamageInfo[0]
        amount, reminder = getRewardableProgress(accumulatedDamage, maxHealth, self._progressStep)
        isAccumulatorTimeout = nowTime - savedTargetDamageInfo[1] > ClientDamageProcessor.ATTACK_TIMEOUT
        self._avatarsDamageRemainders[avatarId] = (reminder, nowTime)
        if not avatarId == self._currentTarget or isAccumulatorTimeout:
            self._currentTarget = avatarId
            self._targetAccumulator = 0
        reward = int(amount * self._reward)
        if reward != 0:
            self._targetAccumulator += reward
            accumulatorResetted = self._currentTarget != self._targetWithAccumulatedDamage or isAccumulatorTimeout
            self._targetWithAccumulatedDamage = self._currentTarget
            self.eDamage(self._eventId, reward, self._targetAccumulator, accumulatorResetted)
        elif isAccumulatorTimeout:
            self._targetWithAccumulatedDamage = 0

    def destroy(self):
        self._unlinkEvents(self._gameEnvironment)
        self._gameEnvironment = None
        self._avatarsDamageRemainders = None
        self.eDamage.clear()
        self.eDamage = None
        self.PREDICATES.clear()
        self._predicates = []
        return

    def _linkEvents(self, gameEnvironment):
        gameEnvironment.eAvatarAdded += self._onAvatarAdded
        gameEnvironment.eAvatarRemoved += self._onAvatarRemoved

    def _unlinkEvents(self, gameEnvironment):
        gameEnvironment.eAvatarAdded -= self._onAvatarAdded
        gameEnvironment.eAvatarRemoved -= self._onAvatarRemoved

    def _onAvatarAdded(self, avatar):
        avatar.eHealthChanged += self._processDamage

    def _onAvatarRemoved(self, avatar, isLeaveWorld):
        if isLeaveWorld:
            avatar.eHealthChanged -= self._processDamage

    def _teammatePredicate(self, victimEntityID, needRes):
        entity = BigWorld.entities.get(victimEntityID, None)
        if not entity:
            LOG_WARNING('ECO: _teammatePredicate: entity not found')
            return False
        else:
            player = BigWorld.player()
            return needRes == (player.teamIndex == entity.teamIndex)

    def _typePredicate(self, entityId, neededType):
        result = None
        entity = BigWorld.entities.get(entityId)
        if EntityHelpers.isTeamObject(entity):
            result = 'GroundObject'
        elif EntityHelpers.isPlayerAvatar(entity):
            result = 'Player'
        elif EntityHelpers.isAvatarBot(entity):
            clientArena = self._gameEnvironment.service('ClientArena')
            info = clientArena.getAvatarInfo(entityId)
            isDefender = info.get('defendSector')
            if bool(isDefender):
                result = 'Defender'
            elif bool(info.get('isBomber')):
                result = 'Bomber'
            else:
                result = 'Player'
        return result == neededType

    def _acTypePredicate(self, entityId, validTypes):
        clientArena = self._gameEnvironment.service('ClientArena')
        objectData = clientArena.allObjectsData[entityId]
        if 'ACType' not in objectData:
            return False
        try:
            typeName = GROUND_OBJECT_TYPE.getName(objectData['ACType'])
        except ValueError:
            return False

        validTypes = validTypes.split('|')
        return typeName in validTypes