import html
import re
from bs4 import BeautifulSoup
from ghost import Ghost
from ghost import TimeoutError
from PyQt5 import QtCore

from pinsey.Utils import EmptyDict


class GoogleSearchByImageThread(QtCore.QThread):
    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, image_url):
        QtCore.QThread.__init__(self)
        self.google_url = 'http://www.google.com/searchbyimage?image_url='
        self.image_url = image_url

    def run(self):
        """
        Performs a Google Search by Image given an image URL. This method returns a -1 if the search is
        unsuccessful. Otherwise, it returns the number of results found.
        """
        url = self.google_url + html.escape(self.image_url)
        ghost = Ghost()

        result = EmptyDict()
        result.number = -1
        result.guess = 'Unknown error!'

        try:
            with ghost.start() as session:
                page, extra_resources = session.open(url)
                if page.http_status != 200:
                    result.guess = 'Unable to load page. Is your Internet connection down?'
                else:
                    soup = BeautifulSoup(page.content, 'html.parser')
                    found = soup.find(id='resultStats').contents[0]
                    result.number = int(re.sub(r'\D', '', found))
                    result.guess = soup.find(string=re.compile('Best guess for this image:')).find_next().contents[0]
        except TimeoutError as te:
            result.guess = 'Timeout error. ' + str(te)
        finally:
            self.data_downloaded.emit(result)

