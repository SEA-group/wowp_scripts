# Embedded file name: scripts/client/VSHangarEvent.py
import BigWorld
import Keys

def getVSEventByName(eventName):
    events = BigWorld.events()
    if events:
        event = getattr(events, eventName)
        if event:
            return event
        LOG_ERROR('[VSCRIPT] Event is not registered')
    else:
        LOG_ERROR('[VSCRIPT] Event system is not registered')
    return None


def getVSEvent(isKeyDown, key):
    CMD_MOUSE_LBUTTON_DOWN = 'CMD_MOUSE_LBUTTON_DOWN'
    CMD_MOUSE_LBUTTON_UP = 'CMD_MOUSE_LBUTTON_UP'
    CMD_MOUSE_RBUTTON_DOWN = 'CMD_MOUSE_RBUTTON_DOWN'
    CMD_MOUSE_RBUTTON_UP = 'CMD_MOUSE_RBUTTON_UP'
    CMD_SKIP_INTRO = 'CMD_SKIP_INTRO'
    eventName = None
    if key == Keys.KEY_ESCAPE and isKeyDown:
        eventName = CMD_SKIP_INTRO
    elif key == Keys.KEY_LEFTMOUSE:
        eventName = CMD_MOUSE_LBUTTON_DOWN if isKeyDown else CMD_MOUSE_LBUTTON_UP
    elif key == Keys.KEY_RIGHTMOUSE:
        eventName = CMD_MOUSE_RBUTTON_DOWN if isKeyDown else CMD_MOUSE_RBUTTON_UP
    if eventName:
        return getVSEventByName(eventName)
    else:
        return


def onHangarKeyEvent(event):
    vsEvent = getVSEvent(event.isKeyDown(), event.key)
    if vsEvent:
        if event.isMouseButton():
            vsEvent.post('', {'x': event.cursorPosition.x,
             'y': event.cursorPosition.y})
        else:
            vsEvent.post('', {})