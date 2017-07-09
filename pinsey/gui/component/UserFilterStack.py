from PyQt4 import QtGui


class UserFilterStack(QtGui.QWidget):
    def __init__(self, filter_list):
        """
            This is a widget which contains other widgets that make up of the filter section of the user list GUI.
            It takes in a list of strings to sort by. These strings are attribute names of the Pynder User object
            so that they can be sorted by that attribute.

            :param filter_list:     List of User attribute names to be sorted.
            :type filter_list:      list of str
        """
        super().__init__()
        self.filter_list = filter_list
        label_sort_by = QtGui.QLabel('Sort By: ')
        self.cmb_sort_by = QtGui.QComboBox()
        self.cmb_sort_by.addItems(self.filter_list)
        self.radio_ascending = QtGui.QRadioButton('Ascending')
        self.radio_ascending.setChecked(True)
        self.radio_descending = QtGui.QRadioButton('Descending')
        label_filter = QtGui.QLabel('Filter: ')
        self.chk_male = QtGui.QCheckBox('Male')
        self.chk_male.setChecked(True)
        self.chk_female = QtGui.QCheckBox('Female')
        self.chk_female.setChecked(True)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(label_sort_by)
        layout.addWidget(self.cmb_sort_by)
        layout.addWidget(self.radio_ascending)
        layout.addWidget(self.radio_descending)
        layout.addStretch()
        layout.addWidget(label_filter)
        layout.addWidget(self.chk_male)
        layout.addWidget(self.chk_female)
        self.setLayout(layout)

    def sort_attribute(self):
        """
            Gets the attribute name to be sorted from the filter list combo box. For example, if the combo box
            current text is 'Date Added', this function will return 'date_added' as a string.

            :return:    Attribute name that is selected in the Sort By combo box.
            :rtype:     str
        """
        return self.cmb_sort_by.currentText().lower().replace(' ', '_')

    def is_descending(self):
        """
            Checks if the descending order filter radio button has been turned on.

            :return:    True if descending order filter is enabled. Otherwise, False.
            :rtype:     bool
        """
        return self.radio_descending.isChecked()

    def gender_filter(self):
        """
            Returns a list of strings that contain either 'male' or 'female' depending on which gender filter
            is checked.

            :return:    List of strings that contain either 'male' or 'female'
            :rtype:     list of str
        """
        gender_list = []
        if self.chk_male.isChecked():
            gender_list.append(self.chk_male.text().lower())
        if self.chk_female.isChecked():
            gender_list.append(self.chk_female.text().lower())
        return gender_list
