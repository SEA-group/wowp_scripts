# Embedded file name: scripts/common/BWUserTypesCommon/ConsumableRecord.py
from FixedDictWrapper import FixedDictWrapper, FDMemberProxy

class ConsumableRecord(FixedDictWrapper):
    """Consumable record on Avatar
    """
    id = FDMemberProxy('key')
    chargesCount = FDMemberProxy('chargesCount')
    coolDownTill = FDMemberProxy('coolDownTill')
    activeTill = FDMemberProxy('activeTill')
    pendingCoolDown = FDMemberProxy('pendingCoolDown')
    EMPTY_MARKER = -1
    INFINITE_CHARGES_COUNT = -1

    @classmethod
    def create(cls, id_, chargesCount, coolDownTill = EMPTY_MARKER, activeTill = EMPTY_MARKER, pendingCoolDown = EMPTY_MARKER):
        fixedDict = {'key': id_,
         'chargesCount': chargesCount,
         'coolDownTill': coolDownTill,
         'activeTill': activeTill,
         'pendingCoolDown': pendingCoolDown}
        return cls(fixedDict)

    @property
    def key(self):
        """Compatibility field. Consumable id or -1 for empty slot
        :rtype: int 
        """
        return self.id

    @property
    def isCoolDownInProgress(self):
        """Flag indicating that cooldown is in progress
        :rtype: bool
        """
        return self.coolDownTill != self.EMPTY_MARKER

    @property
    def isActivated(self):
        """Flag indicating that consumable is activated now
        :rtype: bool
        """
        return self.activeTill != self.EMPTY_MARKER

    @property
    def hasAvailableCharges(self):
        """Flag indicating that consumable has available charges
        :rtype: bool
        """
        return self.chargesCount > 0 or self.chargesCount == self.INFINITE_CHARGES_COUNT

    @property
    def hasPendingCoolDown(self):
        """Flag indicating that consumable has active charges
        :rtype: bool
        """
        return self.pendingCoolDown != self.EMPTY_MARKER

    @property
    def isReadyToUse(self):
        """Flag indicating that consumable can be used
        :rtype: bool
        """
        return self.hasAvailableCharges and not self.isCoolDownInProgress and not self.hasPendingCoolDown and not self.isActivated

    def pauseCoolDown(self, currentTime):
        """Pause current consumable cooldown (for example, on avatar death)
        :param currentTime: Current timestamp value
        """
        raise self.isCoolDownInProgress or AssertionError('Failed to pause cooldown for {0}'.format(self))
        self.pendingCoolDown = self.coolDownTill - currentTime
        self.coolDownTill = self.EMPTY_MARKER

    def resumeCoolDown(self, currentTime):
        """Resume pending cooldown (for example after avatar respawn)
        :param currentTime: Current timestamp value
        """
        raise self.pendingCoolDown != self.EMPTY_MARKER or AssertionError('Failed to resume cooldown for {0}'.format(self))
        self.coolDownTill = currentTime + self.pendingCoolDown
        self.pendingCoolDown = self.EMPTY_MARKER

    def clearCoolDown(self):
        """Clear current cooldown for consumable
        """
        self.coolDownTill = self.EMPTY_MARKER

    def clearActivation(self):
        """Clear consumable activation
        """
        self.activeTill = self.EMPTY_MARKER

    def __getitem__(self, item):
        """Dictionary protocol is implemented for compatibility with old code
        """
        return self.fixedDict.__getitem__(item)

    def __setitem__(self, key, value):
        """Dictionary protocol is implemented for compatibility with old code
        """
        self.fixedDict.__setitem__(key, value)

    def __repr__(self):
        return '<{0}: id={1}, chargesCount={2}, coolDownTill={3}, activeTill={4}, pendingCoolDown={5}>'.format(self.__class__.__name__, self.id, self.chargesCount, self.coolDownTill, self.activeTill, self.pendingCoolDown)


class ConsumableRecordConverter(object):
    """Fixed-Dict converter for ConsumableRecord type
    """

    def getDictFromObj(self, obj):
        """Convert ConsumableRecord to dict representation
        :type obj: ConsumableRecord
        :rtype: dict
        """
        return obj.fixedDict

    def createObjFromDict(self, dict_):
        """Convert FIXED_DICT to ConsumableRecord
        @type dict_: dict
        @rtype: ConsumableRecord
        """
        return ConsumableRecord(dict_)

    def isSameType(self, obj):
        return isinstance(obj, ConsumableRecord)


instance = ConsumableRecordConverter()