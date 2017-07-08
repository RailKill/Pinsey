from PyQt4 import QtGui
from pinsey.Constants import ICON_FILEPATH, THUMBNAIL_SIZE, NUMBER_OF_PHOTOS, \
    CSS_FONT_MESSAGE_YOU, CSS_FONT_MESSAGE_MATCH, FONT_EMOJI
from pinsey.Utils import center, picture_grid, UserInformationWidgetStack


class MessageWindow(QtGui.QMainWindow):
    def __init__(self, match, main_window):
        super(MessageWindow, self).__init__()
        self.main_window = main_window
        self.match = match
        self.setWindowTitle('Messaging: ' + self.match.user.name)
        self.setWindowIcon(QtGui.QIcon(ICON_FILEPATH))

        # Setup the messaging layout.
        info_widget = QtGui.QWidget()
        number_of_photos = NUMBER_OF_PHOTOS
        info_layout = picture_grid(self.match.user.photos, THUMBNAIL_SIZE, number_of_photos)
        info_stack = UserInformationWidgetStack(self.match.user)
        info_layout.addWidget(info_stack.name_set, number_of_photos, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.dob, number_of_photos + 1, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.distance, number_of_photos + 2, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.schools, number_of_photos + 3, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.jobs, number_of_photos + 4, 0, 1, number_of_photos)
        info_layout.addWidget(info_stack.bio, number_of_photos + 5, 0, 1, number_of_photos)

        self.messages_area = QtGui.QTextEdit()
        self.messages_area.setFont(FONT_EMOJI)
        self.messages_area.setReadOnly(True)
        self.load_messages(self.match.messages)
        messages_widget = QtGui.QWidget()
        messages_widget.setLayout(QtGui.QVBoxLayout())
        messages_widget.layout().addWidget(self.messages_area)

        self.send_area = QtGui.QPlainTextEdit()
        self.send_area.setFont(QtGui.QFont('Segoe UI Symbol', 12))
        self.send_button = QtGui.QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)
        send_layout = QtGui.QHBoxLayout()
        send_layout.addWidget(self.send_area)
        send_layout.addWidget(self.send_button)
        send_widget = QtGui.QWidget()
        send_widget.setLayout(send_layout)
        messages_widget.layout().addWidget(send_widget)

        main_layout = QtGui.QHBoxLayout()
        main_layout.addWidget(info_widget)
        main_layout.addWidget(messages_widget)
        main_widget = QtGui.QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        center(self)
        self.show()

    def closeEvent(self, event):
        self.main_window.windows.remove(self)
        super(MessageWindow, self).closeEvent(event)

    def load_messages(self, messages):
        conversation = ''
        for m in messages:
            if m.sender == self.match.user.id:
                conversation += '<span style="' + CSS_FONT_MESSAGE_MATCH + '">' + self.match.user.name + ': </span>'
            else:
                conversation += '<span style="' + CSS_FONT_MESSAGE_YOU + '">You: </span>'
            conversation += m.body
            conversation += '<br/>'

        self.messages_area.setText(conversation)

    def send_message(self):
        message = self.send_area.toPlainText()
        self.match.message(message)
        self.send_area.clear()
        self.messages_area.append('<span style="' + CSS_FONT_MESSAGE_YOU + '">You: </span>' + message)
