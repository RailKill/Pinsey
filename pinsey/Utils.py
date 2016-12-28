from PyQt4 import QtGui, QtCore

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
    window.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


def horizontal_line():
    line = QtGui.QFrame()
    line.setFrameShadow(QtGui.QFrame.Sunken)
    line.setFrameShape(QtGui.QFrame.HLine)
    return line