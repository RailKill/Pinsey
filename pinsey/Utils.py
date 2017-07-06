import re
from PyQt4 import QtGui, QtCore

EMOJI_PATTERN = re.compile('['
        u'\U0001F600-\U0001F64F'  # emoticons
        u'\U0001F300-\U0001F5FF'  # symbols & pictographs
        u'\U0001F680-\U0001F6FF'  # transport & map symbols
        u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
                           ']+', flags=re.UNICODE)

class EmptyDict(dict):
    pass

def clickable(widget):
    class Filter(QtCore.QObject):
        clicked = QtCore.pyqtSignal()

        def eventFilter(self, obj, event):

            if obj == widget:
                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        # The developer can opt for .emit(obj) to get the object within the slot.
                        return True

            return False

    event_filter = Filter(widget)
    widget.installEventFilter(event_filter)
    return event_filter.clicked


def center(window):
    screen = QtGui.QDesktopWidget().screenGeometry()
    size = window.geometry()
    window.move((screen.width() / 2) - (size.width() / 2), (screen.height() / 2) - (size.height() / 2))


def horizontal_line():
    line = QtGui.QFrame()
    line.setFrameShadow(QtGui.QFrame.Sunken)
    line.setFrameShape(QtGui.QFrame.HLine)
    return line