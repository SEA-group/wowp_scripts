# Embedded file name: scripts/common/ControllerManager.py
from debug_utils import *
from time import time

class _ControllerManager:

    def __init__(self, profiler = None):
        self.controllers = {}
        self.__orderedControllers = []
        self.profiler = profiler
        self.__freezeControllers = set()

    def _registerController(self, name, controller):
        if controller:
            if name not in self.controllers:
                self.__orderedControllers.append((name, controller))
                self.controllers[name] = controller
            else:
                LOG_ERROR('You are trying to register controller twice', name)
            if self.profiler is not None and name not in self.profiler:
                self.profiler[name] = {'tickCount': 0,
                 'summ': 0,
                 'max': 0}
        return

    def _unregisterController(self, controllerName):
        self.__orderedControllers.remove((controllerName, self.controllers.pop(controllerName)))

    def _destroyControllers(self):
        self.__orderedControllers = []
        for controller in self.controllers.values():
            controller.destroy()

        self.controllers.clear()

    def _onControllersCreated(self):
        for controllerName, controller in self.__orderedControllers:
            controller.onControllersCreated()

    def _restartControllers(self):
        for controllerName, controller in self.__orderedControllers:
            controller.restart()

    def _backupControllers(self):
        data = {}
        for key, controller in self.controllers.items():
            controllerData = controller.backup()
            if controllerData:
                data[key] = controllerData

        freezeData = self.__freezeControllers
        return [data, freezeData]

    def _restoreControllers(self, container):
        for key, controller in self.controllers.items():
            controllerData = container[0].get(key, None)
            if controllerData:
                controller.restore(controllerData)

        self.__freezeControllers = container[1]
        return

    def _updateControllers(self, dt):
        if self.profiler is not None:
            for controllerName, controller in self.__orderedControllers:
                if controllerName not in self.__freezeControllers:
                    t1 = time()
                    controller.update(dt)
                    t2 = time()
                    functionTime = t2 - t1
                    controllerProfile = self.profiler[controllerName]
                    controllerProfile['tickCount'] += 1
                    controllerProfile['summ'] += functionTime
                    controllerProfile['max'] = max(functionTime, controllerProfile['max'])

        elif self.__freezeControllers:
            for controllerName, controller in self.__orderedControllers:
                if controllerName not in self.__freezeControllers:
                    controller.update(dt)

        else:
            for controllerName, controller in self.__orderedControllers:
                controller.update(dt)

        return

    def _update1secControllers(self, dt):
        if self.__freezeControllers:
            for controllerName, controller in self.__orderedControllers:
                if controllerName not in self.__freezeControllers:
                    controller.update1sec(dt)

        else:
            for controllerName, controller in self.__orderedControllers:
                controller.update1sec(dt)

    def _setControllersState(self, stateID, data):
        for controllerName, controller in self.__orderedControllers:
            controller.onParentSetState(stateID, data)

    def _logProfiler(self):
        if self.profiler is not None:
            LOG_NOTE('CLASS - ', type(self))
            LOG_NOTE('CONTROLLERS_INFO average')
            for controllerName, data in self.profiler.items():
                LOG_NOTE('Name ', controllerName, ' time ', data['summ'] / data['tickCount'])

            LOG_NOTE('')
            LOG_NOTE('CONTROLLERS_INFO max')
            for controllerName, data in self.profiler.items():
                LOG_NOTE('Name ', controllerName, ' time %2', data['max'])

        return

    def _freezeControllers(self, controllerName):
        self.__freezeControllers.add(controllerName)

    def _unFreezeControllers(self, controllerName):
        if controllerName in self.__freezeControllers:
            self.__freezeControllers.remove(controllerName)

    def _unFreezeAllControllers(self):
        self.__freezeControllers = set()


ControllerManager = _ControllerManager
from consts import IS_CLIENT
if IS_CLIENT:

    def proxying(func):

        def wrapper(*args, **kwargs):
            raise AttributeError

        return wrapper


    class _ComponentProvider(object):
        """
            cpp interface:  destroyComponents,
                            registerComponent,
                            unregisterComponent,
                            getComponet
        """

        def __init__(self, obj):
            self.__obj = obj
            self.__componentKeys = []

        def dispose(self):
            self.__obj.destroyComponents()
            self.__obj = None
            return

        def registerController(self, name, controller):
            componentID = name
            isSuccess = self.__obj.registerComponent(componentID, controller)
            if isSuccess:
                self.__componentKeys.append(name)
            return isSuccess

        def unregisterController(self, name):
            componentID = name
            isSuccess = self.__obj.unregisterComponent(componentID)
            if isSuccess:
                self.__componentKeys.remove(name)
            return isSuccess

        def get(self, key, default = None):
            componentID = key
            component = self.__obj.getComponet(componentID)
            if component is not None:
                return component
            else:
                return default

        def __getitem__(self, item):
            componentID = item
            component = self.__obj.getComponet(componentID)
            if component is not None:
                return component
            else:
                raise KeyError
                return

        def __iter__(self):
            for attr in self.__componentKeys:
                yield attr


    class ControllerManagerProxy(_ControllerManager):

        def __init__(self, *args, **kwargs):
            _ControllerManager.__init__(self, *args, **kwargs)
            self.controllers = _ComponentProvider(self)

        def _registerController(self, name, controller):
            if controller:
                if not self.controllers.registerController(name, controller):
                    LOG_ERROR('You are trying to register controller twice', name)

        def _unregisterController(self, name):
            if not self.controllers.unregisterController(name):
                LOG_ERROR('You are trying to unregister unknown controller', name)

        def _destroyControllers(self):
            self.controllers.dispose()

        @proxying
        def _onControllersCreated(self):
            pass

        @proxying
        def _restartControllers(self):
            pass

        @proxying
        def _backupControllers(self):
            pass

        @proxying
        def _restoreControllers(self, container):
            pass

        @proxying
        def _updateControllers(self, dt):
            pass

        @proxying
        def _update1secControllers(self, dt):
            pass

        @proxying
        def _setControllersState(self, stateID, data):
            pass

        @proxying
        def _logProfiler(self):
            pass

        @proxying
        def _freezeControllers(self, controllerName):
            pass

        @proxying
        def _unFreezeControllers(self, controllerName):
            pass

        @proxying
        def _unFreezeAllControllers(self):
            pass


    ControllerManager = ControllerManagerProxy