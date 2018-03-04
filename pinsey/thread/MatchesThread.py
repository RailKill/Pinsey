import logging
import pynder
from PyQt5 import QtCore


class MatchesThread(QtCore.QThread):
    """
        This is a QThread which runs in the background as a PyQt Signal. It emits the matches object.
        To access the matches object, you need to retrieve from the signal, which is named 'data_downloaded'.

        For example:

        instance = MatchesThread()
        instance.data_downloaded.connect(yourMethod)
        instance.start()

        With the example above, yourMethod() will be called when the background thread has finished fetching the
        matches data. The matches object will be passed in as the first parameter. Therefore, if you define your
        method like this: yourMethod(matches), then the session object will be passed into 'matches'.
    """
    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, session):
        QtCore.QThread.__init__(self)
        self.session = session
        self.abort = False
        self.bot_running = False
        self.logger = logging.getLogger(__name__)

    def stop(self):
        self.abort = True

    def start_bot(self):
        self.bot_running = True

    def stop_bot(self):
        self.bot_running = False

    def run(self):
        while not self.abort:
            try:
                matches = self.session.matches()
                self.data_downloaded.emit(matches)
            except pynder.errors.RequestError as requestError:
                if 504 in requestError.args:
                    self.logger.error('Error getting matches: 504 Gateway Timeout. Retrying...')
                elif 401 in requestError.args:
                    self.logger.error('Error getting matches: 401 Unauthorized. Renewing session...')
                    # TODO: Renew the pynder session.
                else:
                    raise

            # TODO: Bot handle matches. Message if needed.
            # if self.bot_running:
                # MatchesThread(matches)

            self.msleep(5000)  # Sleep for 5 seconds.
