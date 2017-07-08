from PyQt4 import QtCore


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

    def stop(self):
        self.abort = True

    def run(self):
        while not self.abort:
            # TODO: Bot handle likes. Probably there should be a separate thread for this.
            matches = self.session.matches()
            # TODO: Bot handle matches. Message if needed.
            self.data_downloaded.emit(matches)
            self.msleep(5000)  # Sleep for 5 seconds.
