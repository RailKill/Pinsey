from abc import abstractmethod
from pinsey.gui.component.PaginationWidget import PaginationWidget
from pinsey.gui.component.UserFilterStack import UserFilterStack
from pinsey import Constants
from pinsey.gui.ImageWindow import ImageWindow
from pinsey.Utils import clickable, windows
from gui.component.UserInformationStack import UserInformationStack
from PyQt5 import QtGui, QtWidgets


class UserListingWidget(QtWidgets.QWidget):
    def __init__(self, refresh_text, likes_handler, filter_list, friend_list=None):
        super().__init__()
        if friend_list is None:
            self.friend_list = []
        self.likes_handler = likes_handler
        self.scroll = QtWidgets.QScrollArea()
        self.btn_refresh = QtWidgets.QPushButton(refresh_text, self)
        self.btn_refresh.clicked.connect(self.refresh)

        self.filter_stack = UserFilterStack(filter_list)
        self.pagination_widget = PaginationWidget()
        self.pagination_widget.btn_page.clicked.connect(self.paginate)
        self.page_display_limit = 20  # By default, each user list page should display no more than 20 users.

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.filter_stack)
        layout.addWidget(self.pagination_widget)
        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.scroll)
        self.setLayout(layout)

    def create_user_card(self, user):
        # Thumbnail
        thumbnail = QtGui.QImage()
        thumbnail.loadFromData(user.thumb_data)
        label_thumbnail = QtWidgets.QLabel()
        label_thumbnail.setFixedWidth(Constants.THUMBNAIL_SIZE)
        label_thumbnail.setFixedHeight(Constants.THUMBNAIL_SIZE)
        label_thumbnail.setScaledContents(True)
        label_thumbnail.setPixmap(QtGui.QPixmap(thumbnail))
        # IMPORTANT: lambda user=user forces a capture of the variable into the anonymous scope. Don't remove.
        # Otherwise, the 'user' variable will just be a reference, and won't reflect the user assigned in loop.
        clickable(label_thumbnail).connect(lambda user=user:
                                           (windows.append(ImageWindow(user.name, user.photos))))

        card = QtWidgets.QWidget()
        card_layout = QtWidgets.QGridLayout()
        card_layout.setSpacing(10)
        info_widgets = UserInformationStack(user, self.friend_list)
        card_layout.addWidget(label_thumbnail, 1, 0, 8, 1)
        card_layout.addWidget(info_widgets.name_set, 1, 1)
        card_layout.addWidget(info_widgets.dob, 2, 1)
        card_layout.addWidget(info_widgets.distance, 3, 1)
        card_layout.addWidget(info_widgets.connections, 4, 1)
        card_layout.addWidget(info_widgets.schools, 5, 1)
        card_layout.addWidget(info_widgets.jobs, 6, 1)
        card_layout.addWidget(info_widgets.bio, 7, 1)
        card.setLayout(card_layout)
        return card

    def populate_users(self, user_list):
        user_list_widget = QtWidgets.QWidget()
        user_list_widget.setLayout(QtWidgets.QVBoxLayout())

        # Populate the list with users if available.
        for user in user_list:
            try:
                card = self.create_user_card(user)
                user_list_widget.layout().addWidget(card)
            except Exception as ex:
                print('User population error: ' + str(ex))  # Doesn't matter, ignore if this user fails to populate.
                continue

        self.scroll.setWidget(user_list_widget)
        return True

    @abstractmethod
    def paginate(self):
        return

    @abstractmethod
    def refresh(self):
        return