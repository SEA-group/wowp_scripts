# Embedded file name: scripts/client/gui/HUD2/features/PlaneScheme/PlaneSchemeSource.py
import db.DBLogic
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class PlaneSchemeSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).planeScheme
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._clientArena.onNewAvatarsInfo += self._setupModel
        self._playerAvatar.eRespawn += self._onClean
        self._playerAvatar.eTacticalSpectator += self._onClean
        self._groupDependency = {}
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        return

    @property
    def _planeSettings(self):
        return self._playerAvatar.settings.airplane

    @property
    def _schemeData(self):
        d = db.DBLogic.g_instance
        return d.getHudPlaneSchemeByName(self._planeSettings.visualSettings.hudPlaneScheme.lower())

    def _setupModel(self, newInfos):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._playerAvatar.ePartStateChanged += self._updatePart
        self._groupDependency = {}
        self._setBase()
        self._updateAllParts()

    def _setBase(self):
        self._model.scheme = self._schemeData.planeScheme

    def _updateAllParts(self):
        from Avatar import AvatarDummyPart
        for partID, stateID in self._playerAvatar.partStates:
            part = AvatarDummyPart(self._planeSettings, partID, stateID)
            self._updatePart(part)

    def _updatePart(self, partData):
        self._checkOnPartDamage(partData)
        self._checkOnGroupDependency(partData)

    def _checkOnPartDamage(self, partData):
        schemePartData = self._schemeData.parts.get(partData.name)
        if schemePartData is not None:
            damage = self._model.damage.first(lambda a: a.partName.get() == partData.name)
            if damage:
                damage.state = partData.stateID
            else:
                self._initDamagePart(partData.name, partData.stateID, schemePartData)
        return

    def _checkOnGroupDependency(self, partData):
        for gName, group in self._schemeData.groups.iteritems():
            if partData.name in group.dependency:
                self._groupDependency.setdefault(gName, {})[partData.name] = partData.stateID
                damageGroup = self._model.damage.first(lambda a: a.partName.get() == gName)
                if damageGroup:
                    damageGroup.state = max(self._groupDependency[gName].values())
                else:
                    self._initDamagePart(gName, partData.stateID, group)

    def _initDamagePart(self, name, state, schemePartData):
        self._model.damage.append(partName=name, state=state, normal=schemePartData.normalState, damage=schemePartData.damageState, crit=schemePartData.critState)

    def _onClean(self, *args, **kwargs):
        self._model.damage.clean()
        self._groupDependency = {}
        self._setBase()
        self._updateAllParts()

    def dispose(self):
        self._playerAvatar.eRespawn -= self._onClean
        self._playerAvatar.eTacticalSpectator -= self._onClean
        self._playerAvatar.ePartStateChanged -= self._updatePart
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._model = None
        self._playerAvatar = None
        self._clientArena = None
        return