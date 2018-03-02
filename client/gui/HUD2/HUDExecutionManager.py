# Embedded file name: scripts/client/gui/HUD2/HUDExecutionManager.py
from ExecutionManager import ExecutionManager, RegicToExecutionManager

class HUDExecutionManager(ExecutionManager):
    pass


class RegicToHUDExecutionManager(RegicToExecutionManager):
    ManagerClass = HUDExecutionManager

    def dispose(self):
        self.unregicClass()