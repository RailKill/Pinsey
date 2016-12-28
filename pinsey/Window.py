from configparser import ConfigParser
from configparser import DuplicateSectionError
from pinsey.ImageWindow import ImageWindow
from pinsey.Utils import clickable, center, horizontal_line
from pinsey.thread.NearbyUsersThread import NearbyUsersThread
from pinsey.thread.SessionThread import SessionThread
from PyQt4 import QtGui, QtCore


class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        # Constants.
        self.CSS_FONT_EMOJI = "font-family: 'Segoe UI Symbol', sans;"  # Segoe as a Windows-friendly font for emoji.
        self.CSS_FONT_HEADLINE = "font-size: xx-large; font-weight: bold;"  # Used for big headings.
        self.CSS_FONT_CATEGORY = "color: blue; font-weight: bold;"  # Used for category headings.
        self.THUMBNAIL_SIZE = 300  # Size of the thumbnail picture squares in pixels.

        # Initialize Window GUI controls.
        self.label_status = QtGui.QLabel()
        self.txt_location = QtGui.QLineEdit()
        self.txt_auth = QtGui.QLineEdit()
        self.txt_id = QtGui.QLineEdit()
        self.txt_img_threshold = QtGui.QLineEdit()
        self.txt_face_threshold = QtGui.QLineEdit()
        self.txt_bio_threshold = QtGui.QLineEdit()
        self.txt_pickup_threshold = QtGui.QLineEdit()
        self.chk_decision = QtGui.QCheckBox('Decision-Making', self)
        self.chk_autochat = QtGui.QCheckBox('Autonomous Chatting', self)
        self.chk_respond_list = QtGui.QCheckBox('Respond from List', self)
        self.chk_respond_bot = QtGui.QCheckBox('Respond using Cleverbot', self)

        # Initialize application variables.
        self.windows = []
        self.session = None
        self.setWindowTitle('Pinsey')
        self.setWindowIcon(QtGui.QIcon('../resources/icons/logo-128x128.png'))
        self.setMinimumWidth(500)
        self.minimumHeight()
        center(self)

        # Run startup methods to setup the GUI.
        self.read_settings()
        self.setup_tabs()
        self.connect_tinder()  # Start Tinder session.
        self.decision_change()

    '''
    +=======================================+
    | GUI METHODS: Resizing, UI setup, etc. |
    +=======================================+
    '''

    def setup_tabs(self):
        tabs = QtGui.QTabWidget()

        tab_liked = QtGui.QWidget()
        la = QtGui.QWidget()
        la.setLayout(QtGui.QVBoxLayout())
        boton = QtGui.QPushButton('Top', self)
        boton.clicked.connect(lambda: (sc.setWidget(QtGui.QWidget()), print('clicked')))
        for _ in range(10):
            card = QtGui.QWidget()
            card.setLayout(QtGui.QGridLayout())
            card.layout().setSpacing(10)
            card.layout().addWidget(QtGui.QPushButton('thumb', self), 1, 0, 4, 1)
            card.layout().addWidget(QtGui.QLabel('name'), 1, 1)
            card.layout().addWidget(QtGui.QLabel('school'), 2, 1)
            card.layout().addWidget(QtGui.QLabel('job'), 3, 1)
            card.layout().addWidget(QtGui.QTextEdit('bio'), 4, 1)
            la.layout().addWidget(card)
        sc = QtGui.QScrollArea()
        sc.setWidget(la)
        tab_liked.setLayout(QtGui.QVBoxLayout())
        tab_liked.layout().addWidget(boton)
        tab_liked.layout().addWidget(sc)

        tab_disliked = QtGui.QWidget()
        tab_matches = QtGui.QWidget()

        # Resize width and height
        tabs.resize(250, 150)

        # Add tabs
        tabs.addTab(self.setup_settings(), 'Settings')
        tabs.addTab(tab_liked, 'Liked')
        tabs.addTab(tab_disliked, 'Disliked')
        tabs.addTab(self.setup_browse(), 'Browse')
        tabs.addTab(tab_matches, 'Matches')

        # Set main window layout
        self.setCentralWidget(tabs)
        self.show()

    def setup_settings(self):
        # Set layout of settings tab
        tab_settings = QtGui.QWidget()
        label_location = QtGui.QLabel('Location:')
        label_auth = QtGui.QLabel('Facebook Auth Token:')
        label_id = QtGui.QLabel('Facebook Profile ID:')
        label_img_threshold = QtGui.QLabel('Image Search Threshold:')
        label_face_threshold = QtGui.QLabel('Faces Found Threshold:')
        label_bio_threshold = QtGui.QLabel('Biography Threshold:')
        label_pickup_threshold = QtGui.QLabel('Pick-up after X Messages:')

        btn_save = QtGui.QPushButton('Save Settings', self)
        btn_save.setFixedHeight(50)
        btn_save.clicked.connect(self.save_settings)
        btn_start = QtGui.QPushButton('Start Pinning', self)
        btn_start.setFixedHeight(50)

        self.label_status.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_id.setEchoMode(QtGui.QLineEdit.Password)
        self.txt_auth.setEchoMode(QtGui.QLineEdit.Password)
        self.txt_img_threshold.setValidator(QtGui.QIntValidator())
        self.txt_face_threshold.setValidator(QtGui.QIntValidator())
        self.txt_bio_threshold.setValidator(QtGui.QIntValidator())
        self.txt_pickup_threshold.setValidator(QtGui.QIntValidator())
        self.chk_decision.setStyleSheet(self.CSS_FONT_CATEGORY)
        self.chk_decision.stateChanged.connect(self.decision_change)
        self.chk_autochat.setStyleSheet(self.CSS_FONT_CATEGORY)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.label_status, 1, 0, 1, 2)
        grid.addWidget(label_location, 2, 0)
        grid.addWidget(self.txt_location, 2, 1)
        grid.addWidget(label_auth, 3, 0)
        grid.addWidget(self.txt_auth, 3, 1)
        grid.addWidget(label_id, 4, 0)
        grid.addWidget(self.txt_id, 4, 1)
        grid.addWidget(horizontal_line(), 5, 0, 1, 2)
        grid.addWidget(self.chk_decision, 6, 0, 1, 2)
        grid.addWidget(label_img_threshold, 7, 0)
        grid.addWidget(self.txt_img_threshold, 7, 1)
        grid.addWidget(label_face_threshold, 8, 0)
        grid.addWidget(self.txt_face_threshold, 8, 1)
        grid.addWidget(label_bio_threshold, 9, 0)
        grid.addWidget(self.txt_bio_threshold, 9, 1)
        grid.addWidget(horizontal_line(), 10, 0, 1, 2)
        grid.addWidget(self.chk_autochat, 11, 0, 1, 2)
        grid.addWidget(self.chk_respond_list, 12, 0, 1, 2)
        grid.addWidget(self.chk_respond_bot, 13, 0, 1, 2)
        grid.addWidget(label_pickup_threshold, 14, 0)
        grid.addWidget(self.txt_pickup_threshold, 14, 1)
        grid.addWidget(horizontal_line(), 15, 0, 1, 2)
        grid.addWidget(btn_save, 16, 0)
        grid.addWidget(btn_start, 16, 1)

        tab_settings.setLayout(grid)
        return tab_settings

    def setup_browse(self):
        tab_browse = QtGui.QWidget()
        scroll = QtGui.QScrollArea()
        btn_refresh = QtGui.QPushButton('Refresh', self)
        btn_refresh.clicked.connect(lambda: (self.refresh_users(scroll, btn_refresh)))
        tab_browse.setLayout(QtGui.QVBoxLayout())
        tab_browse.layout().addWidget(btn_refresh)
        tab_browse.layout().addWidget(scroll)
        self.refresh_users(scroll, btn_refresh)
        return tab_browse

    def refresh_users(self, list_area, refresh_button):
        def nearby_users_fetched(data):
            refresh_button.setText('Refresh')
            refresh_button.setDisabled(False)
            list_area.setWidget(self.populate_users(data))

        if self.session:
            nearby_users = NearbyUsersThread(self.session)
            nearby_users.data_downloaded.connect(nearby_users_fetched)
            nearby_users.start()

            # Show loading screen in the meantime.
            refresh_button.setText('Refreshing...')
            refresh_button.setDisabled(True)
            loading = QtGui.QWidget()
            loading.setLayout(QtGui.QHBoxLayout())
            loading_icon = QtGui.QMovie('../resources/icons/heart-32x32.gif')
            loading_label = QtGui.QLabel()
            loading_label.setMovie(loading_icon)
            loading_icon.start()
            loading.layout().addWidget(QtGui.QLabel('Loading...'))
            loading.layout().addWidget(loading_label)
            list_area.setWidget(loading)
        else:
            label_noauth = QtGui.QLabel('Not connected. Please enter correct authentication details in Settings tab.')
            noauth = QtGui.QWidget()
            noauth.setLayout(QtGui.QVBoxLayout())
            noauth.layout().addWidget(label_noauth)
            list_area.setWidget(noauth)

    def populate_users(self, user_list):
        user_list_widget = QtGui.QWidget()
        user_list_widget.setLayout(QtGui.QVBoxLayout())

        # Populate the list with users if available.
        for user in user_list:
            # Thumbnail
            try:
                thumbnail = QtGui.QImage()
                thumbnail.loadFromData(user.thumb_data)
                label_thumbnail = QtGui.QLabel()
                label_thumbnail.setFixedWidth(self.THUMBNAIL_SIZE)
                label_thumbnail.setFixedHeight(self.THUMBNAIL_SIZE)
                label_thumbnail.setScaledContents(True)
                label_thumbnail.setPixmap(QtGui.QPixmap(thumbnail))
                # IMPORTANT: lambda user=user forces a capture of the variable into the anonymous scope. Don't remove.
                # Otherwise, the 'user' variable will just be a reference, and won't reflect the user assigned in loop.
                clickable(label_thumbnail).connect(lambda user=user:
                                                   (self.windows.append(ImageWindow(user.name, user.photos))))
            except Exception as ex:
                print('User population error: ' + str(ex))  # Doesn't matter, ignore if this user fails to populate.
                continue

            # Name
            if user.gender.lower() == 'female':
                gender_string = '<span style="color: DeepPink;' + self.CSS_FONT_EMOJI + '"> ♀ </span>'
            else:
                gender_string = '<span style="color: DodgerBlue;' + self.CSS_FONT_EMOJI + '"> ♂ </span>'
            name_string = '<span style="' + self.CSS_FONT_HEADLINE + '">' + user.name \
                          + gender_string + '(' + str(user.age) + ')' + '</span>'
            label_name = QtGui.QLabel(name_string)
            label_name.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

            # Date of Birth
            label_dob = QtGui.QLabel('<b>Birthday: </b>' + user.birth_date.strftime("%B %d, %Y"))
            label_dob.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

            # Distance
            label_distance = QtGui.QLabel('<b>Distance: </b>' + "{0:.2f}".format(user.distance_km) + 'km')
            label_distance.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

            # Last Ping (Last Known Active Time)
            ping = user.ping_time[:-5].split('T')  # Removes the last few characters and splits the date and time.
            label_ping = QtGui.QLabel('<b>Last Seen: </b>' + ping[1] + ' on ' + ping[0])
            label_ping.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

            # Schools
            if user.schools:
                schools = ", ".join(str(x) for x in user.schools)
            else:
                schools = 'None.'
            label_schools = QtGui.QLabel('<b>Schools: </b>' + schools)
            label_schools.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

            # Occupation
            if user.jobs:
                jobs = ", ".join(str(x) for x in user.jobs)
            else:
                jobs = 'None.'
            label_jobs = QtGui.QLabel('<b>Occupation: </b>' + jobs)
            label_jobs.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

            # Biography
            if user.bio:
                txt_bio = QtGui.QLabel(user.bio)
            else:
                txt_bio = QtGui.QLabel('No biography found.')
            txt_bio.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            txt_bio.setStyleSheet(self.CSS_FONT_EMOJI)

            # Like, dislike and super like buttons.
            btn_like = QtGui.QPushButton('Like', self)
            #btn_like.clicked.connect(user.like)
            btn_dislike = QtGui.QPushButton('Dislike', self)
            #btn_like.clicked.connect(user.dislike)
            btn_superlike = QtGui.QPushButton('Super Like', self)
            #btn_like.clicked.connect(user.superlike)
            like_buttons_layout = QtGui.QHBoxLayout()
            like_buttons_layout.addWidget(btn_like)
            like_buttons_layout.addWidget(btn_dislike)
            like_buttons_layout.addWidget(btn_superlike)

            card = QtGui.QWidget()
            card_layout = QtGui.QGridLayout()
            card_layout.setSpacing(10)
            card_layout.addWidget(label_thumbnail, 1, 0, 8, 1)
            card_layout.addWidget(label_name, 1, 1)
            card_layout.addWidget(label_dob, 2, 1)
            card_layout.addWidget(label_distance, 3, 1)
            card_layout.addWidget(label_ping, 4, 1)
            card_layout.addWidget(label_schools, 5, 1)
            card_layout.addWidget(label_jobs, 6, 1)
            card_layout.addWidget(txt_bio, 7, 1)
            card_layout.addLayout(like_buttons_layout, 8, 1)
            card.setLayout(card_layout)
            user_list_widget.layout().addWidget(card)

        return user_list_widget



    '''
        +================================================================+
        | HANDLING METHODS: Events, background, saving preferences, etc. |
        +================================================================+
    '''
    def closeEvent(self, event):
        for window in self.windows:
            window.close()  # Close all windows associated with this window.

    def connect_tinder(self):
        status_text = 'Tinder Status: '

        def session_connected(data):
            if isinstance(data, Exception):
                self.session = None
                self.label_status.setText(status_text + '<span style="color:red;font-weight:bold">Offline</span>')
                QtGui.QMessageBox.critical(self, 'Error', str(data))
            else:
                self.session = data
                self.label_status.setText(status_text + '<span style="color:green;font-weight:bold">Online</span>')

        if self.txt_location.text() and self.txt_id.text() and self.txt_auth.text():
            self.session_thread = SessionThread(self.txt_id.text(), self.txt_auth.text(), self.txt_location.text())
            self.session_thread.data_downloaded.connect(session_connected)
            self.session_thread.start()
            self.label_status.setText(status_text + '<span style="color:orange;font-weight:bold">Connecting...</span>')
        else:
            self.session = None
            self.label_status.setText(status_text + '<span style="color:red;font-weight:bold">Offline</span>')
            QtGui.QMessageBox.information(self, 'Connect to Tinder', 'In order to start using Pinsey, you will need '
                                                                     'to key in your rough location (similar to how '
                                                                     'you would search on Google Maps), Facebook '
                                                                     'authentication token from Tinder, and Facebook '
                                                                     'profile ID. Then, click Save Settings and it '
                                                                     'will start connecting to Tinder.\n\n'
                                                                     'If you are unsure how to obtain some of the '
                                                                     'values required, please visit: '
                                                                     '<a href="http://railkill.com/pinsey">'
                                                                     'http://railkill.com/pinsey</a>')

    def decision_change(self):
        """Handles decision-making checkbox state change."""
        if self.chk_decision.isChecked():
            self.txt_img_threshold.setDisabled(False)
            self.txt_face_threshold.setDisabled(False)
            self.txt_bio_threshold.setDisabled(False)
        else:
            self.txt_img_threshold.setDisabled(True)
            self.txt_face_threshold.setDisabled(True)
            self.txt_bio_threshold.setDisabled(True)

    def read_settings(self):
        """Reads saved user preferences and loads it into the application. Otherwise, load defaults."""
        config = ConfigParser()
        if config.read('config.ini'):
            self.txt_location.setText(config.get('Authentication', 'location'))
            self.txt_auth.setText(config.get('Authentication', 'auth'))
            self.txt_id.setText(config.get('Authentication', 'id'))
            self.txt_id.setText(config.get('Authentication', 'id'))

            self.chk_decision.setChecked(config.getboolean('Decision', 'enabled'))
            self.txt_img_threshold.setText(config.get('Decision', 'img_threshold'))
            self.txt_face_threshold.setText(config.get('Decision', 'face_threshold'))
            self.txt_bio_threshold.setText(config.get('Decision', 'bio_threshold'))

            self.chk_autochat.setChecked(config.getboolean('Chat', 'enabled'))
            self.chk_respond_list.setChecked(config.getboolean('Chat', 'respond_list'))
            self.chk_respond_bot.setChecked(config.getboolean('Chat', 'respond_bot'))
            self.txt_pickup_threshold.setText(config.get('Chat', 'pickup_threshold'))

    def save_settings(self):
        config = ConfigParser()
        config.read('config.ini')
        try:
            config.add_section('Authentication')
        except DuplicateSectionError:
            pass
        config.set('Authentication', 'location', self.txt_location.text())
        config.set('Authentication', 'auth', self.txt_auth.text())
        config.set('Authentication', 'id', self.txt_id.text())

        try:
            config.add_section('Decision')
        except DuplicateSectionError:
            pass
        config.set('Decision', 'enabled', str(self.chk_decision.isChecked()))
        config.set('Decision', 'img_threshold', self.txt_img_threshold.text())
        config.set('Decision', 'face_threshold', self.txt_face_threshold.text())
        # TODO: insert filepath of cascade, for user customizability
        config.set('Decision', 'bio_threshold', self.txt_bio_threshold.text())

        try:
            config.add_section('Chat')
        except DuplicateSectionError:
            pass
        config.set('Chat', 'enabled', str(self.chk_autochat.isChecked()))
        config.set('Chat', 'respond_list', str(self.chk_respond_list.isChecked()))
        # TODO: insert filepath of response list, for user customizability
        config.set('Chat', 'respond_bot', str(self.chk_respond_bot.isChecked()))
        config.set('Chat', 'pickup_threshold', self.txt_pickup_threshold.text())

        with open('config.ini', 'w') as f:
            config.write(f)
        QtGui.QMessageBox.information(self, 'Information', 'Settings saved.')
        self.connect_tinder()