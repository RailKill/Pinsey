import math

from pinsey.gui.component.LikesListing import LikesListing


class DislikesListing(LikesListing):
    def refresh(self):
        self.user_list = self.likes_handler.get_dislikes()
        # Set page to 1 and display first. Pagination has separate controls that do not refresh list.
        page_limit = math.ceil(len(self.user_list) / 20)
        self.pagination_widget.set_page_limit(page_limit)
        self.paginate()
