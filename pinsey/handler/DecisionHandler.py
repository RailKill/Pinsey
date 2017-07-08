import os
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
        self.bio_blacklist = self.initialize_blacklist()

    def analyze(self, user, friend_list):
        """
            Analyze a user and see if this person is fit to be liked or disliked.

            :param user:    Pynder User object.
            :type user:     pynder.models.user.User
            :return:        True if this user should be liked. Otherwise, False.
            :rtype:         bool
        """
        if self.exclude_friends and is_fb_friend(user, friend_list):
            print('Disliking ' + user.name + ' because this user is a Facebook friend.')
            return False

        if self.exclude_mutual and user.common_connections:
            print('Disliking ' + user.name + ' because this user is a mutual friend.')
            return False

        if user.bio:
            # Biography threshold check.
            if self.bio_threshold > 0:
                if len(user.bio) < self.bio_threshold:
                    print('Disliking ' + user.name + ' due to not having a long enough biography.')
                    return False

            # Biography blacklist word check.
            if any(blacklisted_substring.lower() in user.bio.lower() for blacklisted_substring in self.bio_blacklist):
                print('Disliking ' + user.name + ' for having a biography that contains a blacklisted keyword.')
                return False

        # Check each image for this user if it is within the specified minimum and maximum face threshold.
        faces_detected_list = FaceDetectionHandler(user.photos).run()
        number_of_good_images = 0
        for number in faces_detected_list:
            if self.face_minimum <= number <= self.face_threshold:
                number_of_good_images += 1

        if number_of_good_images >= self.img_threshold:
            return True
        else:
            print('Disliking ' + user.name + ' due to not having good enough images.')
            return False

    @staticmethod
    def initialize_blacklist():
        blacklist_path = 'bio-blacklist.txt'  # TODO: Replace path to user data directory instead.
        if os.path.exists(blacklist_path):
            with open(blacklist_path, 'r') as blacklist:
                bio_blacklist = [line.strip() for line in blacklist]

            return bio_blacklist
        else:
            default_blacklist = ['shemale', 'she-male', 'trans', 'm a guy', 'm a dude', 'm male', 'm a boy',
                                 'i have a dick', 'my dick']
            with open(blacklist_path, 'w') as blacklist:
                for item in default_blacklist:
                    blacklist.write("%s\n" % item)

            return default_blacklist
