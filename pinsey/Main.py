import logging
import os
import sys

from PyQt5 import QtWidgets

from pinsey.Constants import LOGS_DATA_DIR
from pinsey.gui.MainWindow import MainWindow

# Set up logging service for bot.
log_path = LOGS_DATA_DIR + 'pinsey.log'
log_dir = os.path.dirname(log_path)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    handlers=[logging.FileHandler(log_path, 'a', 'utf-8')],
                    level=logging.INFO)


# The exception hook defined here enables PyQt5 to tell us any exceptions instead of just swallowing it.
# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

app = QtWidgets.QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
gui = MainWindow(app)
sys.exit(app.exec_())
