from os import system
from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from phonenumbers import PhoneNumberFormat, format_number

from .database_utils import DatabaseUtils

name = 'Translate to email'
icon = Path(__file__).parent / 'icons' / 'tte.png'


class Window(QWidget):
    """
    Translate to email Pop-up Window.
    """

    def __init__(self, phonenumber_obj, database_path=None):
        """

        Initialize GUI for pop-up window.
        :param phonenumber_obj: phonenumber object
        :param database_path: Database file to be used to perform operations
        """
        super().__init__()
        self.phonenumber = format_number(phonenumber_obj, PhoneNumberFormat.E164)

        self.label = QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        close_button = QPushButton('Close')
        close_button.clicked.connect(self.onclick_close)
        self.close_button_hbox = QHBoxLayout()
        self.close_button_hbox.addStretch(1)
        self.close_button_hbox.addWidget(close_button)
        self.close_button_hbox.addStretch(1)

        self.outer_vbox = QVBoxLayout()
        self.outer_vbox.addWidget(self.label)
        self.resize(400, 100)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        self.setLayout(self.outer_vbox)
        self.setWindowTitle('Translate to Email')
        self.get_data(database_path)

    def get_data(self, database_path):
        """
        Method for fetching email and displaying them in pop-up window.
        :param database_path: Database file to be used to perform operations
        :return: None
        """
        try:
            db_connection = DatabaseUtils(path=database_path)
        except FileNotFoundError:
            self.label.setText("Gnome Contact database doesn't exists!")
            self.outer_vbox.addLayout(self.close_button_hbox)
        else:
            response = db_connection.translate_to_email(self.phonenumber)
            db_connection.close_connection()

            if response is -1:
                self.label.setText("Phone Number doesn't exist in addressbook!")
                self.outer_vbox.addLayout(self.close_button_hbox)
            else:
                emails = response
                number_of_email = len(emails)
                if number_of_email is 0:
                    self.label.setText("Contact doesn't has emails!")
                    self.outer_vbox.addLayout(self.close_button_hbox)
                else:
                    if number_of_email is 1:
                        self.label.setText('Email found :')
                    else:
                        self.label.setText('Emails found :')
                    vbox = QVBoxLayout()
                    vbox.setSpacing(10)
                    self.labels = []
                    for i in range(number_of_email):
                        label = QLabel(emails[i])
                        self.labels.append(label)
                        button = QPushButton('Open')
                        button.clicked.connect(self.onclick_open(emails[i]))
                        hbox = QHBoxLayout()
                        hbox.addWidget(label)
                        hbox.addStretch()
                        hbox.addWidget(button)
                        vbox.addLayout(hbox)
                    self.outer_vbox.addLayout(vbox)
        self.outer_vbox.addStretch()

    def onclick_open(self, email):
        """
        Action when 'open' button is pressed.
        :param email: email that will be set as mailto:
        :return: None
        """

        def do():
            system('xdg-email ' + email)

        return do

    def onclick_close(self):
        """
        Action when 'close' button is pressed.
        :return: None
        """
        self.close()


def launch(parent, phonenumber_obj):
    """
    Method for displaying translate to email pop-up window.
    :param parent: reference of parent window (main popup)
    :param phonenumber_obj: Phonenumber object
    :return: None
    """
    parent.tte = Window(phonenumber_obj)
    parent.tte.show()
