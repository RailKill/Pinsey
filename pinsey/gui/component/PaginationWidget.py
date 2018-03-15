from PyQt5 import QtWidgets, QtGui


class PaginationWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout()

        lbl_page_desc = QtWidgets.QLabel('Page ')
        self.txt_page = QtWidgets.QLineEdit()
        lbl_page_desc_of = QtWidgets.QLabel('out of ')
        self.lbl_page = QtWidgets.QLabel()
        self.btn_page = QtWidgets.QPushButton('Show', self)
        self.user_list = []

        self.set_page_limit(1)  # Default page limit is 1

        layout.addWidget(lbl_page_desc)
        layout.addWidget(self.txt_page)
        layout.addWidget(lbl_page_desc_of)
        layout.addWidget(self.lbl_page)
        layout.addWidget(self.btn_page)
        layout.addStretch(10)

        self.setLayout(layout)

    def set_page_limit(self, maximum):
        self.txt_page.setValidator(QtGui.QIntValidator(1, maximum))
        self.lbl_page.setText(str(maximum))
        self.set_current_page(1)

    def get_current_page(self):
        current_page = int(self.txt_page.text())
        if current_page <= 0:
            return 1
        else:
            return current_page

    def set_current_page(self, page):
        self.txt_page.setText(str(page))