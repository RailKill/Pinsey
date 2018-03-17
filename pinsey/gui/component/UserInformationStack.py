from PyQt5 import QtWidgets, QtCore
from Constants import THUMBNAIL_SIZE, CSS_FONT_NOTIFICATION, FONT_EMOJI
from Utils import name_set, get_connection_name, is_fb_friend


class UserInformationStack:
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

        # Set the maximum width that an information stack should take up.
        stack_maximum_width = THUMBNAIL_SIZE * 2

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
        self.connections.setMaximumWidth(stack_maximum_width)
        self.connections.setWordWrap(True)

        if user.schools:
            schools = str(user.schools)
        else:
            schools = 'None.'
        self.schools = QtWidgets.QLabel('<b>Schools: </b>' + schools)
        "QLabel containing user's list of schools."
        self.schools.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.schools.setMaximumWidth(stack_maximum_width)
        self.schools.setWordWrap(True)

        if user.jobs:
            jobs = ", ".join(str(x) for x in user.jobs)
        else:
            jobs = 'None.'
        self.jobs = QtWidgets.QLabel('<b>Occupation: </b>' + jobs)
        "QLabel containing user's list of jobs."
        self.jobs.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.jobs.setMaximumWidth(stack_maximum_width)
        self.jobs.setWordWrap(True)

        self.bio = QtWidgets.QLabel()
        "QLabel containing user's biography."
        # Users that don't have a biography will not have this 'bio' attribute. Check if it exists before proceeding.
        if user.bio:
            self.bio.setText(user.bio)
        else:
            self.bio.setText('No biography found.')
        self.bio.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.bio.setFont(FONT_EMOJI)
        self.bio.setMaximumWidth(stack_maximum_width)
        self.bio.setWordWrap(True)