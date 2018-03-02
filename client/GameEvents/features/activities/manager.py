# Embedded file name: scripts/client/GameEvents/features/activities/manager.py
from gui.WindowsManager import g_windowsManager
from consts import EMPTY_IDTYPELIST
import time
ACTIVITY_KEY = ('start', 'end', 'vse', 'ui')

class ActivitiesManager(object):

    def __init__(self, account):
        self.__account = account
        self.__activities = {}
        self.__currentActivities = {}

    def destroy(self):
        self.__account = None
        self.__activities = None
        return

    @property
    def currentActivities(self):
        return self.__currentActivities

    @property
    def activities(self):
        return self.__activities

    def onSecondTimer(self):
        if not (self.__account and (self.__activities or self.__currentActivities)):
            return
        self._updateActivities(self.__activities)

    def onUpdateActivities(self, activities):
        self._updateActivities(activities)

    def getCurrentActivities(self, allActivities, currentTime = None):
        if currentTime is None:
            currentTime = time.time()
        tree, name = self._getCurrentActivityTreeNames(allActivities, currentTime)
        return tree or name or {}

    def _updateActivities(self, activities):
        currentTime = self.__account.currentTime - self.__account.deltaTimeClientServer
        newCurActivities = self.getCurrentActivities(activities, currentTime)
        oldCurrActivities = self.__currentActivities
        expiredAct = self._getNewStages(oldCurrActivities, newCurActivities)
        newAct = self._getNewStages(newCurActivities, oldCurrActivities)
        self._processVSEActivities('end', expiredAct, self.__activities)
        self._processVSEActivities('start', newAct, activities)
        self.__activities = activities
        self.__currentActivities = newCurActivities
        if expiredAct or newAct:
            self._updateICurrentActivities()

    def _getNewStages(self, newStage, oldStage):
        ret = {}
        for name, v in newStage.iteritems():
            if name in oldStage:
                for group, stage in v.iteritems():
                    if group not in oldStage[name] or stage != oldStage[name][group]:
                        ret.setdefault(name, {})[group] = stage

            else:
                ret[name] = v

        return ret

    def _processVSEActivities(self, vseType, currActivities, allActivities):

        def subTreeCallVSE(currActiveSubTree, allActiveSubTree):
            if not currActiveSubTree:
                return
            else:
                if type(currActiveSubTree) is dict:
                    for name, v in currActiveSubTree.iteritems():
                        subTreeCallVSE(v, allActiveSubTree[name])

                else:
                    vseAction = allActiveSubTree[currActiveSubTree].get('vse', {}).get(vseType, {})
                    if vseAction:
                        vseScript = vseAction.get('script', None)
                        if vseScript:
                            self.__account.callVSE(vseScript, vseAction['params'])
                return

        subTreeCallVSE(currActivities, allActivities)

    def _updateICurrentActivities(self):
        accountUI = g_windowsManager.getAccountUI()
        accountUI.editIFace([[{'ICurrentActivities': {}}, EMPTY_IDTYPELIST]])

    def _getSubActivities(self, activities):
        subActiveNames = []
        for name in activities:
            if name not in ACTIVITY_KEY:
                subActiveNames.append(name)

        return subActiveNames

    def _getCurrentActivityTreeNames(self, activities, currentTime):
        tree = {}
        for name, activityData in activities.iteritems():
            if name not in ACTIVITY_KEY:
                subActivityNames = self._getSubActivities(activityData)
                if subActivityNames:
                    activeTree, activeName = self._getCurrentActivityTreeNames(activityData, currentTime)
                    if activeTree or activeName:
                        tree[name] = activeTree or activeName
                elif activityData['start'] <= currentTime < activityData['end']:
                    return ({}, name)

        return (tree, '')