import logging
import os
from pinsey.Constants import USER_DATA_DIR
from pinsey.Utils import is_fb_friend
from pinsey.handler.FaceDetectionHandler import FaceDetectionHandler


class DecisionHandler:
    def __init__(self, img_threshold, face_threshold, bio_threshold, exclude_friends, exclude_mutual):
        """
            Handles the decision-making required by the bot to choose whether to like or dislike a user.

            :param img_threshold:       Minimum number of good images required to pass.
            :type img_threshold:        int
            :param face_threshold:      Minimum number of faces required in an image to be considered good.
            :type face_threshold:       int
            :param bio_threshold:       Minimum length of biography required to pass.
            :type bio_threshold:        int
            :param exclude_friends:     If True, fail immediately if user is a Facebook friend.
            :type exclude_friends:      bool
            :param exclude_mutual:      If True, fail immediately if user is a mutual friend on Facebook.
            :type exclude_mutual:       bool
        """
        self.img_threshold = img_threshold
        self.face_minimum = 1  # Assume that we want to detect at least 1 face for all of the user's images.
        self.face_threshold = face_threshold
        self.bio_threshold = bio_threshold
        self.exclude_friends = exclude_friends
        self.exclude_mutual = exclude_mutual
        self.blacklist_path = USER_DATA_DIR + 'bio-blacklist.txt'
        self.bio_blacklist = self.initialize_blacklist()
        self.logger = logging.getLogger(__name__)

    def analyze(self, user, friend_list):
        """
            Analyze a user and see if this person is fit to be liked or disliked.

            :param user:    Pynder User object.
            :type user:     pynder.models.user.User
            :return:        True if this user should be liked. Otherwise, False.
            :rtype:         bool
        """
        if self.exclude_friends and is_fb_friend(user, friend_list):
            self.logger.info(u'Disliking ' + user.name + ' because this user is a Facebook friend.')
            return False

        if self.exclude_mutual and user.common_connections:
            self.logger.info(u'Disliking ' + user.name + ' because this user is a mutual friend.')
            return False

        if user.bio:
            # Biography threshold check.
            if self.bio_threshold > 0:
                if len(user.bio) < self.bio_threshold:
                    self.logger.info(u'Disliking ' + user.name + ' due to biography less than ' +
                                     str(self.bio_threshold) + ' characters.')
                    return False

            # Biography blacklist word check.
            match = [blacklisted_substring for blacklisted_substring in self.bio_blacklist
                     if blacklisted_substring.lower() in user.bio.lower()]
            # any(blacklisted_substring.lower() in user.bio.lower() for blacklisted_substring in self.bio_blacklist)
            if match:
                self.logger.info(u'Disliking ' + user.name + ', biography contains blacklisted keyword(s): ' +
                                 ', '.join(match))
                return False
        else:
            # A biography threshold of more than 0 requires a biography to be present.
            if self.bio_threshold > 0:
                self.logger.info(u'Disliking ' + user.name + ' for not having a biography.')
                return False

        # Check each image for this user if it is within the specified minimum and maximum face threshold.
        faces_detected_list = FaceDetectionHandler(user.photos).run()
        number_of_good_images = 0
        for number in faces_detected_list:
            if self.face_minimum <= number <= self.face_threshold:
                number_of_good_images += 1

        if number_of_good_images < self.img_threshold:
            reason = ' for not having enough good images (detected ' + str(number_of_good_images) + \
                     ', required ' + str(self.img_threshold) + ').'
            self.logger.info(u'Disliking ' + user.name + reason)
            return False

        # After analysis, if there is no reason to dislike, then return True.
        return True

    def initialize_blacklist(self):
        if os.path.exists(self.blacklist_path):
            with open(self.blacklist_path, 'r') as blacklist:
                bio_blacklist = [line.strip() for line in blacklist]

            return bio_blacklist
        else:
            default_blacklist = ['shemale', 'she-male', 'trans', 'm a guy', 'm a dude', 'm male', 'm a boy',
                                 'i have a dick', 'my dick', 'ladyboy', 'lady-boy']
            with open(self.blacklist_path, 'w') as blacklist:
                for item in default_blacklist:
                    blacklist.write("%s\n" % item)

            return default_blacklist
