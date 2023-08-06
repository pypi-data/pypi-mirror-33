from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout,
                             QMessageBox)
from phonenumbers import format_number, PhoneNumberFormat
from vobject.vcard import Name, Address

from .vcard import create_vcard
from ..database_utils import DatabaseUtils

name = 'Add to addressbook'
icon = Path(__file__).parent.parent / 'icons' / 'ata.png'


class Window(QWidget):
    """
    Add to addressbook Pop-up Window.
    """

    def __init__(self, phonenumber_obj, database_path=None):
        """
        Initialize GUI
        :param phonenumber_obj: Phonenumber object
        :param database_path: Database file to be used to perform operations
        """
        super().__init__()
        self.database_path = database_path

        given_phonenumber = format_number(phonenumber_obj, PhoneNumberFormat.E164)
        font = QFont()
        font.setPointSize(10)

        self.name_lineedit = QLineEdit()
        self.name_lineedit.setPlaceholderText('Name (Required)')
        self.name_lineedit.setFixedHeight(28)
        self.name_lineedit.setFont(font)
        self.name_lineedit_original_stylesheet = self.name_lineedit.styleSheet()
        self.name_lineedit.textChanged.connect(self.on_textchanged)

        self.phonenumber_combobox = QComboBox()
        self.phonenumber_combobox.setFont(font)
        self.phonenumber_combobox.setFixedWidth(80)
        self.phonenumber_combobox.addItem('Mobile')
        self.phonenumber_combobox.addItem('Work')
        self.phonenumber_combobox.addItem('Home')
        self.phonenumber_combobox.addItem('Other')
        self.phonenumber_lineedit = QLineEdit()
        self.phonenumber_lineedit.setPlaceholderText('Phone Number')
        self.phonenumber_lineedit.setText(given_phonenumber)
        self.phonenumber_lineedit.setFixedHeight(28)
        self.phonenumber_lineedit.setFont(font)
        phonenumber_hbox = QHBoxLayout()
        phonenumber_hbox.addWidget(self.phonenumber_combobox)
        phonenumber_hbox.addWidget(self.phonenumber_lineedit)

        self.email_combobox = QComboBox()
        self.email_combobox.setFont(font)
        self.email_combobox.setFixedWidth(80)
        self.email_combobox.addItem('Personal')
        self.email_combobox.addItem('Home')
        self.email_combobox.addItem('Work')
        self.email_combobox.addItem('Other')
        self.email_lineedit = QLineEdit()
        self.email_lineedit.setPlaceholderText('Email')
        self.email_lineedit.setFixedHeight(28)
        self.email_lineedit.setFont(font)
        email_hbox = QHBoxLayout()
        email_hbox.addWidget(self.email_combobox)
        email_hbox.addWidget(self.email_lineedit)

        self.address_combobox = QComboBox()
        self.address_combobox.setFont(font)
        self.address_combobox.setFixedWidth(80)
        self.address_combobox.addItem('Home')
        self.address_combobox.addItem('Work')
        self.address_combobox.addItem('Other')
        address_combobox_vbox = QVBoxLayout()
        address_combobox_vbox.addWidget(self.address_combobox)
        address_combobox_vbox.addStretch(1)

        self.street_lineedit = QLineEdit()
        self.street_lineedit.setPlaceholderText('Street')
        self.street_lineedit.setFixedHeight(28)
        self.street_lineedit.setFont(font)
        self.city_lineedit = QLineEdit()
        self.city_lineedit.setPlaceholderText('City')
        self.city_lineedit.setFixedHeight(28)
        self.city_lineedit.setFont(font)
        self.state_lineedit = QLineEdit()
        self.state_lineedit.setPlaceholderText('State')
        self.state_lineedit.setFixedHeight(28)
        self.state_lineedit.setFont(font)
        self.postalcode_lineedit = QLineEdit()
        self.postalcode_lineedit.setPlaceholderText('Postal Code')
        self.postalcode_lineedit.setFixedHeight(28)
        self.postalcode_lineedit.setFont(font)
        self.country_lineedit = QLineEdit()
        self.country_lineedit.setPlaceholderText('Country')
        self.country_lineedit.setFixedHeight(28)
        self.country_lineedit.setFont(font)

        address_vbox = QVBoxLayout()
        address_vbox.setSpacing(0)
        address_vbox.addWidget(self.street_lineedit)
        address_vbox.addWidget(self.city_lineedit)
        address_vbox.addWidget(self.state_lineedit)
        address_vbox.addWidget(self.postalcode_lineedit)
        address_vbox.addWidget(self.country_lineedit)

        address_hbox = QHBoxLayout()
        address_hbox.addLayout(address_combobox_vbox)
        address_hbox.addLayout(address_vbox)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.on_save)
        button_hbox = QHBoxLayout()
        button_hbox.addStretch()
        button_hbox.addWidget(self.save_button)
        button_hbox.addStretch()

        outer_vbox = QVBoxLayout()
        outer_vbox.setSpacing(20)
        outer_vbox.addWidget(self.name_lineedit)
        outer_vbox.addLayout(phonenumber_hbox)
        outer_vbox.addLayout(email_hbox)
        outer_vbox.addLayout(address_hbox)
        outer_vbox.addLayout(button_hbox)
        outer_vbox.addStretch(1)

        self.type_param = {
            'Mobile': 'CELL',
            'Personal': 'PERSONAL',
            'Home': 'HOME',
            'Work': 'WORK',
            'Other': 'OTHER'
        }
        self.resize(400, 100)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self.setMaximumHeight(100)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        self.setLayout(outer_vbox)
        self.setWindowTitle("Add to Addressbook")

    def on_save(self):
        """
        Action when save button is pressed.
        :return: None
        """
        self.name = self.name_lineedit.text().strip()
        if self.name is '':
            self.name_lineedit.setStyleSheet('border: 1px solid red;')
        else:
            self.phonenumber = self.phonenumber_lineedit.text().strip()
            self.email = self.email_lineedit.text().strip()
            self.street = self.street_lineedit.text().strip()
            self.city = self.city_lineedit.text().strip()
            self.state = self.state_lineedit.text().strip()
            self.postalcode = self.postalcode_lineedit.text().strip()
            self.country = self.country_lineedit.text().strip()
            self.whole_address = self.street + self.city + self.state + self.postalcode + self.country

            self.phonenumber_type = self.type_param[self.phonenumber_combobox.currentText()]
            self.email_type = self.type_param[self.email_combobox.currentText()]
            self.address_type = self.type_param[self.address_combobox.currentText()]

            try:
                db_connection = DatabaseUtils(path=self.database_path)
            except:
                self.close()
                self.show_faileddialog()
            else:
                self.uid = db_connection.generate_new_uid()

                name = self.format_name(self.name)

                if self.phonenumber is '':
                    phonenumber = None
                else:
                    phonenumber = (self.phonenumber, self.phonenumber_type)
                if self.email is '':
                    email = None
                else:
                    email = (self.email, self.phonenumber_type)
                if self.whole_address is '':
                    address = None
                else:
                    address = (
                        Address(self.street, self.city, self.state, self.postalcode, self.country), self.email_type)

                vcard = create_vcard(self.uid, name, phonenumber, email, address)

                db_connection.add_to_addressbook(self.uid, self.phonenumber, self.email, vcard)
                self.close()
                self.show_successdialog()

    def on_textchanged(self):
        """
        LineEdit boarder color of Name field is set to red when user presses save button without filling Name field. This method
        is used to remove that red boarder color when user starts typing in Name field.
        :return: None
        """
        self.name_lineedit.setStyleSheet(self.name_lineedit_original_stylesheet)

    def format_name(self, full_name):
        """
        Generate a vcard Name object from given full name.
        :param full_name:
        :return: vobject.vcard.Name object
        """
        name_arr = str(full_name).split(' ')
        arr_len = len(name_arr)
        given = ''
        family = ''
        additional = ''

        if arr_len is 1:
            given = name_arr[0]
        elif arr_len is 2:
            given = name_arr[0]
            family = name_arr[1]
        else:
            given = name_arr[0]
            additional = name_arr[1]
            family = ' '.join(name_arr[2:])
        return Name(family=family, given=given, additional=additional)

    def show_successdialog(self):
        """
        Dialog box that is shown after pressing save button if contact is successfully saved.
        :return: None
        """
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle('Information')
        message_box.setText("Contact Saved!")
        message_box.exec_()

    def show_faileddialog(self):
        """
        Dialog box that is shown after pressing save button if Gnome Contact database doesn't exist.
        :return: None
        """
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle('Information')
        message_box.setText("Gnome Contacts database doesn't exist!")
        message_box.exec_()


def launch(parent, phonenumber_obj):
    """
    Method for launching add to addressbook pop-up window.
    :param parent: reference of parent window (main popup)
    :param phonenumber_obj: Phonenumber object
    :return: None
    """
    parent.ata = Window(phonenumber_obj)
    parent.ata.show()
