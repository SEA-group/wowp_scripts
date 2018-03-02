# Embedded file name: scripts/client/GlobalEvents.py
from Event import BlockingEvent, Event
onChangeLocale = Event()
onRefreshResolutions = Event()
onSetFocus = Event()
onRecreateDevice = Event()
onScreenshot = Event()
onMovieLoaded = Event()
onHideModalScreen = Event()
onHangarLoaded = Event()
onOneSecondTimer = Event()
onKeyEvent = BlockingEvent()
onMouseEvent = BlockingEvent()
onAxisEvent = BlockingEvent()