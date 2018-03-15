import math

from pinsey.gui.component.UserListingWidget import UserListingWidget
from pinsey import Constants
from PyQt5 import QtCore, QtWidgets


class LikesListing(UserListingWidget):
    def __init__(self, *args, **kwargs):
        super(LikesListing, self).__init__(*args, **kwargs)
        self.user_list = []

    def refresh(self):
        self.user_list = self.likes_handler.get_likes()
        # Set page to 1 and display first. Pagination has separate controls that do not refresh list.
        page_limit = math.ceil(len(self.user_list) / 20)
        self.pagination_widget.set_page_limit(page_limit)
        self.paginate()

    def filter(self):
        filtered_list = self.user_list
        filtered_list.sort(key=lambda x: getattr(x, self.filter_stack.sort_attribute()),
                           reverse=self.filter_stack.is_descending())
        filtered_list = [x for x in filtered_list if x.gender.lower() in self.filter_stack.gender_filter()]

        # Select X amount of users from list to display based on current page
        # TODO: Don't hardcode 20 as the amount of users to display.
        current_index = (self.pagination_widget.get_current_page() - 1) * 20
        return filtered_list[current_index : current_index + 20]

    def paginate(self):
        self.populate_users(self.filter())

    def create_user_card(self, user):
        card = super(LikesListing, self).create_user_card(user)
        history_layout = QtWidgets.QHBoxLayout()
        if user.added_by.lower() == 'bot':
            added_by_style = "<span style='" + Constants.CSS_FONT_MESSAGE_MATCH + "font-size: large'>%s</span>"
        else:
            added_by_style = "<span style='" + Constants.CSS_FONT_MESSAGE_YOU + "font-size: large'>%s</span>"

        label_date_added = QtWidgets.QLabel(
            '<b>Date Added: </b>' +
            user.date_added.strftime("%B %d, %Y at %I:%M%p") + ' by ' +
            added_by_style % user.added_by
        )
        label_date_added.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        btn_delete = QtWidgets.QPushButton('Delete', self)
        btn_delete.clicked.connect(lambda ignore, u=user, b=btn_delete: (
            self.likes_handler.delete_history(u),
            b.setText('Deleted'),
            b.setEnabled(False)
        ))
        history_layout.addWidget(label_date_added)
        history_layout.addWidget(btn_delete)
        card.layout().addLayout(history_layout, 8, 1)
        return card
