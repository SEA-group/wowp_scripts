# Embedded file name: scripts/client/gui/Cursor.py
import BigWorld
import GUI
from bwdebug import WARNING_MSG
_mouseModeRefCount = 0

class CursorPositionData:
    CENTER = (0.0, 0.0)
    POSITION = CENTER


def showCursor(show, clipCursor = None):
    global _mouseModeRefCount
    if show:
        _mouseModeRefCount += 1
        if _mouseModeRefCount > 0:
            _showMouseCursor(clipCursor)
    else:
        _mouseModeRefCount -= 1
        if _mouseModeRefCount == 0:
            _hideMouseCursor(clipCursor)
        if _mouseModeRefCount < 0:
            WARNING_MSG('mouseModeRefCount is negative!')


def forceShowCursor(show, clipCursor = None):
    if show:
        _showMouseCursor(clipCursor)
    else:
        _hideMouseCursor(clipCursor)


def centerCursor():
    CursorPositionData.POSITION = CursorPositionData.CENTER


def pixelPosition():
    screenWidth, screenHeight = GUI.screenResolution()
    mouseLeft, mouseTop = GUI.mcursor().position
    width = round((1.0 + mouseLeft) / 2.0 * screenWidth)
    height = round(-(-1.0 + mouseTop) / 2.0 * screenHeight)
    return (width, height)


def _showMouseCursor(clipCursor = None):
    BigWorld.setCursor(GUI.mcursor())
    if not GUI.mcursor().visible:
        GUI.mcursor().position = CursorPositionData.POSITION
    GUI.mcursor().visible = True
    GUI.mcursor().clipped = False if clipCursor is None else clipCursor
    return


def _hideMouseCursor(clipCursor = None):
    BigWorld.setCursor(BigWorld.dcursor())
    GUI.mcursor().visible = False
    GUI.mcursor().clipped = True if clipCursor is None else clipCursor
    CursorPositionData.POSITION = GUI.mcursor().position
    _triggerMouseOutEventsOnScaleform()
    return


def _triggerMouseOutEventsOnScaleform():
    import WindowsManager
    mouseEvent = BigWorld.MouseEvent(0, 0, 0, (-1, -1))
    WindowsManager.g_windowsManager.activeMovie.movie.handleMouseEvent(mouseEvent)