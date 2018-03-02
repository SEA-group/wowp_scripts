# Embedded file name: scripts/client/gui/HUD2/core/DataPrims.py
from debug_utils import LOG_WARNING
from gui.HUD2.HUDExecutionManager import HUDExecutionManager

class DataSource:

    def regicToExecutionManager(self):
        HUDExecutionManager.instance.regicClass(self)

    def unregicFromExecutionManager(self):
        HUDExecutionManager.instance.unregicClass(self)

    def dispose(self):
        LOG_WARNING('Datasource.dispose() not implemented in ', self.__class__.__name__)


class DataController:
    pass