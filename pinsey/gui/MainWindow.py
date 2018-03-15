from configparser import ConfigParser
from configparser import DuplicateSectionError
from PyQt5 import QtCore, QtGui, QtWidgets

from pinsey import Constants
from pinsey.Utils import clickable, center, picture_grid, horizontal_line, resolve_message_sender, name_set, windows
from pinsey.gui.MessageWindow import MessageWindow
from pinsey.gui.component.BrowseListing import BrowseListing
from pinsey.gui.component.DislikesListing import DislikesListing
from pinsey.gui.component.LikesListing import LikesListing
from pinsey.handler.DecisionHandler import DecisionHandler
from pinsey.handler.LikesHandler import LikesHandler
from pinsey.thread.DownloadPhotosThread import DownloadPhotosThread
from pinsey.thread.LikesBotThread import LikesBotThread
from pinsey.thread.SessionThread import SessionThread
from pinsey.thread.MatchesThread import MatchesThread


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()

        # Initialize Window GUI controls.
        self.label_status = QtWidgets.QLabel()
        self.txt_location = QtWidgets.QLineEdit()
        self.txt_auth = QtWidgets.QLineEdit()
        self.txt_id = QtWidgets.QLineEdit()
        self.txt_img_threshold = QtWidgets.QLineEdit()
        self.txt_face_threshold = QtWidgets.QLineEdit()
        self.txt_bio_threshold = QtWidgets.QLineEdit()
        self.txt_pickup_threshold = QtWidgets.QLineEdit()
        self.chk_decision = QtWidgets.QCheckBox('Decision-Making', self)
        self.chk_exclude_friends = QtWidgets.QCheckBox('Exclude Facebook Friends', self)
        self.chk_exclude_mutual = QtWidgets.QCheckBox('Exclude Mutual Friends', self)
        self.chk_autochat = QtWidgets.QCheckBox('Autonomous Chatting', self)
        self.chk_respond_list = QtWidgets.QCheckBox('Respond from List', self)
        self.chk_respond_bot = QtWidgets.QCheckBox('Respond using Cleverbot', self)
        self.profile_area = QtWidgets.QScrollArea()
        self.matches_area = QtWidgets.QScrollArea()
        self.chk_refresh = QtWidgets.QCheckBox('Refresh every: ')
        self.txt_refresh_interval = QtWidgets.QLineEdit()

        # Initialize system tray icon and menu.
        tray_menu = QtWidgets.QMenu()
        restore_action = tray_menu.addAction('Restore')
        restore_action.triggered.connect(self.restore_window)
        close_action = tray_menu.addAction('Exit')
        close_action.triggered.connect(self.close)
        self.tray_icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon(Constants.ICON_FILEPATH))
        self.tray_icon.activated.connect(self.tray_event)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Initialize application variables.
        self.app = app
        self.session = None
        self.friend_list = []
        self.download_thread = []
        self.matches_thread = None
        self.session_thread = None
        self.likes_bot = None
        self.likes_handler = LikesHandler()
        self.filter_list = ['Date Added', 'Name', 'Age', 'Distance KM']
        self.likeslisting = LikesListing('Reload', self.likes_handler, self.filter_list)
        self.dislikeslisting = DislikesListing('Reload', self.likes_handler, self.filter_list)
        self.browselisting = BrowseListing('Refresh', self.likes_handler, self.filter_list[1:])
        self.setWindowTitle(Constants.APP_NAME)
        self.setWindowIcon(QtGui.QIcon(Constants.ICON_FILEPATH))
        self.setMinimumWidth(500)
        self.resize(800, 480)
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
        tabs = QtWidgets.QTabWidget()
        # Resize width and height
        tabs.resize(250, 150)

        # Add tabs
        tabs.addTab(self.setup_settings(), 'Settings')
        tabs.addTab(self.setup_profile(), 'Profile')

        tabs.addTab(self.likeslisting, 'Liked')
        tabs.addTab(self.dislikeslisting, 'Disliked')
        tabs.addTab(self.browselisting, 'Browse')
        tabs.addTab(self.setup_matches(), 'Matches')

        # Set main window layout
        self.setCentralWidget(tabs)
        self.show()

    def setup_settings(self):
        # Set layout of settings tab
        tab_settings = QtWidgets.QWidget()
        label_location = QtWidgets.QLabel('Location:')
        label_auth = QtWidgets.QLabel('Facebook Auth Token:')
        label_id = QtWidgets.QLabel('Facebook Profile ID:')
        label_img_threshold = QtWidgets.QLabel('Minimum Number of Good Images:')
        label_face_threshold = QtWidgets.QLabel('Faces Found Threshold:')
        label_bio_threshold = QtWidgets.QLabel('Biography Minimum Length:')
        label_friend_exclusion = QtWidgets.QLabel('Friend Exclusion: ')
        label_pickup_threshold = QtWidgets.QLabel('Pick-up after X Messages:')

        btn_save = QtWidgets.QPushButton('Save Settings', self)
        btn_save.setFixedHeight(50)
        btn_save.clicked.connect(self.save_settings)
        btn_start = QtWidgets.QPushButton('Start Pinning', self)
        btn_start.clicked.connect(lambda: self.start_botting(btn_start))
        btn_start.setFixedHeight(50)

        exclusion_widget = QtWidgets.QWidget()
        exclusion_widget.setLayout(QtWidgets.QHBoxLayout())
        exclusion_widget.layout().addWidget(self.chk_exclude_friends)
        exclusion_widget.layout().addWidget(self.chk_exclude_mutual)
        exclusion_widget.layout().addStretch()

        self.label_status.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_id.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txt_auth.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txt_img_threshold.setValidator(QtGui.QIntValidator())
        self.txt_face_threshold.setValidator(QtGui.QIntValidator())
        self.txt_bio_threshold.setValidator(QtGui.QIntValidator())
        self.txt_pickup_threshold.setValidator(QtGui.QIntValidator())
        self.chk_decision.setStyleSheet(Constants.CSS_FONT_CATEGORY)
        self.chk_decision.stateChanged.connect(self.decision_change)
        self.chk_autochat.setStyleSheet(Constants.CSS_FONT_CATEGORY)

        grid = QtWidgets.QGridLayout()
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
        grid.addWidget(label_friend_exclusion, 10, 0)
        grid.addWidget(exclusion_widget, 10, 1)
        grid.addWidget(horizontal_line(), 11, 0, 1, 2)
        grid.addWidget(self.chk_autochat, 12, 0, 1, 2)
        grid.addWidget(self.chk_respond_list, 13, 0, 1, 2)
        grid.addWidget(self.chk_respond_bot, 14, 0, 1, 2)
        grid.addWidget(label_pickup_threshold, 15, 0)
        grid.addWidget(self.txt_pickup_threshold, 15, 1)
        grid.addWidget(horizontal_line(), 16, 0, 1, 2)
        grid.addWidget(btn_save, 17, 0)
        grid.addWidget(btn_start, 17, 1)

        tab_settings.setLayout(grid)
        return tab_settings

    def setup_profile(self):
        tab_profile = QtWidgets.QWidget()
        tab_profile.setLayout(QtWidgets.QVBoxLayout())
        tab_profile.layout().addWidget(self.profile_area)
        return tab_profile

    def setup_matches(self):
        tab_matches = QtWidgets.QWidget()
        tab_matches.setLayout(QtWidgets.QVBoxLayout())

        match_refresh_widget = QtWidgets.QWidget()
        match_refresh_widget.setLayout(QtWidgets.QHBoxLayout())
        self.txt_refresh_interval.setValidator(QtGui.QIntValidator(10, 300))
        self.txt_refresh_interval.setText("60")  # Default 60 second refresh interval
        lbl_refresh_unit = QtWidgets.QLabel('seconds')
        match_refresh_widget.layout().addWidget(self.chk_refresh)
        match_refresh_widget.layout().addWidget(self.txt_refresh_interval)
        match_refresh_widget.layout().addWidget(lbl_refresh_unit)
        match_refresh_widget.layout().addStretch()
        btn_refresh = QtWidgets.QPushButton('Refresh', self)
        btn_refresh.clicked.connect(self.load_matches)
        match_refresh_widget.layout().addWidget(btn_refresh)

        tab_matches.layout().addWidget(match_refresh_widget)
        tab_matches.layout().addWidget(self.matches_area)
        return tab_matches

    def load_profile(self):
        def populate(data, thread):
            self.download_thread.remove(thread)
            profile_widget = QtWidgets.QWidget()
            profil = self.session.profile

            # 1. Profile picture grid.
            number_of_photos = Constants.NUMBER_OF_PHOTOS
            pp_layout = picture_grid(data, Constants.THUMBNAIL_SIZE, number_of_photos)

            # 2. Name and gender of user.
            label_name = name_set(profil.name, profil.gender, 0, profil.banned)
            pp_layout.addWidget(label_name, number_of_photos, 0, 1, number_of_photos)

            # 3. Biography.
            def bio_truncate():
                # Tinder counts emojis as 2 characters. Find and manipulate them so the character count is correct.
                emoji_raw = Constants.EMOJI_PATTERN.findall(txt_bio.toPlainText())
                number_of_emojis = 0
                for emoji in emoji_raw:
                    number_of_emojis += len(emoji)

                # Encode to UTF-8, emojis are counted as 4 characters.
                bio_true_length = len(txt_bio.toPlainText().encode()) - (number_of_emojis * 2)
                label_chars.setText(str(biography_max_length - len(txt_bio.toPlainText().encode()) +
                                        (number_of_emojis * 2)) + remaining_chars)
                if bio_true_length > biography_max_length:
                    txt_bio.setPlainText(txt_bio.toPlainText()[:biography_max_length - number_of_emojis])
                    txt_bio.moveCursor(QtGui.QTextCursor.End)

            biography_max_length = 500
            label_bio = QtWidgets.QLabel('Biography: ')
            remaining_chars = ' characters remaining'
            label_chars = QtWidgets.QLabel(str(biography_max_length) + remaining_chars)
            bio_widget = QtWidgets.QWidget()
            bio_widget.setLayout(QtWidgets.QHBoxLayout())
            bio_widget.layout().addWidget(label_bio)
            bio_widget.layout().addStretch()
            bio_widget.layout().addWidget(label_chars)
            pp_layout.addWidget(bio_widget, number_of_photos + 1, 0, 1, number_of_photos)

            # Profile may have no biography yet.
            try:
                bio_text = profil.bio
            except KeyError:
                bio_text = ''

            txt_bio = QtWidgets.QPlainTextEdit(bio_text)
            txt_bio.setFont(QtGui.QFont('Segoe UI Symbol', 16))
            txt_bio.textChanged.connect(bio_truncate)
            bio_truncate()
            pp_layout.addWidget(txt_bio, number_of_photos + 2, 0, 1, number_of_photos)

            # Form layout setup.
            form_layout = QtWidgets.QFormLayout()
            # form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
            form_widget = QtWidgets.QWidget()
            form_widget.setLayout(form_layout)
            pp_layout.addWidget(form_widget, number_of_photos + 3, 0, 1, number_of_photos)
            form_label_style = 'margin-top: 0.3em'

            # 4. Gender
            radio_gender_male = QtWidgets.QRadioButton('Male')
            radio_gender_female = QtWidgets.QRadioButton('Female')
            if profil.gender == 'male':
                radio_gender_male.setChecked(True)
            else:
                radio_gender_female.setChecked(True)
            gender_widget = QtWidgets.QWidget()
            gender_widget.setLayout(QtWidgets.QHBoxLayout())
            gender_widget.layout().addWidget(radio_gender_male)
            gender_widget.layout().addWidget(radio_gender_female)
            label_gender = QtWidgets.QLabel('Gender: ')
            label_gender.setStyleSheet(form_label_style)
            form_layout.addRow(label_gender, gender_widget)

            # 5. Discoverable?
            label_discoverable = QtWidgets.QLabel('Discoverable: ')
            chk_discoverable = QtWidgets.QCheckBox()
            chk_discoverable.setChecked(profil.discoverable)
            form_layout.addRow(label_discoverable, chk_discoverable)

            # 6. Maximum distance filter.
            label_distance = QtWidgets.QLabel('Maximum Distance: ')
            label_distance.setStyleSheet(form_label_style)
            slider_distance = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider_distance.setRange(1, 100)
            slider_distance.setSingleStep(1)
            slider_distance.setValue(profil.distance_filter)
            slider_distance.valueChanged.connect(
                lambda: (label_distance_value.setText(str(round(slider_distance.value() * 1.6)) + 'km')))
            label_distance_value = QtWidgets.QLabel(str(round(slider_distance.value() * 1.6)) + 'km')
            distance_widget = QtWidgets.QWidget()
            distance_widget.setLayout(QtWidgets.QHBoxLayout())
            distance_widget.layout().addWidget(slider_distance)
            distance_widget.layout().addWidget(label_distance_value)
            form_layout.addRow(label_distance, distance_widget)

            # 7. Age filter.
            def max_slider_handle():
                label_age_max.setText('55+' if slider_age_max.value() > 54 else str(slider_age_max.value()))
                slider_age_min.setRange(18, 46 if slider_age_max.value() > 46 else slider_age_max.value())

            def min_slider_handle():
                label_age_min.setText(str(slider_age_min.value()))
                slider_age_max.setRange(slider_age_min.value(), 55)

            label_age = QtWidgets.QLabel('Age: ')
            label_age.setStyleSheet(form_label_style)
            label_to = QtWidgets.QLabel(' to ')
            slider_age_max = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider_age_max.setRange(profil.age_filter_min, 55)
            slider_age_max.setSingleStep(1)
            slider_age_max.setValue(55 if profil.age_filter_max > 54 else profil.age_filter_max)
            slider_age_max.valueChanged.connect(max_slider_handle)
            label_age_max = QtWidgets.QLabel('55+' if slider_age_max.value() > 54 else str(slider_age_max.value()))

            slider_age_min = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider_age_min.setRange(18, 46 if profil.age_filter_max > 46 else profil.age_filter_max)
            slider_age_min.setSingleStep(1)
            slider_age_min.setValue(profil.age_filter_min)
            slider_age_min.valueChanged.connect(min_slider_handle)
            label_age_min = QtWidgets.QLabel(str(slider_age_min.value()))

            age_widget = QtWidgets.QWidget()
            age_widget.setLayout(QtWidgets.QHBoxLayout())
            age_widget.layout().addWidget(label_age_min)
            age_widget.layout().addWidget(slider_age_min)
            age_widget.layout().addWidget(label_to)
            age_widget.layout().addWidget(slider_age_max)
            age_widget.layout().addWidget(label_age_max)
            form_layout.addRow(label_age, age_widget)

            # 8. Interested in which gender?
            label_interested = QtWidgets.QLabel('Interested in: ')
            label_interested.setStyleSheet(form_label_style)
            chk_interested_male = QtWidgets.QCheckBox('Male')
            chk_interested_male.setChecked('male' in list(profil.interested_in))
            chk_interested_female = QtWidgets.QCheckBox('Female')
            chk_interested_female.setChecked('female' in list(profil.interested_in))
            interested_widget = QtWidgets.QWidget()
            interested_widget.setLayout(QtWidgets.QHBoxLayout())
            interested_widget.layout().addWidget(chk_interested_male)
            interested_widget.layout().addWidget(chk_interested_female)
            form_layout.addRow(label_interested, interested_widget)

            # 9. Save button.
            def save_profile():
                # Must have an interested gender before proceeding.
                if not chk_interested_male.isChecked() and not chk_interested_female.isChecked():
                    QtWidgets.QMessageBox().critical(self, 'Profile Error',
                                                 'You must be interested in at least one gender.')
                    return

                # Set profile values.
                try:
                    profile.bio = txt_bio.toPlainText()
                except KeyError:
                    self.session.update_profile({
                        "bio": txt_bio.toPlainText()
                    })
                profile.discoverable = chk_discoverable.isChecked()
                profile.distance_filter = slider_distance.value()
                profile.age_filter_min = slider_age_min.value()
                profile.age_filter_max = 1000 if slider_age_max.value() > 54 else slider_age_max.value()

                # Workaround due to pynder 0.0.13 not yet supporting "gender" and "interested in" changes.
                gender_filter = 2
                profil.interested = []
                profil.sex = (0, 'male') if radio_gender_male.isChecked() else (1, 'female')
                if chk_interested_male.isChecked():
                    gender_filter -= 2
                    profil.interested.append(0)
                if chk_interested_female.isChecked():
                    gender_filter -= 1
                    profil.interested.append(1)
                self.session.update_profile({
                    "interested_in": profil.interested,
                    "gender_filter": gender_filter,
                    "gender": profil.sex[0]
                    # "squads_discoverable": False
                })

                QtWidgets.QMessageBox.information(self, 'Profile Saved', 'Profile information has been updated.')
                reload_profile()

            def reload_profile():
                # Refresh GUI.
                label_name.setText(name_set(profil.name, profil.sex[1], 0, profil.banned).text())
                try:
                    txt_bio.setPlainText(profil.bio)
                except KeyError:
                    txt_bio.setPlainText('')
                chk_discoverable.setChecked(profil.discoverable)
                slider_distance.setValue(profil.distance_filter)
                label_distance_value.setText(str(round(slider_distance.value() * 1.6)) + 'km')
                slider_age_max.setRange(profil.age_filter_min, 55)
                slider_age_max.setValue(55 if profil.age_filter_max > 54 else profil.age_filter_max)
                label_age_max.setText('55+' if slider_age_max.value() > 54 else str(slider_age_max.value()))
                slider_age_min.setRange(18, 46 if profil.age_filter_max > 46 else profil.age_filter_max)
                slider_age_min.setValue(profil.age_filter_min)
                label_age_min.setText(str(slider_age_min.value()))
                chk_interested_male.setChecked(0 in list(profil.interested))  # interested_in workaround.
                chk_interested_female.setChecked(1 in list(profil.interested))  # interested_in workaround.

            btn_save_profile = QtWidgets.QPushButton('Update Profile')
            btn_save_profile.setFixedHeight(50)
            btn_save_profile.clicked.connect(save_profile)
            pp_layout.addWidget(btn_save_profile, number_of_photos + 4, 0, 1, number_of_photos)

            profile_widget.setLayout(pp_layout)
            self.profile_area.setWidget(profile_widget)
            self.profile_area.setAlignment(QtCore.Qt.AlignCenter)

        # Download profile images and then populate the profile GUI.
        profile = self.session.profile
        download_thread = DownloadPhotosThread(profile.photos)
        download_thread.data_downloaded.connect(lambda data, thread=download_thread: populate(data, thread))
        self.download_thread.append(download_thread)
        download_thread.start()

    def load_matches(self, interval=0):
        def load_thumbnail(photo, label, thread):
            self.download_thread.remove(thread)
            thumbnail = QtGui.QImage()
            thumbnail.loadFromData(photo[0].data)
            label.setPixmap(QtGui.QPixmap(thumbnail))

        def populate_matches(data):
            matches = data
            updates = list(self.session.updates())
            updates_balloon_message = ''

            matches_list = QtWidgets.QWidget()
            matches_list.setLayout(QtWidgets.QVBoxLayout())
            for match in matches:
                # Show notification if it is in updates.
                for update in updates:
                    if match.user.id == update.user.id:
                        updates_balloon_message += update.user.name
                        if not update.messages:
                            updates_balloon_message += ' (NEW) '
                        updates_balloon_message += '\n'

                # Load thumbnail of match.
                label_thumbnail = QtWidgets.QLabel()
                label_thumbnail.setFixedWidth(Constants.THUMBNAIL_SIZE / 2)
                label_thumbnail.setFixedHeight(Constants.THUMBNAIL_SIZE / 2)
                label_thumbnail.setScaledContents(True)
                download_thread = DownloadPhotosThread([next(match.user.photos)])
                download_thread.data_downloaded.connect(
                    lambda data, l=label_thumbnail, t=download_thread: load_thumbnail(data, l, t)
                )
                self.download_thread.append(download_thread)
                download_thread.start()

                # Create name set.
                label_name = name_set(match.user.name, match.user.gender, match.user.age)
                # Create match date label.
                label_match_date = QtWidgets.QLabel('<b>Match Date: </b>' +
                                                    match.match_date.strftime("%B %d, %Y at %I:%M%p"))
                # Create last message text.
                if match.messages:
                    last_message = match.messages[len(match.messages) - 1]
                    last_poster = resolve_message_sender(last_message, match)
                    display_message = last_poster + last_message.body
                else:
                    display_message = 'Conversation not started.'

                label_last_message = QtWidgets.QLabel(display_message)
                # Create notification text.
                label_notification = QtWidgets.QLabel('NEW UPDATE!' if match in updates else '')
                label_notification.setStyleSheet(Constants.CSS_FONT_NOTIFICATION)

                # Create a card for each match.
                card_widget = QtWidgets.QWidget()
                card_layout = QtWidgets.QGridLayout()
                card_layout.setSpacing(10)
                card_layout.addWidget(label_thumbnail, 1, 0, 5, 1)
                card_layout.addWidget(label_name, 1, 1)
                card_layout.addWidget(label_match_date, 2, 1)
                card_layout.addWidget(label_last_message, 3, 1)
                card_layout.addWidget(label_notification, 4, 1)
                card_widget.setLayout(card_layout)
                clickable(card_widget).connect(lambda m=match: (
                    windows.append(MessageWindow(m, self.friend_list))
                ))
                matches_list.layout().addWidget(card_widget)

                # Check if any MessageWindow for this match. If there is, update the messages area.
                for window in windows:
                    if isinstance(window, MessageWindow) and match == window.match:
                        window.load_messages(match.messages)

            self.matches_area.setWidget(matches_list)
            self.matches_area.setAlignment(QtCore.Qt.AlignCenter)
            if updates_balloon_message:
                self.tray_icon.showMessage('Pinsey: New Update!', updates_balloon_message)

            if self.chk_refresh.isChecked():
                self.load_matches(int(self.txt_refresh_interval.text()))

        self.matches_thread = MatchesThread(self.session, interval)
        self.matches_thread.data_downloaded.connect(populate_matches)
        self.matches_thread.start()

    '''
        +================================================================+
        | HANDLING METHODS: Events, background, saving preferences, etc. |
        +================================================================+
    '''
    def closeEvent(self, event):
        for window in windows:
            window.close()  # Close all windows associated with this window.
        super(MainWindow, self).closeEvent(event)
        self.app.exit()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            # TODO: Check if windowState = 3, happens when minimize on fullscreen window.
            if self.windowState() == QtCore.Qt.WindowMinimized:
                for window in windows:
                    window.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)  # Required to properly hide window.
                    window.hide()  # Hides all windows associated with this window.
                self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)  # Required to properly hide window.
                self.hide()

    def tray_event(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.restore_window()

    def restore_window(self):
        if self.isHidden():
            for window in windows:
                window.setWindowFlags(self.windowFlags() & ~QtCore.Qt.Tool)  # Required to properly show window.
                window.showNormal()
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.Tool)  # Required to properly show window.
            self.showNormal()

    def connect_tinder(self):
        def session_connected(data):
            if data.session:
                if data.exception:
                    QtWidgets.QMessageBox.warning(self, 'Warning', str(data.exception))
                self.session = data.session
                self.friend_list = list(self.session.get_fb_friends())
                self.label_status.setText(status_text + '<span style="color:green;font-weight:bold">Online</span>')
                self.load_profile()  # Automatically load profile after session is ready.
                self.load_matches()  # Automatically load matches after session is ready.

                # Update user listing.
                self.likeslisting.friend_list = self.friend_list
                self.likeslisting.refresh()
                self.dislikeslisting.friend_list = self.friend_list
                self.dislikeslisting.refresh()
                self.browselisting.friend_list = self.friend_list
                self.browselisting.session = self.session
            else:
                self.session = None
                self.label_status.setText(status_text + '<span style="color:red;font-weight:bold">Offline</span>')
                QtWidgets.QMessageBox.critical(self, 'Error', str(data.exception))

        status_text = 'Tinder Status: '

        if self.txt_location.text() and self.txt_id.text() and self.txt_auth.text():
            self.session_thread = SessionThread(self.txt_id.text(), self.txt_auth.text(), self.txt_location.text())
            self.session_thread.data_downloaded.connect(session_connected)
            self.session_thread.start()
            self.label_status.setText(status_text + '<span style="color:orange;font-weight:bold">Connecting...</span>')
        else:
            self.session = None
            self.label_status.setText(status_text + '<span style="color:red;font-weight:bold">Offline</span>')
            QtWidgets.QMessageBox.information(self, 'Connect to Tinder', 'In order to start using Pinsey, you will need '
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
            self.chk_exclude_friends.setDisabled(False)
            self.chk_exclude_mutual.setDisabled(False)
        else:
            self.txt_img_threshold.setDisabled(True)
            self.txt_face_threshold.setDisabled(True)
            self.txt_bio_threshold.setDisabled(True)
            self.chk_exclude_friends.setDisabled(True)
            self.chk_exclude_mutual.setDisabled(True)

    def read_settings(self):
        """Reads saved user preferences and loads it into the application. Otherwise, load defaults."""
        config = ConfigParser()
        if config.read(Constants.CONFIG_DATA_DIR + 'config.ini'):
            self.txt_location.setText(config.get('Authentication', 'location'))
            self.txt_auth.setText(config.get('Authentication', 'auth'))
            self.txt_id.setText(config.get('Authentication', 'id'))
            self.txt_id.setText(config.get('Authentication', 'id'))

            self.chk_decision.setChecked(config.getboolean('Decision', 'enabled'))
            self.txt_img_threshold.setText(config.get('Decision', 'img_threshold'))
            self.txt_face_threshold.setText(config.get('Decision', 'face_threshold'))
            self.txt_bio_threshold.setText(config.get('Decision', 'bio_threshold'))
            self.chk_exclude_friends.setChecked(config.getboolean('Decision', 'exclude_friends'))
            self.chk_exclude_mutual.setChecked(config.getboolean('Decision', 'exclude_mutual'))

            self.chk_autochat.setChecked(config.getboolean('Chat', 'enabled'))
            self.chk_respond_list.setChecked(config.getboolean('Chat', 'respond_list'))
            self.chk_respond_bot.setChecked(config.getboolean('Chat', 'respond_bot'))
            self.txt_pickup_threshold.setText(config.get('Chat', 'pickup_threshold'))

    def save_settings(self):
        config = ConfigParser()
        config_path = Constants.CONFIG_DATA_DIR + 'config.ini'
        config.read(config_path)
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
        config.set('Decision', 'exclude_friends', str(self.chk_exclude_friends.isChecked()))
        config.set('Decision', 'exclude_mutual', str(self.chk_exclude_mutual.isChecked()))

        try:
            config.add_section('Chat')
        except DuplicateSectionError:
            pass
        config.set('Chat', 'enabled', str(self.chk_autochat.isChecked()))
        config.set('Chat', 'respond_list', str(self.chk_respond_list.isChecked()))
        # TODO: insert filepath of response list, for user customizability
        config.set('Chat', 'respond_bot', str(self.chk_respond_bot.isChecked()))
        config.set('Chat', 'pickup_threshold', self.txt_pickup_threshold.text())

        with open(config_path, 'w') as f:
            config.write(f)
        QtWidgets.QMessageBox.information(self, 'Information', 'Settings saved.')
        self.connect_tinder()

    def start_botting(self, button):
        if self.session:
            decision_handler = None
            if not self.txt_img_threshold.text():
                self.txt_img_threshold.setText(str(Constants.THRESHOLD_IMG_DEFAULT))
            if not self.txt_face_threshold.text():
                self.txt_face_threshold.setText(str(Constants.THRESHOLD_FACE_DEFAULT))
            if not self.txt_bio_threshold.text():
                self.txt_bio_threshold.setText(str(Constants.THRESHOLD_BIO_DEFAULT))

            if self.chk_decision.isChecked():
                decision_handler = DecisionHandler(
                    int(self.txt_img_threshold.text()),
                    int(self.txt_face_threshold.text()),
                    int(self.txt_bio_threshold.text()),
                    self.chk_exclude_friends.isChecked(),
                    self.chk_exclude_mutual.isChecked()
                )
            self.likes_bot = LikesBotThread(self.session, self.likes_handler, decision_handler)
            self.likes_bot.start()

            if self.chk_autochat.isChecked():
                self.matches_thread.start_bot()

            button.setText('Stop Pinning')
            button.clicked.disconnect()
            button.clicked.connect(lambda: self.stop_botting(button))
        else:
            QtWidgets.QMessageBox.critical(self, 'Unable to Start Pinning', 'You are not connected to Tinder yet.')

    def stop_botting(self, button):
        self.likes_bot.stop()
        self.matches_thread.stop_bot()
        button.setText('Start Pinning')
        button.clicked.disconnect()
        button.clicked.connect(lambda: self.start_botting(button))
