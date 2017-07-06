from configparser import ConfigParser
from configparser import DuplicateSectionError
from PyQt4 import QtGui, QtCore
from pinsey.Utils import clickable, center, horizontal_line, EMOJI_PATTERN
from pinsey.gui.ImageWindow import ImageWindow
from pinsey.handler.LikesHandler import LikesHandler
from pinsey.thread.DownloadPhotosThread import DownloadPhotosThread
from pinsey.thread.NearbyUsersThread import NearbyUsersThread
from pinsey.thread.SessionThread import SessionThread


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

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
        self.profile_area = QtGui.QScrollArea()

        # Initialize application variables.
        self.windows = []
        self.session = None
        self.download_thread = None
        self.likes_handler = LikesHandler()
        self.setWindowTitle('Pinsey')
        self.setWindowIcon(QtGui.QIcon('../resources/icons/logo-128x128.png'))
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
        tabs = QtGui.QTabWidget()
        tab_matches = QtGui.QWidget()

        # Resize width and height
        tabs.resize(250, 150)

        # Add tabs
        tabs.addTab(self.setup_settings(), 'Settings')
        tabs.addTab(self.setup_profile(), 'Profile')
        tabs.addTab(self.setup_userlisting('Reload', self.reload_likes), 'Liked')
        tabs.addTab(self.setup_userlisting('Reload', self.reload_dislikes), 'Disliked')
        tabs.addTab(self.setup_userlisting('Refresh', self.refresh_users), 'Browse')
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

    def setup_profile(self):
        tab_profile = QtGui.QWidget()
        tab_profile.setLayout(QtGui.QVBoxLayout())
        tab_profile.layout().addWidget(self.profile_area)
        return tab_profile

    def setup_userlisting(self, refresh_text, refresh_function):
        tab_userlist = QtGui.QWidget()
        scroll = QtGui.QScrollArea()
        btn_refresh = QtGui.QPushButton(refresh_text, self)
        btn_refresh.clicked.connect(lambda: (refresh_function(scroll, btn_refresh)))
        tab_userlist.setLayout(QtGui.QVBoxLayout())
        tab_userlist.layout().addWidget(btn_refresh)
        tab_userlist.layout().addWidget(scroll)
        refresh_function(scroll, btn_refresh)
        return tab_userlist

    def load_profile(self):
        def populate(data):
            profile_widget = QtGui.QWidget()

            # 1. Profile picture grid.
            pp_layout = QtGui.QGridLayout()
            pp_layout.setSpacing(1)
            number_of_photos_allowed = 6
            photos_half_amount = number_of_photos_allowed / 2
            photos_median = number_of_photos_allowed - photos_half_amount - 1
            median_section_count = 0
            last_section_count = 0

            for i in range(number_of_photos_allowed):
                image = QtGui.QImage()
                label = QtGui.QLabel()

                # Load profile photo data.
                label.setScaledContents(True)
                if i < len(data):
                    image.loadFromData(data[i].data)
                    label.setPixmap(QtGui.QPixmap(image))
                else:
                    label.setText(str(i + 1))
                    label.setAlignment(QtCore.Qt.AlignCenter)
                    label.setStyleSheet('border: 1px solid')

                # Determine photo size for grid arrangement.
                size = self.THUMBNAIL_SIZE
                if i >= photos_half_amount:
                    size /= photos_half_amount
                    pp_layout.addWidget(label, last_section_count * photos_median, 2, photos_median, 1)
                    last_section_count += 1
                elif i > 0:
                    size /= photos_median
                    pp_layout.addWidget(label, median_section_count *  photos_half_amount, 1, photos_half_amount, 1)
                    median_section_count += 1
                else:
                    pp_layout.addWidget(label, 0, 0, photos_half_amount * photos_median, 1)
                label.setFixedWidth(size)
                label.setFixedHeight(size)

            # 2. Name and gender of user.
            if profile.gender == 'female':
                gender_string = '<span style="color: DeepPink;' + self.CSS_FONT_EMOJI + '"> ♀ </span>'
            else:
                gender_string = '<span style="color: DodgerBlue;' + self.CSS_FONT_EMOJI + '"> ♂ </span>'
            banned_string = '<span style="color: Red;"> [BANNED] </span>' if profile.banned else ''
            name_string = '<span style="' + self.CSS_FONT_HEADLINE + '">' + profile.name + gender_string + \
                          banned_string + '</span>'
            label_name = QtGui.QLabel(name_string)
            label_name.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            pp_layout.addWidget(label_name, number_of_photos_allowed, 0, 1, number_of_photos_allowed)

            # 3. Biography.
            def bio_truncate():
                # Tinder counts emojis as 2 characters. Find and manipulate them so the character count is correct.
                emoji_raw = EMOJI_PATTERN.findall(txt_bio.toPlainText())
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
            label_bio = QtGui.QLabel('Biography: ')
            remaining_chars = ' characters remaining'
            label_chars = QtGui.QLabel(str(biography_max_length) + remaining_chars)
            bio_widget = QtGui.QWidget()
            bio_widget.setLayout(QtGui.QHBoxLayout())
            bio_widget.layout().addWidget(label_bio)
            bio_widget.layout().addStretch()
            bio_widget.layout().addWidget(label_chars)
            pp_layout.addWidget(bio_widget, number_of_photos_allowed + 1, 0, 1, number_of_photos_allowed)

            txt_bio = QtGui.QPlainTextEdit(profile.bio)
            txt_bio.setFont(QtGui.QFont('Segoe UI Symbol', 16))
            txt_bio.textChanged.connect(bio_truncate)
            bio_truncate()
            pp_layout.addWidget(txt_bio, number_of_photos_allowed + 2, 0, 1, number_of_photos_allowed)

            # Form layout setup.
            form_layout = QtGui.QFormLayout()
            # form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
            form_widget = QtGui.QWidget()
            form_widget.setLayout(form_layout)
            pp_layout.addWidget(form_widget, number_of_photos_allowed + 3, 0, 1, number_of_photos_allowed)
            form_label_style = 'margin-top: 0.3em'

            # 4. Gender
            radio_gender_male = QtGui.QRadioButton('Male')
            radio_gender_female = QtGui.QRadioButton('Female')
            if profile.gender == 'male':
                radio_gender_male.setChecked(True)
            else:
                radio_gender_female.setChecked(True)
            gender_widget = QtGui.QWidget()
            gender_widget.setLayout(QtGui.QHBoxLayout())
            gender_widget.layout().addWidget(radio_gender_male)
            gender_widget.layout().addWidget(radio_gender_female)
            label_gender = QtGui.QLabel('Gender: ')
            label_gender.setStyleSheet(form_label_style)
            form_layout.addRow(label_gender, gender_widget)

            # 5. Discoverable?
            label_discoverable = QtGui.QLabel('Discoverable: ')
            chk_discoverable = QtGui.QCheckBox()
            chk_discoverable.setChecked(profile.discoverable)
            form_layout.addRow(label_discoverable, chk_discoverable)

            # 6. Maximum distance filter.
            label_distance = QtGui.QLabel('Maximum Distance: ')
            label_distance.setStyleSheet(form_label_style)
            slider_distance = QtGui.QSlider(QtCore.Qt.Horizontal)
            slider_distance.setRange(1, 100)
            slider_distance.setSingleStep(1)
            slider_distance.setValue(profile.distance_filter)
            slider_distance.valueChanged.connect(
                lambda: (label_distance_value.setText(str(round(slider_distance.value() * 1.6)) + 'km')))
            label_distance_value = QtGui.QLabel(str(round(slider_distance.value() * 1.6)) + 'km')
            distance_widget = QtGui.QWidget()
            distance_widget.setLayout(QtGui.QHBoxLayout())
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

            label_age = QtGui.QLabel('Age: ')
            label_age.setStyleSheet(form_label_style)
            label_to = QtGui.QLabel(' to ')
            slider_age_max = QtGui.QSlider(QtCore.Qt.Horizontal)
            slider_age_max.setRange(profile.age_filter_min, 55)
            slider_age_max.setSingleStep(1)
            slider_age_max.setValue(55 if profile.age_filter_max > 54 else profile.age_filter_max)
            slider_age_max.valueChanged.connect(max_slider_handle)
            label_age_max = QtGui.QLabel('55+' if slider_age_max.value() > 54 else str(slider_age_max.value()))

            slider_age_min = QtGui.QSlider(QtCore.Qt.Horizontal)
            slider_age_min.setRange(18, 46 if profile.age_filter_max > 46 else profile.age_filter_max)
            slider_age_min.setSingleStep(1)
            slider_age_min.setValue(profile.age_filter_min)
            slider_age_min.valueChanged.connect(min_slider_handle)
            label_age_min = QtGui.QLabel(str(slider_age_min.value()))

            age_widget = QtGui.QWidget()
            age_widget.setLayout(QtGui.QHBoxLayout())
            age_widget.layout().addWidget(label_age_min)
            age_widget.layout().addWidget(slider_age_min)
            age_widget.layout().addWidget(label_to)
            age_widget.layout().addWidget(slider_age_max)
            age_widget.layout().addWidget(label_age_max)
            form_layout.addRow(label_age, age_widget)

            # 8. Interested in which gender?
            label_interested = QtGui.QLabel('Interested in: ')
            label_interested.setStyleSheet(form_label_style)
            chk_interested_male = QtGui.QCheckBox('Male')
            chk_interested_male.setChecked('male' in list(profile.interested_in))
            chk_interested_female = QtGui.QCheckBox('Female')
            chk_interested_female.setChecked('female' in list(profile.interested_in))
            interested_widget = QtGui.QWidget()
            interested_widget.setLayout(QtGui.QHBoxLayout())
            interested_widget.layout().addWidget(chk_interested_male)
            interested_widget.layout().addWidget(chk_interested_female)
            form_layout.addRow(label_interested, interested_widget)

            # 9. Save button.
            def save_profile():
                # Must have an interested gender before proceeding.
                if not chk_interested_male.isChecked() and not chk_interested_female.isChecked():
                    QtGui.QMessageBox().critical(self, 'Profile Error',
                                                 'You must be interested in at least one gender.')
                    return

                # Set profile values.
                profile.bio = txt_bio.toPlainText()
                profile.discoverable = chk_discoverable.isChecked()
                profile.distance_filter = slider_distance.value()
                profile.age_filter_min = slider_age_min.value()
                profile.age_filter_max = 1000 if slider_age_max.value() > 54 else slider_age_max.value()

                # Workaround due to pynder 0.0.13 not yet supporting "gender" and "interested in" changes.
                gender_filter = 2
                profile.interested = []
                profile.sex = 0 if radio_gender_male.isChecked() else 1
                if chk_interested_male.isChecked():
                    gender_filter -= 2
                    profile.interested.append(0)
                if chk_interested_female.isChecked():
                    gender_filter -= 1
                    profile.interested.append(1)
                self.session.update_profile({
                    "interested_in": profile.interested,
                    "gender_filter": gender_filter,
                    "gender": profile.sex
                    # "squads_discoverable": False
                })

                QtGui.QMessageBox.information(self, 'Profile Saved', 'Profile information has been updated.')
                reload_profile()

            def reload_profile():
                # Refresh GUI.
                if profile.sex == 'female':
                    reload_gender_string = '<span style="color: DeepPink;' + self.CSS_FONT_EMOJI + '"> ♀ </span>'
                else:
                    reload_gender_string = '<span style="color: DodgerBlue;' + self.CSS_FONT_EMOJI + '"> ♂ </span>'
                label_name.setText('<span style="' + self.CSS_FONT_HEADLINE + '">' +
                                   profile.name + reload_gender_string + banned_string + '</span>')
                txt_bio.setPlainText(profile.bio)
                chk_discoverable.setChecked(profile.discoverable)
                slider_distance.setValue(profile.distance_filter)
                label_distance_value.setText(str(round(slider_distance.value() * 1.6)) + 'km')
                slider_age_max.setRange(profile.age_filter_min, 55)
                slider_age_max.setValue(55 if profile.age_filter_max > 54 else profile.age_filter_max)
                label_age_max.setText('55+' if slider_age_max.value() > 54 else str(slider_age_max.value()))
                slider_age_min.setRange(18, 46 if profile.age_filter_max > 46 else profile.age_filter_max)
                slider_age_min.setValue(profile.age_filter_min)
                label_age_min.setText(str(slider_age_min.value()))
                chk_interested_male.setChecked(0 in list(profile.interested))  # interested_in workaround.
                chk_interested_female.setChecked(1 in list(profile.interested))  # interested_in workaround.

            btn_save_profile = QtGui.QPushButton('Update Profile')
            btn_save_profile.setFixedHeight(50)
            btn_save_profile.clicked.connect(save_profile)
            pp_layout.addWidget(btn_save_profile, number_of_photos_allowed + 4, 0, 1, number_of_photos_allowed)

            profile_widget.setLayout(pp_layout)
            self.profile_area.setWidget(profile_widget)
            self.profile_area.setAlignment(QtCore.Qt.AlignCenter)

        # Download profile images and then populate the profile GUI.
        profile = self.session.profile
        self.download_thread = DownloadPhotosThread(profile.photos)
        self.download_thread.data_downloaded.connect(populate)
        self.download_thread.start()

    def refresh_users(self, list_area, refresh_button):
        def nearby_users_fetched(data):
            refresh_button.setText('Refresh')
            refresh_button.setDisabled(False)
            if data:
                list_area.setWidget(self.populate_users(data, False))
            else:
                # No more users to go through. Reset the distance filter so the session will fetch the users again.
                self.session.profile.distance_filter = self.session.profile.distance_filter
                no_more_widget = QtGui.QWidget()
                no_more_widget.setLayout(QtGui.QHBoxLayout())
                no_more_widget.layout().addWidget(QtGui.QLabel('No more users to show for now.'))
                list_area.setWidget(no_more_widget)

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

    def populate_users(self, user_list, is_history):
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

            card = QtGui.QWidget()
            card_layout = QtGui.QGridLayout()
            card_layout.setSpacing(10)
            card_layout.addWidget(label_thumbnail, 1, 0, 7, 1)
            card_layout.addWidget(label_name, 1, 1)
            card_layout.addWidget(label_dob, 2, 1)
            card_layout.addWidget(label_distance, 3, 1)
            card_layout.addWidget(label_schools, 4, 1)
            card_layout.addWidget(label_jobs, 5, 1)
            card_layout.addWidget(txt_bio, 6, 1)

            like_buttons_layout = QtGui.QHBoxLayout()
            if not is_history:
                # Like, dislike and super like buttons.
                btn_like = QtGui.QPushButton('Like', self)
                btn_dislike = QtGui.QPushButton('Dislike', self)
                btn_superlike = QtGui.QPushButton('Super Like', self)
                # 'ignore' is just a name to store and ignore the boolean that comes from the assigning the user
                # parameter into the lambda scope. Do not remove, required to work.
                btn_like.clicked.connect(lambda ignore, u=user, l=btn_like, d=btn_dislike, s=btn_superlike: (
                    self.likes_handler.like_user(u),
                    l.setEnabled(False),
                    d.setEnabled(False),
                    s.setEnabled(False)
                ))
                btn_dislike.clicked.connect(lambda ignore, u=user, l=btn_like, d=btn_dislike, s=btn_superlike: (
                    self.likes_handler.dislike_user(u),
                    l.setEnabled(False),
                    d.setEnabled(False),
                    s.setEnabled(False)
                ))
                btn_superlike.clicked.connect(lambda ignore, u=user, l=btn_like, d=btn_dislike, s=btn_superlike: (
                    self.likes_handler.superlike_user(u),
                    l.setEnabled(False),
                    d.setEnabled(False),
                    s.setEnabled(False)
                ))

                like_buttons_layout.addWidget(btn_like)
                like_buttons_layout.addWidget(btn_dislike)
                like_buttons_layout.addWidget(btn_superlike)
            else:
                btn_delete = QtGui.QPushButton('Delete', self)
                btn_delete.clicked.connect(lambda ignore, u=user, b=btn_delete: (
                    self.likes_handler.delete_history(u),
                    b.setText('Deleted'),
                    b.setEnabled(False)
                ))
                like_buttons_layout.addWidget(btn_delete)

            card_layout.addLayout(like_buttons_layout, 7, 1)
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
                self.load_profile()  # Automatically load profile after session is ready.

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

    def reload_likes(self, list_area, *_):
        list_area.setWidget(self.populate_users(self.likes_handler.get_likes(), True))

    def reload_dislikes(self, list_area, *_):
        list_area.setWidget(self.populate_users(self.likes_handler.get_dislikes(), True))

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