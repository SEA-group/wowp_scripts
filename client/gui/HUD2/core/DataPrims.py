# Embedded file name: scripts/client/gui/HUD2/core/DataPrims.py
from debug_utils import LOG_WARNING

class DataSource:

    def dispose(self):
        LOG_WARNING('Datasource.dispose() not implemented in ', self.__class__.__name__)


class DataController:
    pass