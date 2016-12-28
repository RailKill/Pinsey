import sys
from pinsey.Window import Window
from PyQt4 import QtGui


app = QtGui.QApplication(sys.argv)
gui = Window()
sys.exit(app.exec_())
