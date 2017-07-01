import pynder
from geopy.geocoders import Nominatim
from PyQt4 import QtCore


class SessionThread(QtCore.QThread):
    """
        This is a QThread which runs in the background as a PyQt Signal. It emits the Pynder session object.
        To access the session object, you need to retrieve from the signal, which is named 'data_downloaded'.

        For example:

        instance = SessionThread()
        instance.data_downloaded.connect(yourMethod)

        With the example above, yourMethod() will be called when the background thread has finished fetching the
        session data. The session object will be passed in as the first parameter. Therefore, if you define your
        method like this: yourMethod(sess), then the session object will be passed into 'sess'.
    """
    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, id, auth, location):
        QtCore.QThread.__init__(self)
        self.id = id
        self.auth = auth
        self.location = location

    def run(self):
        try:
            session = pynder.Session(facebook_id=self.id, facebook_token=self.auth)
            geolocator = Nominatim()
            location = geolocator.geocode(self.location)
            session.update_location(location.latitude, location.longitude)
        except pynder.errors.RequestError:
            session = pynder.errors.RequestError('Facebook authentication failed! \n\n'
                                                 'Please ensure that the authentication details are entered and saved '
                                                 'correctly in the Settings tab.')
        except Exception as e:
            session = e

        self.data_downloaded.emit(session)

