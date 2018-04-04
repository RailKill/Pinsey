import logging
from pynder import errors
from random import randint
from PyQt5 import QtCore


class LikesBotThread(QtCore.QThread):
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

    def __init__(self, session, likes_handler, decision_handler=None):
        QtCore.QThread.__init__(self)
        self.session = session
        self.friends = session.get_fb_friends()
        self.likes_handler = likes_handler
        self.decision_handler = decision_handler
        self.abort = False
        self.logger = logging.getLogger(__name__)

    def stop(self):
        self.abort = True

    def run(self):
        while not self.abort:
            if self.session.likes_remaining != 0:
                nearby_users = self.session.nearby_users()
                try:
                    user = next(nearby_users)  # Iterate through generator object.
                    if self.decision_handler:
                        if not self.decision_handler.analyze(user, self.friends):
                            self.likes_handler.dislike_user(user, 'Bot')
                            continue
                    self.likes_handler.like_user(user, 'Bot')
                    self.logger.info(u'Liking ' + user.name + '.')
                except StopIteration:
                    try:
                        # No more users to go through. Reset the distance filter to fetch the users again.
                        self.session.profile.distance_filter = self.session.profile.distance_filter
                    except errors.RequestError:
                        self.logger.error('Request timed out when trying to update distance filter in profile.')
                except errors.RecsError:
                    self.logger.info('There are probably no more nearby users to fetch. '
                                     'Increasing distance filter by 1 mile...')
                    self.session.profile.distance_filter += 1
                self.sleep(randint(3, 5))  # Give it a break, 3 to 5 seconds between every swipe.
            else:
                try:
                    like_in_seconds = self.session.can_like_in
                    like_in_hours = like_in_seconds / 60 / 60
                    self.logger.info('Out of likes. Can like in: ' + str(like_in_seconds) + ' seconds (' +
                                     str(like_in_hours) + ' hours).')
                except errors.RequestError:
                    self.logger.info('Out of likes. Retrying in an hour...')
                self.sleep(3600 * 6)  # Out of likes, pausing for X hours.
