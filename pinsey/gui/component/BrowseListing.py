from pinsey.gui.component.UserListingWidget import UserListingWidget
from PyQt5 import QtGui, QtWidgets

from pinsey.thread.NearbyUsersThread import NearbyUsersThread


class BrowseListing(UserListingWidget):
    def __init__(self, *args, **kwargs):
        super(BrowseListing, self).__init__(*args, **kwargs)
        self.session = None
        self.pagination_widget.setVisible(False)  # No pagination for browsing, just keep refreshing instead.

    def create_user_card(self, user):
        card = super().create_user_card(user)
        like_buttons_layout = QtWidgets.QHBoxLayout()
        # Like, dislike and super like buttons.
        btn_like = QtWidgets.QPushButton('Like', self)
        btn_dislike = QtWidgets.QPushButton('Dislike', self)
        btn_superlike = QtWidgets.QPushButton('Super Like', self)
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

        card.layout().addLayout(like_buttons_layout, 8, 1)
        return card

    def populate_users(self, user_list):
        self.btn_refresh.setText('Refresh')
        self.btn_refresh.setDisabled(False)
        if user_list:
            super(BrowseListing, self).populate_users(user_list)
            return True
        else:
            # No more users to go through. Reset the distance filter so the session will fetch the users again.
            #  self.session.profile.distance_filter = self.session.profile.distance_filter
            no_more_widget = QtWidgets.QWidget()
            no_more_widget.setLayout(QtWidgets.QHBoxLayout())
            no_more_widget.layout().addWidget(QtWidgets.QLabel('No more users to show for now.'))
            self.scroll.setWidget(no_more_widget)
            return False

    def paginate(self):
        # BrowseListing does not support pagination.
        return

    def refresh(self):
        if self.session:
            nearby_users = NearbyUsersThread(self.session)
            nearby_users.data_downloaded.connect(self.populate_users)
            nearby_users.start()

            # Show loading screen in the meantime.
            self.btn_refresh.setText('Refreshing...')
            self.btn_refresh.setDisabled(True)
            loading = QtWidgets.QWidget()
            loading.setLayout(QtWidgets.QHBoxLayout())
            loading_icon = QtGui.QMovie('../resources/icons/heart-32x32.gif')
            loading_label = QtWidgets.QLabel()
            loading_label.setMovie(loading_icon)
            loading_icon.start()
            loading.layout().addWidget(QtWidgets.QLabel('Loading...'))
            loading.layout().addWidget(loading_label)
            self.scroll.setWidget(loading)
        else:
            label_noauth = QtWidgets.QLabel('Not connected. Please enter correct authentication '
                                            'details in Settings tab.')
            noauth = QtWidgets.QWidget()
            noauth.setLayout(QtWidgets.QVBoxLayout())
            noauth.layout().addWidget(label_noauth)
            self.scroll.setWidget(noauth)
