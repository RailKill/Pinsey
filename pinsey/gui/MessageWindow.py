from PyQt5 import QtGui, QtWidgets
from pinsey.Constants import ICON_FILEPATH, THUMBNAIL_SIZE, NUMBER_OF_PHOTOS, \
    CSS_FONT_MESSAGE_YOU, FONT_EMOJI
from pinsey.Utils import center, picture_grid, resolve_message_sender, windows, UserInformationWidgetStack
from pinsey.thread.DownloadPhotosThread import DownloadPhotosThread


class MessageWindow(QtWidgets.QMdiSubWindow):
    def __init__(self, match, friend_list):
        super(MessageWindow, self).__init__()
        self.match = match
        self.photo_data = {}
        self.friend_list = friend_list

        # Download the images for viewing.
        download_photos = DownloadPhotosThread(list(match.user.photos))
        download_photos.data_downloaded.connect(self.ready)
        download_photos.start()

        self.setWindowTitle('Messaging: ' + self.match.user.name)
        self.setWindowIcon(QtGui.QIcon(ICON_FILEPATH))
        self.messages_area = QtWidgets.QTextEdit()
        self.send_area = QtWidgets.QPlainTextEdit()
        self.setWidget(QtWidgets.QLabel('Loading details for ' + match.user.name + '...'))
        center(self)
        self.show()

    def closeEvent(self, event):
        windows.remove(self)
        super(MessageWindow, self).closeEvent(event)

    def ready(self, data):
        self.photo_data = data
        self.draw()

    def draw(self):
        self.setWidget(self.load_details())

    def load_details(self):
        # Setup the messaging layout.
        info_widget = QtWidgets.QWidget()
        number_of_photos = NUMBER_OF_PHOTOS
        info_layout = picture_grid(self.photo_data, THUMBNAIL_SIZE, number_of_photos)
        info_stack = UserInformationWidgetStack(self.match.user, self.friend_list)
        info_layout.addWidget(info_stack.name_set, number_of_photos, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.dob, number_of_photos + 1, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.distance, number_of_photos + 2, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.connections, number_of_photos + 3, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.schools, number_of_photos + 4, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.jobs, number_of_photos + 5, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.bio, number_of_photos + 6, 0, 1, number_of_photos)
        info_widget.setLayout(info_layout)

        self.messages_area.setFont(FONT_EMOJI)
        self.messages_area.setReadOnly(True)
        self.load_messages(self.match.messages)
        messages_widget = QtWidgets.QWidget()
        messages_widget.setLayout(QtWidgets.QVBoxLayout())
        messages_widget.layout().addWidget(self.messages_area)

        self.send_area.setFont(QtGui.QFont('Segoe UI Symbol', 12))
        send_button = QtWidgets.QPushButton('Send')
        send_button.clicked.connect(self.send_message)
        send_layout = QtWidgets.QHBoxLayout()
        send_layout.addWidget(self.send_area)
        send_layout.addWidget(send_button)
        send_widget = QtWidgets.QWidget()
        send_widget.setLayout(send_layout)
        messages_widget.layout().addWidget(send_widget)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(info_widget)
        main_layout.addWidget(messages_widget)
        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(main_layout)

        return main_widget

    def load_messages(self, messages):
        conversation = ''
        for m in messages:
            conversation += resolve_message_sender(m, self.match)
            conversation += m.body
            conversation += '<br/>'

        self.messages_area.setText(conversation)

    def send_message(self):
        message = self.send_area.toPlainText()
        self.match.message(message)
        self.send_area.clear()
        self.messages_area.append('<span style="' + CSS_FONT_MESSAGE_YOU + '">You: </span>' + message)
