# Embedded file name: scripts/client/gui/HUD2/features/FastCommands/FastCommandSource.py
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.features.FastCommands.FastCommandManager import FastCommandManager
from gui.HUD2.hudFeatures import Feature

class FastCommandSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).fastCommand
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._db = features.require(Feature.DB_LOGIC)
        self._cfg = self._db.getFastCommands()
        captureRadiusIntentionsKoef = self._cfg.intentions.captureRadiusKoef
        captureRadiusKoefPlanes = self._cfg.offenseDefense.captureRadiusKoef
        self._model.sector.radiusCoef = captureRadiusIntentionsKoef
        self._model.plane.radiusCoef = captureRadiusKoefPlanes
        self._fastCommandManager = FastCommandManager(features, self._model)

    def dispose(self):
        self._fastCommandManager.dispose()
        self._db = None
        self._cfg = None
        self._fastCommandManager = None
        self._model = None
        self._clientArena = None
        return