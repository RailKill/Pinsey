import logging
import os
import sys
from PyQt4 import QtGui
from pinsey.Constants import LOGS_DATA_DIR
from pinsey.gui.MainWindow import MainWindow


# Set up logging service for bot.
log_path = LOGS_DATA_DIR + 'pinsey.log'
log_dir = os.path.dirname(log_path)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(filename=LOGS_DATA_DIR + 'pinsey.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

app = QtGui.QApplication(sys.argv)
gui = MainWindow(app)
sys.exit(app.exec_())
