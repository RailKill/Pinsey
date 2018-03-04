import urllib
from pinsey.Utils import EmptyDict
from PyQt5 import QtCore


class DownloadPhotosThread(QtCore.QThread):
    """
    This is a QThread which runs in the background as a PyQt Signal. It emits the list of downloaded photo data given a
    list of URLs. To access the photo data list, you need to retrieve from the signal, which is named 'data_downloaded'.

    For example:

    instance = DownloadPhotosThread(url_list)
    instance.data_downloaded.connect(yourMethod)

    With the example above, yourMethod() will be called when the background thread has finished fetching the
    photo data. The photo data list will be passed in as the first parameter. Therefore, if you define your
    method like this: yourMethod(list), then the photo data will be passed into 'list'.
    """
    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, url_list):
        QtCore.QThread.__init__(self)
        self.url_list = url_list

    def download(self):
        photo_list = []
        for url in self.url_list:
            photo = EmptyDict()
            photo.url = url
            try:
                photo.data = urllib.request.urlopen(url).read()
                photo_list.append(photo)
            except urllib.error.HTTPError as ex:
                # Ignore. Sometimes images are inaccessible, maybe it's private or deleted?
                print('Download photos error: ' + str(ex))
        return photo_list

    def run(self):
        # Return the list of photo data.
        self.data_downloaded.emit(self.download())
