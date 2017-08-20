import os

from pinsey.Constants import USER_DATA_DIR


class MatchChatHandler:
    def __init__(self, match):
        """

        :param match:
        :type match: pynder.models.user.Match
        """
        self.match = match
        self.conversation_history_path = os.path.join(USER_DATA_DIR + 'conversations', '')
        self.possible_responses_path = USER_DATA_DIR + 'automated_responses.txt'

    def flirt(self):
        match = self.match
        sentence = ''

        # Check bio for anything usable. Split by '.' and find sentences, then compare with automated responses.
        match.message(sentence)
