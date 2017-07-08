import re
from PyQt4.QtGui import QFont

# Regular expression pattern for emoji unicode characters.
EMOJI_PATTERN = re.compile('['
        u'\U0001F600-\U0001F64F'  # emoticons
        u'\U0001F300-\U0001F5FF'  # symbols & pictographs
        u'\U0001F680-\U0001F6FF'  # transport & map symbols
        u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
                           ']+', flags=re.UNICODE)

# Standard font for emoji-containing text such as biography or messaging area.
FONT_EMOJI = QFont('Segoe UI Symbol', 12)

# Standard emoji-supporting font used for big headings.
FONT_HEADLINE = QFont('Segoe UI Symbol', 16, QFont.Bold)

# Used for category headings.
CSS_FONT_CATEGORY = 'color: teal; font-weight: bold;'

# Used for notification alerts.
CSS_FONT_NOTIFICATION = 'color: green; font-size: large; font-weight: bold;'

# Used in the messaging area when you are the sender of the message.
CSS_FONT_MESSAGE_YOU = 'color: blue; font-weight: bold;'

# Used in the messaging area when your match is the sender of the message.
CSS_FONT_MESSAGE_MATCH = 'color: red; font-weight: bold;'

# Size of the thumbnail picture squares in pixels.
THUMBNAIL_SIZE = 300

# Number of photos allowed per user.
NUMBER_OF_PHOTOS = 6

# File path of the application's logo/icon.
ICON_FILEPATH = '../resources/icons/logo-128x128.png'

# Maximum number of faces detected in photo before marking user's photo as bad.
THRESHOLD_FACE_DEFAULT = 2

# Minimum number of good images required to pass as a likeable user.
THRESHOLD_IMG_DEFAULT = 1

# Minimum biography character length in order to pass as a likeable user.
THRESHOLD_BIO_DEFAULT = 0
