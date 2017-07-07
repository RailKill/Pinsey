import html
import webbrowser

from PyQt4 import QtGui
from pinsey.Utils import clickable, center
from pinsey.thread.DownloadPhotosThread import DownloadPhotosThread


class ImageWindow(QtGui.QMainWindow):
    def __init__(self, name, image_urls, main_window):
        super(ImageWindow, self).__init__()
        self.main_window = main_window
        self.photo_list = []
        self.current_image_count = -1  # Initialize at negative 1, so the index will start at 0 during update_image().
        self.maximum_image_count = len(image_urls)
        self.label_name = QtGui.QLabel(name)
        self.label_count = QtGui.QLabel()
        self.label_pic = QtGui.QLabel()
        self.label_pic.setFixedWidth(600)
        self.label_pic.setFixedHeight(600)
        self.label_pic.setScaledContents(True)
        clickable(self.label_pic).connect(self.draw)

        # Download the images for viewing.
        download_photos = DownloadPhotosThread(image_urls)
        download_photos.data_downloaded.connect(self.ready)
        download_photos.start()
        self.setCentralWidget(QtGui.QLabel('Fetching images of ' + name + '...'))
        self.setWindowTitle('Pinsey: Pictures of ' + name)
        self.setWindowIcon(QtGui.QIcon('../resources/icons/logo-128x128.png'))
        self.setFixedWidth(620)
        self.setFixedHeight(660)
        center(self)
        self.show()

    def closeEvent(self, event):
        self.main_window.windows.remove(self)
        super(ImageWindow, self).closeEvent(event)

    def ready(self, data):
        self.photo_list = data
        self.draw()

    def draw(self):
        self.setCentralWidget(self.update_image())

    def update_image(self):
        # Update currently viewed image count.
        if self.current_image_count + 1 >= self.maximum_image_count:
            self.current_image_count = 0
        else:
            self.current_image_count += 1

        # Update label that tells the user the currently viewed image count.
        current_image_string = 'Viewing ' + str(self.current_image_count + 1)\
                               + ' out of ' + str(self.maximum_image_count)
        self.label_count.setText(current_image_string)

        # Update the image shown.
        pic = QtGui.QImage()
        pic.loadFromData(self.photo_list[self.current_image_count].data)
        self.label_pic.setPixmap(QtGui.QPixmap(pic))

        # Setup the layout and return the widget with this layout.
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.label_name)

        # Google search functionality only supported for web URLs for now. Local images have to upload manually.
        if not self.photo_list[self.current_image_count].url.startswith('file:'):
            btn_google = QtGui.QPushButton('Google This', self)
            btn_google.clicked.connect(
                lambda web_search: (webbrowser.open('http://www.google.com/searchbyimage?image_url='
                                                    + html.escape(self.photo_list[self.current_image_count].url))))
            hbox.addWidget(btn_google)

        hbox.addStretch(1)
        hbox.addWidget(self.label_count)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.label_pic)

        widget = QtGui.QWidget()
        widget.setLayout(vbox)
        return widget

