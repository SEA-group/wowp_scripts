# Embedded file name: scripts/client/gui/Scaleform/WebBrowser2.py
import BigWorld
import GlobalEvents
import BWLogging
import weakref
import Keys
import urlparse
from collections import namedtuple
from Event import Event, EventManager
from debug_utils import LOG_CURRENT_EXCEPTION
from config_consts import IS_DEVELOPMENT
_BROWSER_LOGGING = True
_BROWSER_KEY_LOGGING = False
_DEFAULT_BROWSER_ID = 0
_BROWSER_SIZE = None
BrowserFilterResult = namedtuple('BrowserFilterResult', 'stopNavigation closeBrowser')
BrowserFilterResult.__new__.__defaults__ = (False, False)

def LOG_BROWSER(msg):
    if _BROWSER_LOGGING and IS_DEVELOPMENT:
        BWLogging.getLogger('WEB').debug(msg)


def LOG_ERROR_BROWSER(msg):
    BWLogging.getLogger('WEB').error(msg)


class WebBrowserImpl(object):
    _WOWP_CLIENT_PARAM_NAME = 'wowp_client_param'
    url = property(lambda self: ('' if self.__browser is None else self.__browser.url))
    isFocused = property(lambda self: self.__isFocused)
    hasBrowser = property(lambda self: self.__browser is not None)
    isSuccessfulLoad = property(lambda self: self.__successfulLoad)
    skipEscape = property(lambda self: self.__skipEscape)
    ignoreKeyEvents = property(lambda self: self.__ignoreKeyEvents)
    useSpecialKeys = property(lambda self: self.__useSpecialKeys)
    allowMouseWheel = property(lambda self: self.__allowMouseWheel)

    @skipEscape.setter
    def skipEscape(self, value):
        LOG_BROWSER('skipEscape set %s (was: %s)' % (value, self.__skipEscape))
        self.__skipEscape = value

    @ignoreKeyEvents.setter
    def ignoreKeyEvents(self, value):
        LOG_BROWSER('ignoreKeyEvents set %s (was: %s)' % (value, self.__ignoreKeyEvents))
        self.__ignoreKeyEvents = value

    @useSpecialKeys.setter
    def useSpecialKeys(self, value):
        LOG_BROWSER('useSpecialKeys set %s (was: %s)' % (value, self.__useSpecialKeys))
        self.__useSpecialKeys = value

    @allowMouseWheel.setter
    def allowMouseWheel(self, value):
        LOG_BROWSER('allowMouseWheel set %s (was: %s)' % (value, self.__allowMouseWheel))
        self.__allowMouseWheel = value

    def __init__(self, browser_id, width, height, sfMovieClip, sfResourceName, url):
        self.__width = width
        self.__height = height
        self.__sfMovieClip = weakref.ref(sfMovieClip)
        self.__sfResourceName = sfResourceName
        self.__browserId = browser_id
        self.__browser = None
        self.__isFocused = False
        self.__isReady = False
        self.__baseUrl = url
        self.__navigationFilters = set()
        self.__skipEscape = True
        self.__ignoreKeyEvents = False
        self.__useSpecialKeys = True
        self.__allowMouseWheel = True
        self.__disableKeyHandlers = []
        self.__loadStartTime = BigWorld.time()
        self.__enableUpdate = False
        self.__isMouseDown = False
        self.__isWaitingForUnfocus = False
        self.__allowAutoLoadingScreenChange = True
        self.__isNavigationComplete = False
        self.__successfulLoad = False
        self.__delayedUrls = []
        self.__isCloseTriggered = False
        self.__specialKeyHandlers = None
        self.__browserKeyHandlers = None
        self.__eventMgr = EventManager()
        self.onLoadStart = Event(self.__eventMgr)
        self.onLoadEnd = Event(self.__eventMgr)
        self.onLoadingStateChange = Event(self.__eventMgr)
        self.onReadyToShowContent = Event(self.__eventMgr)
        self.onNavigate = Event(self.__eventMgr)
        self.onReady = Event(self.__eventMgr)
        self.onJsHostQuery = Event(self.__eventMgr)
        self.onTitleChange = Event(self.__eventMgr)
        self.onFailedCreation = Event(self.__eventMgr)
        self.onCanCreateNewBrowser = Event(self.__eventMgr)
        self.onCursorUpdated = Event(self.__eventMgr)
        return

    def create(self):
        LOG_BROWSER('Create id:{}'.format(self.__browserId))
        clientLanguage = ''
        self.__browser = BigWorld.createBrowser(self.__browserId, clientLanguage)
        if self.__browser is None:
            LOG_BROWSER('create() NO BROWSER WAS CREATED')
            return False
        else:
            self.__browser.script = EventListener(self)
            self.__browser.script.onLoadStart += self.__onLoadStart
            self.__browser.script.onLoadEnd += self.__onLoadEnd
            self.__browser.script.onLoadingStateChange += self.__onLoadingStateChange
            self.__browser.script.onDOMReady += self.__onReadyToShowContent
            self.__browser.script.onCursorUpdated += self.__onCursorUpdated
            self.__browser.script.onReady += self.__onReady
            self.__browser.script.onJsHostQuery += self.__onJsHostQuery
            self.__browser.script.onTitleChange += self.__onTitleChange

            def injectBrowserKeyEvent(me, e):
                if _BROWSER_KEY_LOGGING:
                    LOG_BROWSER('injectBrowserKeyEvent key:{} isKeyDown:{} isAltDown:{} isShiftDown:{} isCtrlDown:{}'.format(e.key, e.isKeyDown(), e.isAltDown(), e.isShiftDown(), e.isCtrlDown()))
                me.__browser.injectKeyEvent(e)

            def injectKeyDown(me, e):
                injectBrowserKeyEvent(me, e)

            def injectKeyUp(me, e):
                injectBrowserKeyEvent(me, e)

            def resetBit(value, bitMask):
                return value & ~bitMask

            self.__specialKeyHandlers = ((Keys.KEY_LEFTARROW,
              True,
              True,
              None,
              None,
              lambda me, _: me.__browser.goBack()), (Keys.KEY_RIGHTARROW,
              True,
              True,
              None,
              None,
              lambda me, _: me.__browser.goForward()), (Keys.KEY_F5,
              True,
              None,
              None,
              None,
              lambda me, _: me.__browser.reload()))
            self.__browserKeyHandlers = ((Keys.KEY_LSHIFT,
              False,
              None,
              True,
              None,
              lambda me, e: injectKeyUp(me, BigWorld.KeyEvent(e.key, e.repeatCount, resetBit(e.modifiers, 1), None, e.cursorPosition, 0))),
             (Keys.KEY_RSHIFT,
              False,
              None,
              True,
              None,
              lambda me, e: injectKeyUp(me, BigWorld.KeyEvent(e.key, e.repeatCount, resetBit(e.modifiers, 1), None, e.cursorPosition, 0))),
             (Keys.KEY_LCONTROL,
              False,
              None,
              None,
              True,
              lambda me, e: injectKeyUp(me, BigWorld.KeyEvent(e.key, e.repeatCount, resetBit(e.modifiers, 2), None, e.cursorPosition, 0))),
             (Keys.KEY_RCONTROL,
              False,
              None,
              None,
              True,
              lambda me, e: injectKeyUp(me, BigWorld.KeyEvent(e.key, e.repeatCount, resetBit(e.modifiers, 2), None, e.cursorPosition, 0))),
             (None,
              True,
              None,
              None,
              None,
              lambda me, e: injectKeyDown(me, e)),
             (None,
              False,
              None,
              None,
              None,
              lambda me, e: injectKeyUp(me, e)))
            self.__disableKeyHandlers = []
            return True

    def setDisabledKeys(self, keys):
        self.__disableKeyHandlers = []
        for key, isKeyDown, isAltDown, isShiftDown, isCtrlDown in keys:
            self.__disableKeyHandlers.append((key,
             isKeyDown,
             isAltDown,
             isShiftDown,
             isCtrlDown,
             lambda me, e: None))

    def ready(self, success):
        LOG_BROWSER('ready: id:{}, status:{}'.format(self.__browserId, 'success' if success else ''))
        self.__successfulLoad = False
        self.__enableUpdate = True
        self.__isMouseDown = False
        self.__isFocused = False
        self.__isWaitingForUnfocus = False
        if success:
            if self.__sfMovieClip():
                self.__browser.setScaleformRender(self.__sfMovieClip(), self.__sfResourceName, self.__width, self.__height)
            self.__browser.activate(True)
            self.__browser.loadURL(self.__baseUrl)
            self.__isReady = True
            self.focus(True)
            self.onReady(self.__browser.url, success)
        else:
            self.__isNavigationComplete = True
            self.onFailedCreation(self.__baseUrl)

    def __processDelayedNavigation(self):
        if self.__isNavigationComplete and self.__delayedUrls:
            self.doNavigate(self.__delayedUrls.pop(0))
            return True
        return False

    def destroy(self):
        LOG_BROWSER('fini id:{}'.format(self.__browserId))
        self.__eventMgr.clear()
        self.__eventMgr = None
        if self.__browser is not None:
            self.__browser.script.clear()
            self.__browser.script = None
            if self.__sfMovieClip():
                self.__browser.resetScaleformRender(self.__sfMovieClip(), self.__sfResourceName)
            BigWorld.removeBrowser(self.__browserId)
            self.__browser = None
        self.__navigationFilters = None
        self.onCursorUpdated('Cursor.ARROW')
        return

    def focus(self, focus):
        if self.hasBrowser:
            if focus and not self.__isFocused:
                self.__browser.focus()
                self.__isFocused = True
                self.onCursorUpdated(self.__browser.script.cursorType)
            elif not focus and self.__isFocused:
                self.__browser.unfocus()
                self.__isFocused = False
                self.__isWaitingForUnfocus = False

    def refresh(self, ignoreCache = True):
        if BigWorld.time() - self.__loadStartTime < 0.5:
            LOG_BROWSER('refresh - called too soon')
            return
        if self.hasBrowser:
            self.__browser.reload()
            self.onNavigate(self.__browser.url)

    def navigate(self, url):
        lastIsSame = self.__delayedUrls and self.__delayedUrls[-1] == url
        if not lastIsSame:
            self.__delayedUrls.append(url)
        self.__processDelayedNavigation()

    def sendMessage(self, message):
        if self.hasBrowser:
            self.__browser.sendMessage(message)

    def doNavigate(self, url):
        LOG_BROWSER('doNavigate: {}'.format(url))
        self.__baseUrl = url
        if self.hasBrowser:
            self.__browser.script.newNavigation()
            self.__browser.loadURL(url)
            self.onNavigate(url)

    def navigateBack(self):
        if self.hasBrowser:
            self.__browser.goBack(self.url)

    def navigateForward(self):
        if self.hasBrowser:
            self.__browser.goForward(self.url)

    def navigateStop(self):
        if BigWorld.time() - self.__loadStartTime < 0.5:
            LOG_BROWSER('navigateStop - called too soon')
            return
        if self.hasBrowser:
            self.__browser.stop()
            self.__onLoadEnd(self.__browser.url)

    def __getBrowserKeyHandler(self, key, isKeyDown, isAltDown, isShiftDown, isCtrlDown):
        from itertools import izip
        params = (key,
         isKeyDown,
         isAltDown,
         isShiftDown,
         isCtrlDown)
        matches = lambda t: t[0] is None or t[0] == t[1]
        browserKeyHandlers = tuple(self.__disableKeyHandlers) + self.__browserKeyHandlers
        if self.useSpecialKeys:
            browserKeyHandlers = self.__specialKeyHandlers + browserKeyHandlers
        for values in browserKeyHandlers:
            if reduce(lambda a, b: a and matches(b), izip(values, params), True):
                return values[-1]

        return None

    def handleKeyEvent(self, event):
        if not (self.hasBrowser and self.__enableUpdate):
            return False
        e = event
        keyState = (e.key,
         e.isKeyDown(),
         e.isAltDown(),
         e.isShiftDown(),
         e.isCtrlDown())
        if not self.skipEscape and e.key == Keys.KEY_ESCAPE and e.isKeyDown():
            self.__getBrowserKeyHandler(*keyState)(self, e)
            return True
        if not self.isFocused:
            self.__browser.injectKeyModifiers(e)
            return False
        if _BROWSER_KEY_LOGGING:
            LOG_BROWSER('handleKeyEvent {}'.format(keyState))
        if self.ignoreKeyEvents:
            return False
        if e.key in (Keys.KEY_ESCAPE,
         Keys.KEY_SYSRQ,
         Keys.KEY_LEFTMOUSE,
         Keys.KEY_RIGHTMOUSE):
            return False
        if e.key in (Keys.KEY_RETURN, Keys.KEY_NUMPADENTER) and e.isAltDown():
            return False
        self.__getBrowserKeyHandler(*keyState)(self, e)
        return True

    def browserMove(self, x, y, z):
        if not (self.hasBrowser and self.__enableUpdate and self.isFocused):
            return
        if z != 0:
            if self.allowMouseWheel:
                self.__browser.injectMouseWheelEvent(z * 20)
            return
        self.__browser.injectMouseMoveEvent(x, y)

    def browserDown(self, x, y, z):
        if not (self.hasBrowser and self.__enableUpdate):
            return
        elif self.__isMouseDown:
            return
        else:
            if not self.isFocused:
                self.focus(True)
                self.__isMouseDown = True
                self.browserUp(x, y, z)
                self.browserMove(x, y, z)
            self.__isMouseDown = True
            self.__browser.injectKeyEvent(BigWorld.KeyEvent(Keys.KEY_LEFTMOUSE, 0, 0, None, (x, y), 0))
            return

    def browserUp(self, x, y, z):
        if not (self.hasBrowser and self.__enableUpdate):
            return
        elif not self.__isMouseDown:
            return
        else:
            self.__isMouseDown = False
            self.__browser.injectKeyEvent(BigWorld.KeyEvent(Keys.KEY_LEFTMOUSE, -1, 0, None, (x, y), 0))
            if self.__isWaitingForUnfocus:
                self.focus(False)
            return

    def browserFocusOut(self):
        if self.isFocused and self.__isMouseDown:
            self.__isWaitingForUnfocus = True
            return
        self.focus(False)

    def browserAction(self, action):
        if self.hasBrowser and self.__enableUpdate:
            if action == 'reload' and self.__isNavigationComplete:
                self.refresh()
            elif action == 'loading' and not self.__isNavigationComplete:
                self.navigateStop()

    def onBrowserShow(self, needRefresh):
        self.__enableUpdate = True
        if needRefresh and self.__baseUrl != self.url:
            self.navigate(self.url)
        self.focus(True)

    def onBrowserHide(self):
        self.navigate(self.__baseUrl)
        self.__enableUpdate = False
        self.focus(False)

    def addFilter(self, handler):
        if handler in self.__navigationFilters:
            LOG_ERROR_BROWSER('Navigation filter is already added {}'.format(handler))
        else:
            self.__navigationFilters.add(handler)

    def removeFilter(self, handler):
        if handler in self.__navigationFilters:
            self.__navigationFilters.discard(handler)
        else:
            LOG_ERROR_BROWSER("Trying to delete navigation filter which doesn't exist {}".format(handler))

    def filterNavigation(self, url):
        query = urlparse.urlparse(url).query
        tags = urlparse.parse_qs(query).get(self._WOWP_CLIENT_PARAM_NAME, [])
        stopNavigation = False
        closeBrowser = False
        for handler in self.__navigationFilters:
            try:
                result = handler(url, tags)
                stopNavigation |= result.stopNavigation
                closeBrowser |= result.closeBrowser
                if result.stopNavigation:
                    LOG_BROWSER('Navigation filter triggered navigation stop: {}'.format(handler))
                if result.closeBrowser:
                    LOG_BROWSER('Navigation filter triggered browser close: {}'.format(handler))
            except:
                LOG_CURRENT_EXCEPTION()

        self.__isCloseTriggered = closeBrowser
        return stopNavigation

    def setLoadingScreenVisible(self, visible):
        LOG_BROWSER('setLoadingScreenVisible {}'.format(visible))
        self.onLoadingStateChange(visible, True)

    def setAllowAutoLoadingScreen(self, enabled):
        LOG_BROWSER('setAllowAutoLoadingScreen {}'.format(enabled))
        self.__allowAutoLoadingScreenChange = enabled

    def changeTitle(self, title):
        self.onTitleChange(title)

    def __onLoadStart(self, url):
        if url == self.__browser.url:
            self.__isNavigationComplete = False
            self.__loadStartTime = BigWorld.time()
            LOG_BROWSER('onLoadStart {}'.format(self.__browser.url))
            self.onLoadStart(self.__browser.url)
            self.__successfulLoad = False

    def __onLoadEnd(self, url, isLoaded = True, httpStatusCode = None):
        if url == self.__browser.url:
            self.__isNavigationComplete = True
            self.__successfulLoad = isLoaded
            if not self.__processDelayedNavigation():
                LOG_BROWSER('onLoadEnd {} {} {}'.format(self.__browser.url, isLoaded, httpStatusCode))
                self.onLoadEnd(self.__browser.url, isLoaded, httpStatusCode)

    def __onLoadingStateChange(self, isLoading):
        LOG_BROWSER('onLoadingStateChange {} {}'.format(isLoading, self.__allowAutoLoadingScreenChange))
        self.onLoadingStateChange(isLoading, self.__allowAutoLoadingScreenChange)
        if self.__isCloseTriggered:
            pass
        elif not isLoading:
            self.onCanCreateNewBrowser()

    def __onReadyToShowContent(self, url):
        if url == self.__browser.url:
            LOG_BROWSER('onReadyToShowContent {}'.format(self.__browser.url))
            self.onReadyToShowContent(self.__browser.url)

    def __isValidTitle(self, title):
        if self.__browser.url.startswith('about:'):
            return False
        if self.__browser.url.endswith(title):
            return False
        if self.__browser.url.endswith('/'):
            secondtest = self.__browser.url[:-1]
            if secondtest.endswith(title):
                return False
        if self.__baseUrl == title or self.__baseUrl.endswith(title):
            return False
        return True

    def __onTitleChange(self, title):
        if self.hasBrowser and self.__isValidTitle(title):
            LOG_BROWSER('onTitleChange {} {}'.format(title, self.__browser.url))
            self.onTitleChange(title)

    def __onCursorUpdated(self):
        if self.hasBrowser and self.isFocused:
            self.onCursorUpdated(self.__browser.script.cursorType)

    def __onReady(self, success):
        self.ready(success)

    def __onJsHostQuery(self, command):
        self.onJsHostQuery(command)

    def executeJavascript(self, script, frame):
        if self.hasBrowser:
            self.__browser.executeJavascript(script, frame)


def setWebBrowserSize(width, height):
    global _BROWSER_SIZE
    if _BROWSER_SIZE is None:
        _BROWSER_SIZE = (width, height)
    return


class WebBrowser(object):
    _TITLE_CHANGED = 1
    _CURSOR_CHANGED = 2
    _LOADING_STARTED = 3
    _LOADING_ENDED = 4
    _GOT_MESSAGE = 5

    def __init__(self, sfMovieClip, sfResourceName, flashCallbacks, pyGUIWindowOwner, url = 'about:blank'):
        self.__registeredFlashCallbackTypes = {self._TITLE_CHANGED: 'titleChanged',
         self._CURSOR_CHANGED: 'cursorChanged',
         self._LOADING_STARTED: 'loadingStarted',
         self._LOADING_ENDED: 'loadingEnded',
         self._GOT_MESSAGE: 'gotMessage'}
        if _BROWSER_SIZE:
            width = _BROWSER_SIZE[0]
            height = _BROWSER_SIZE[1]
        else:
            width = 515
            height = 512
        self._flashCallbacks = flashCallbacks or {}
        self._pyGUIWindowOwner = None
        self._impl = WebBrowserImpl(_DEFAULT_BROWSER_ID, width, height, sfMovieClip, sfResourceName, url)
        result = self._impl.create()
        if result:
            self._impl.onJsHostQuery += self._onJsHostQuery
            self._impl.onLoadStart += self._onLoadStart
            self._impl.onLoadEnd += self._onLoadEnd
            self._impl.onTitleChange += self._onChangeTitle
            self._impl.onCursorUpdated += self._onCursorUpdated
            GlobalEvents.onKeyEvent += self._onKeyEvent
            getattr(pyGUIWindowOwner, 'addExternalCallbacks')({'browser2.navigate': self.navigate,
             'browser2.refresh': self._onRefresh,
             'browser2.close': self._onClose,
             'browser2.mouseMove': self._onMouseMove,
             'browser2.mouseDown': self._onMouseDown,
             'browser2.mouseUp': self._onMouseUp,
             'browser2.sendMessage': self._onSendMessage})
            self._pyGUIWindowOwner = weakref.ref(pyGUIWindowOwner)
            self._impl.addFilter(self._onFilter)
        else:
            self._impl = None
        return

    def __del__(self):
        self.fini()

    def fini(self):
        if self._impl:
            if self._pyGUIWindowOwner():
                getattr(self._pyGUIWindowOwner(), 'removeExternalCallbacks')('browser2.navigate', 'browser2.refresh', 'browser2.close', 'browser2.mouseMove', 'browser2.mouseDown', 'browser2.mouseUp', 'browser2.sendMessage')
            GlobalEvents.onKeyEvent -= self._onKeyEvent
            self._impl.onJsHostQuery -= self._onJsHostQuery
            self._impl.onLoadStart -= self._onLoadStart
            self._impl.onLoadEnd -= self._onLoadEnd
            self._impl.onTitleChange -= self._onChangeTitle
            self._impl.onCursorUpdated -= self._onCursorUpdated
            self._impl.destroy()
            self._impl = None
        self._onClose()
        return

    def isWebBrowserSuccessCreated(self):
        return self._impl is not None

    def navigate(self, url):
        if self._impl:
            self._impl.navigate(url)

    def _onRefresh(self):
        self._impl.refresh()

    def _onClose(self):
        pass

    def _onMouseMove(self, x, y, mouseWheelDelta):
        self._impl.browserMove(x, y, mouseWheelDelta)

    def _onMouseDown(self, x, y, mouseWheelDelta):
        self._impl.browserDown(x, y, mouseWheelDelta)

    def _onMouseUp(self, x, y, mouseWheelDelta):
        self._impl.browserUp(x, y, mouseWheelDelta)

    def _onSendMessage(self, message):
        self._impl.sendMessage(message)

    def _onKeyEvent(self, event):
        self._impl.handleKeyEvent(event)

    def _callFlashCallback(self, callbackID, *args):
        if self._pyGUIWindowOwner() and callbackID in self._flashCallbacks:
            getattr(self._pyGUIWindowOwner(), 'call_1')(self._flashCallbacks[callbackID], *args)

    def _onChangeTitle(self, title):
        self._callFlashCallback(self.__registeredFlashCallbackTypes.get(self._TITLE_CHANGED), title)

    def _onCursorUpdated(self, cursorType):
        self._callFlashCallback(self.__registeredFlashCallbackTypes.get(self._CURSOR_CHANGED), cursorType)

    def _onLoadStart(self, url):
        self._callFlashCallback(self.__registeredFlashCallbackTypes.get(self._LOADING_STARTED), url)

    def _onLoadEnd(self, url, isLoaded, httpStatusCode = None):
        self._callFlashCallback(self.__registeredFlashCallbackTypes.get(self._LOADING_ENDED), url, isLoaded, httpStatusCode)

    def _onJsHostQuery(self, command):
        self._callFlashCallback(self.__registeredFlashCallbackTypes.get(self._GOT_MESSAGE), command)

    def _onFilter(self, url, tags):
        xmlData = ('yandex', 'ya.ru')
        for furl in xmlData:
            try:
                if url.index(furl):
                    return BrowserFilterResult(stopNavigation=True, closeBrowser=False)
            except ValueError:
                pass

        return BrowserFilterResult(stopNavigation=False, closeBrowser=False)


class EventListener():
    cursorType = property(lambda self: self.__cursorType)

    def __init__(self, browser):
        self.__cursorTypes = {CURSOR_TYPES.Hand: 'Cursor.HAND',
         CURSOR_TYPES.Pointer: 'Cursor.ARROW',
         CURSOR_TYPES.IBeam: 'Cursor.IBEAM',
         CURSOR_TYPES.Grab: 'Cursor.DRAG_OPEN',
         CURSOR_TYPES.Grabbing: 'Cursor.DRAG_CLOSE',
         CURSOR_TYPES.ColumnResize: 'Cursor.MOVE'}
        self.__cursorType = 'Cursor.ARROW'
        self.__eventMgr = EventManager()
        self.onLoadStart = Event(self.__eventMgr)
        self.onLoadEnd = Event(self.__eventMgr)
        self.onLoadingStateChange = Event(self.__eventMgr)
        self.onCursorUpdated = Event(self.__eventMgr)
        self.onDOMReady = Event(self.__eventMgr)
        self.onReady = Event(self.__eventMgr)
        self.onJsHostQuery = Event(self.__eventMgr)
        self.onTitleChange = Event(self.__eventMgr)
        self.__urlFailed = False
        self.__browserProxy = weakref.proxy(browser)

    def clear(self):
        self.__eventMgr.clear()

    def newNavigation(self):
        self.__urlFailed = False

    def onChangeCursor(self, cursorType):
        self.__cursorType = self.__cursorTypes.get(cursorType) or 'Cursor.ARROW'
        self.onCursorUpdated()

    def onChangeTitle(self, title):
        LOG_BROWSER('onChangeTitle "{}"'.format(title))
        self.onTitleChange(title)

    def ready(self, success):
        self.onReady(success)

    def onBeginLoadingFrame(self, frameId, isMainFrame, url):
        if isMainFrame:
            LOG_BROWSER('onBeginLoadingFrame(isMainFrame) "{}"'.format(url))
            self.onLoadStart(url)
            if self.__urlFailed:
                self.onLoadEnd(url, False)

    def onFailLoadingFrame(self, frameId, isMainFrame, url, errorCode, errorDesc):
        if isMainFrame:
            LOG_BROWSER('onFailLoadingFrame(isMainFrame) "{}", errorCode:{}, errorDesc:{}'.format(url, errorCode, errorDesc))
            self.__urlFailed = True

    def onFinishLoadingFrame(self, frameId, isMainFrame, url, httpStatusCode):
        if isMainFrame:
            LOG_BROWSER('onFinishLoadingFrame(isMainFrame) "{}" status:{}'.format(url, httpStatusCode))
            self.onLoadEnd(url, not self.__urlFailed, httpStatusCode)

    def onBrowserLoadingStateChange(self, isLoading):
        LOG_BROWSER('onBrowserLoadingStateChange() isLoading:{}'.format(isLoading))
        self.onLoadingStateChange(isLoading)

    def onDocumentReady(self, url):
        LOG_BROWSER('onDocumentReady "{}"'.format(url))
        self.onDOMReady(url)

    def onAddConsoleMessage(self, message, lineNumber, source):
        pass

    def onFilterNavigation(self, url):
        """
        This event occurs before frame navigations. You can use this to
        block or log navigations for each frame of a WebView.
        
        :param url: The URL that the frame wants to navigate to.
        :return: True to block a navigation. Return False to let it continue.
        """
        return self.__browserProxy.filterNavigation(url)

    def onWhitelistMiss(self, isMainFrame, failedURL):
        if isMainFrame:
            LOG_BROWSER('onWhitelistMiss(isMainFrame) "{}"'.format(failedURL))
            self.onLoadStart(failedURL)
            self.onLoadEnd(failedURL, False)

    def onShowCreatedWebView(self, url, isPopup):
        LOG_BROWSER('onShowCreatedWebView "{}" isPopup:{}'.format(url, isPopup))


class CURSOR_TYPES():
    Pointer = 0
    Cross = 1
    Hand = 2
    IBeam = 3
    Wait = 4
    Help = 5
    EastResize = 6
    NorthResize = 7
    NorthEastResize = 8
    NorthWestResize = 9
    SouthResize = 10
    SouthEastResize = 11
    SouthWestResize = 12
    WestResize = 13
    NorthSouthResize = 14
    EastWestResize = 15
    NorthEastSouthWestResize = 16
    NorthWestSouthEastResize = 17
    ColumnResize = 18
    RowResize = 19
    MiddlePanning = 20
    EastPanning = 21
    NorthPanning = 22
    NorthEastPanning = 23
    NorthWestPanning = 24
    SouthPanning = 25
    SouthEastPanning = 26
    SouthWestPanning = 27
    WestPanning = 28
    Move = 29
    VerticalText = 30
    Cell = 31
    ContextMenu = 32
    Alias = 33
    Progress = 34
    NoDrop = 35
    Copy = 36
    CursorNone = 37
    NotAllowed = 38
    ZoomIn = 39
    ZoomOut = 40
    Grab = 41
    Grabbing = 42
    Custom = 43