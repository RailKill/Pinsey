import urllib
from pynder import errors
from PyQt5 import QtCore


class NearbyUsersThread(QtCore.QThread):
    """
    This is a QThread which runs in the background as a PyQt Signal. It emits the list of nearby users given a
    Pynder session. To access the nearby users, you need to retrieve from the signal, which is named 'data_downloaded'.

    For example:

    instance = NearbyUsersThread(session)
    instance.data_downloaded.connect(yourMethod)

    With the example above, yourMethod() will be called when the background thread has finished fetching the
    nearby users data. The nearby users list will be passed in as the first parameter. Therefore, if you define your
    method like this: yourMethod(list), then the nearby users will be passed into 'list'.
    """
    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, session):
        QtCore.QThread.__init__(self)
        self.session = session

    def run(self):
        nearby_users = self.session.nearby_users()  # Generator object.
        user_list = []
        limit = 10  # TODO: Should not be fixed to 10, let it be user customizable.

        # Download first image as thumbnail and add it as a new attribute of the user so it can be retrieved later.
        for i in range(limit):
            try:
                user = next(nearby_users)  # Iterate through generator object.
                user.thumb_data = urllib.request.urlopen(next(user.photos)).read()
                user_list.append(user)
            except urllib.error.HTTPError as ex:
                # Ignore. Sometimes images are inaccessible, maybe it's private or deleted?
                print('Nearby users fetching error: ' + str(ex))
            except StopIteration:
                break
            except errors.RecsTimeout as recs:
                # Request timeout, stop and ask the user to try again later.
                print('Request timeout. Possibly no more nearby users to show. ' + str(recs))
                break

        # Return the modified list of users.
        self.data_downloaded.emit(user_list)