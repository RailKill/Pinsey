from PyQt5 import QtCore, QtGui, QtWidgets
from pinsey.Constants import FONT_EMOJI, FONT_HEADLINE, CSS_FONT_NOTIFICATION


class EmptyDict(dict):
    pass


class UserInformationWidgetStack:
    def __init__(self, user, friend_list=None):
        """
                Generates a dictionary object containing widgets for user information. These widgets can be accessed by
                the following attributes: name_set, dob, distance, schools, jobs, bio.

                :param user:    Pynder User object whose information is to be generated.
                :type user:     pynder.models.user.User

                :Example:
                addWidget(UserInformationWidgetStack(user).name_set)
        """
        if not friend_list:
            friend_list = []

        self.name_set = name_set(user.name, user.gender, user.age)  # User will definitely have a name attribute.
        "QLabel formatting of user's name, gender and age."

        self.dob = QtWidgets.QLabel('<b>Birthday: </b>' + user.birth_date.strftime("%B %d, %Y"))
        "QLabel containing user's date of birth."
        self.dob.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.distance = QtWidgets.QLabel('<b>Distance: </b>' + "{0:.2f}".format(user.distance_km) + 'km')
        "QLabel containing user's distance in km."
        self.distance.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        if user.common_connections:
            connections = ", ".join(str(x) + ' (' + get_connection_name(x, friend_list) + ')'
                                    for x in user.common_connections)
        else:
            connections = 'None.'
        if is_fb_friend(user, friend_list):
            connections += '<span style="' + CSS_FONT_NOTIFICATION + '"> (Friend) </span>'
        self.connections = QtWidgets.QLabel('<b>Common Connections: </b>' + connections)
        "QLabel containing user's list of common connections."
        self.connections.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        if user.schools:
            schools = ", ".join(str(x) for x in user.schools)
        else:
            schools = 'None.'
        self.schools = QtWidgets.QLabel('<b>Schools: </b>' + schools)
        "QLabel containing user's list of schools."
        self.schools.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        if user.jobs:
            jobs = ", ".join(str(x) for x in user.jobs)
        else:
            jobs = 'None.'
        self.jobs = QtWidgets.QLabel('<b>Occupation: </b>' + jobs)
        "QLabel containing user's list of jobs."
        self.jobs.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.bio = QtWidgets.QLabel()
        "QLabel containing user's biography."
        # Users that don't have a biography will not have this 'bio' attribute. Check if it exists before proceeding.
        if user.bio:
            self.bio.setText(user.bio)
        else:
            self.bio.setText('No biography found.')
        self.bio.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.bio.setFont(FONT_EMOJI)


def clickable(widget):
    class Filter(QtCore.QObject):
        clicked = QtCore.pyqtSignal()

        def eventFilter(self, obj, event):

            if obj == widget:
                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        # The developer can opt for .emit(obj) to get the object within the slot.
                        return True

            return False

    event_filter = Filter(widget)
    widget.installEventFilter(event_filter)
    return event_filter.clicked


def center(window):
    screen = QtWidgets.QDesktopWidget().screenGeometry()
    size = window.geometry()
    window.move((screen.width() / 2) - (size.width() / 2), (screen.height() / 2) - (size.height() / 2))


def horizontal_line():
    line = QtWidgets.QFrame()
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    line.setFrameShape(QtWidgets.QFrame.HLine)
    return line


def is_fb_friend(user, friend_list):
    """
        Checks if a given user exists in the given friend list.

        :param user:            User.
        :type user:             pynder.models.user.User
        :param friend_list:     Friend list.
        :type friend_list:      list of pynder.models.friend.Friend
        :return:                True if user is a friend, false otherwise.
        :rtype:                 bool
    """
    for friend in friend_list:
        if friend.user_id == user.id:
            return True
    return False


def get_connection_name(connection_id, friend_list):
    """
        Given a mutual friends' ID, check the given list of Facebook friends and extract the name.

        :param connection_id:       Connection's (mutual friend) Facebook ID.
        :type connection_id:        str
        :param friend_list:         List of Facebook friends.
        :type friend_list:          list of pynder.models.friend.Friend
        :return:                    Friend's name.
        :rtype:                     str
    """
    for friend in friend_list:
        if connection_id == friend.facebook_id:
            return friend.name
    return ''


def name_set(name, gender, age=0, banned=False):
    """
        Generates a QLabel name set that formats the name, gender and age nicely.

        :param name:    User's name.
        :type name:     str
        :param gender:  User's gender which should be 'male' or 'female' only.
        :type gender:   str
        :param age:     User's age.
        :type age:      int
        :param banned:  [Optional] Is the user banned or not?
        :type banned:   bool
        :return:        A QtWidgets.QLabel set that has the name, gender and age nicely formatted.
        :rtype:         QtWidgets.QLabel
    """
    age_string = '(' + str(age) + ')' if age > 0 else ''
    banned_string = '<span style="color: Red;"> [BANNED] </span>' if banned else ''

    if gender.lower() == 'female':
        gender_string = '<span style="color: DeepPink;"> ♀ </span>'
    else:
        gender_string = '<span style="color: DodgerBlue;"> ♂ </span>'
    name_string = name + gender_string + age_string + banned_string
    label_name = QtWidgets.QLabel(name_string)
    label_name.setFont(FONT_HEADLINE)
    label_name.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
    return label_name


def picture_grid(image_dict, image_size, number_of_photos):
    """
        Generates a picture grid that has exactly 3 columns and fits the images in image_dict based on
        number_of_photos. The first column will contain the main image with image_size, followed by the second
        and third columns containing the rest of the images.

        :param image_dict:          This dictionary of image data is generated by DownloadPhotosThread
                                    containing 'url' and 'data' attributes.
        :type image_dict:           dict
        :param image_size:          Size in pixels squared for the main image on the grid.
        :type image_size:           int
        :param number_of_photos:    Number of photos to fit into the grid.
        :type number_of_photos:     int
        :return:                    Generated QtWidgets.QGridLayout picture grid layout.
        :rtype:                     QtWidgets.QGridLayout
    """
    pp_layout = QtWidgets.QGridLayout()
    pp_layout.setSpacing(1)

    photos_half_amount = number_of_photos / 2
    photos_median = number_of_photos - photos_half_amount - 1
    median_section_count = 0
    last_section_count = 0

    for i in range(number_of_photos):
        image = QtGui.QImage()
        label = QtWidgets.QLabel()

        # Load profile photo data.
        label.setScaledContents(True)
        if i < len(image_dict):
            image.loadFromData(image_dict[i].data)
            label.setPixmap(QtGui.QPixmap(image))
        else:
            label.setText(str(i + 1))
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet('border: 1px solid')

        # Determine photo size for grid arrangement.
        size = image_size
        if i >= photos_half_amount:
            size /= photos_half_amount
            pp_layout.addWidget(label, last_section_count * photos_median, 2, photos_median, 1)
            last_section_count += 1
        elif i > 0:
            size /= photos_median
            pp_layout.addWidget(label, median_section_count * photos_half_amount, 1, photos_half_amount, 1)
            median_section_count += 1
        else:
            pp_layout.addWidget(label, 0, 0, photos_half_amount * photos_median, 1)
        label.setFixedWidth(size)
        label.setFixedHeight(size)

    return pp_layout
