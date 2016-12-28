import html
import re
import webbrowser
from bs4 import BeautifulSoup
from ghost import Ghost


class GoogleSearchByImage:
    def __init__(self):
        self.google_url = 'http://www.google.com/searchbyimage?image_url='

    def search(self, image_url, open_in_browser):
        """
        Performs a Google Search by Image given an image URL. This method returns a -1 if the search is
        unsuccessful. Otherwise, it returns the number of results found.
        """
        url = self.google_url + html.escape(image_url)

        if open_in_browser:
            webbrowser.open(url)
        else:
            ghost = Ghost()
            with ghost.start() as session:
                page, extra_resources = session.open(url)
                if page.http_status != 200:
                    return -1
                else:
                    soup = BeautifulSoup(page.content, 'html.parser')
                    found = soup.find(id='resultStats').contents[0]
                    guess = soup.find(string=re.compile('Best guess for this image:')).find_next().contents[0]
                    return int(re.sub(r'\D', '', found))
