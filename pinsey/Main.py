import sys
from PyQt4 import QtGui
from pinsey.gui.MainWindow import MainWindow

app = QtGui.QApplication(sys.argv)
gui = MainWindow(app)
sys.exit(app.exec_())
