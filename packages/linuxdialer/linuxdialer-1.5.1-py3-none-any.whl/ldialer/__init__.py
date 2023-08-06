import json
import os
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

import pytz
from PyQt5.QtCore import QSize
from PyQt5.QtGui import (QFont, QIcon)
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox)
from phonenumbers import geocoder, carrier, timezone, PhoneNumberFormat, parse, is_valid_number, format_number
from phonenumbers.phonenumberutil import NumberParseException

from .buttons import buttons as data

__version__ = '1.5.1'


class Window(QWidget):
    """
    Main pop-up window that contains information about phone number and buttons
    """

    config_dir = Path('~/.config/linuxdialer').expanduser()
    config_file = Path('~/.config/linuxdialer/linuxdialer.config').expanduser()

    def __init__(self, parsed_phone_number, data=data):
        """
        Initialize GUI
        :param phone_number: parsed phone number
        """
        super().__init__()
        self.data = data

        if not self.config_file.exists():
            self.create_config()

        config = ConfigParser()
        config.read(self.config_file.__str__())
        country_iso = config['Settings']['lan']
        data_dict = self.readJson()
        for country, iso in data_dict.items():
            if country_iso == iso:
                combobox_text = country
        try:
            self.phonenumber = parse(parsed_phone_number, country_iso)
        except NumberParseException:
            self.phonenumber = None

        font = QFont()
        font.setPointSize(24)

        self.location = QLabel('Location   : --')
        self.timezone = QLabel('Timezone : --')
        self.carrier = QLabel('Carrier      : --')

        details_vbox1 = QVBoxLayout()
        details_vbox1.addWidget(self.location)
        details_vbox1.addWidget(self.carrier)
        details_vbox1.addStretch(1)

        details_vbox2 = QVBoxLayout()
        details_vbox2.addWidget(self.timezone)
        details_vbox2.addStretch(1)

        details_outer_box = QHBoxLayout()
        details_outer_box.addLayout(details_vbox1)
        details_outer_box.addStretch(1)
        details_outer_box.addLayout(details_vbox2)

        self.display = QLabel()
        self.display.setFont(font)

        phone_number_hbox = QHBoxLayout()
        phone_number_hbox.addStretch(1)
        phone_number_hbox.addWidget(self.display)
        phone_number_hbox.addStretch(1)

        footer = QHBoxLayout()
        country_font = QFont()
        country_font.setPointSize(10)

        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("QLabel {color : red; }")
        label = QLabel('Country')
        label.setFont(country_font)
        country_combobox = QComboBox()
        country_combobox.setFixedWidth(120)
        country_combobox.setFixedHeight(25)
        country_combobox.setFont(country_font)
        countries = sorted(data_dict.keys())
        for country in countries:
            country_combobox.addItem(country)

        country_combobox.setCurrentText(combobox_text)
        country_combobox.currentTextChanged.connect(
            lambda: self.on_combobox_text_changed(data_dict[country_combobox.currentText().__str__()]))
        footer.addWidget(self.warning_label)
        footer.addStretch(1)
        footer.addWidget(label)
        footer.addWidget(country_combobox)

        outer_vbox = QVBoxLayout()
        outer_vbox.addLayout(details_outer_box)
        outer_vbox.addLayout(phone_number_hbox)
        outer_vbox.addSpacing(10)
        outer_vbox.addLayout(self.buttons())
        outer_vbox.addSpacing(10)
        outer_vbox.addStretch(1)
        outer_vbox.addLayout(footer)

        if self.phonenumber is None:
            self.display.setText("Invalid Format")
            self.display.setStyleSheet("QLabel {color : red; }")
        elif not is_valid_number(self.phonenumber):
            self.display.setText("Invalid Phone Number")
            self.display.setStyleSheet("QLabel {color : red; }")
        else:
            self.display.setText(format_number(self.phonenumber, PhoneNumberFormat.INTERNATIONAL))
            self.location.setText('Location   : ' + geocoder.description_for_number(self.phonenumber, "en"))
            self.timezone.setText('Timezone : ' + timezone.time_zones_for_number(self.phonenumber)[0] +
                                  ' (' + self.utc_offset() + ")")
            self.carrier.setText(
                'Carrier      : ' + (carrier.name_for_number(self.phonenumber, "en")
                                     if carrier.name_for_number(self.phonenumber, "en") != '' else 'Unknown'))

        self.resize(600, 200)
        self.setMinimumWidth(600)
        self.setLayout(outer_vbox)
        self.setWindowTitle("Linux Dialer")

    def utc_offset(self):
        """
        Generate UTC offset from phonenumber object
        :return: UTC offset
        """
        offset = datetime.now(pytz.timezone(timezone.time_zones_for_number(self.phonenumber)[0])).strftime('%z')
        return 'UTC' + offset[:3] + ':' + offset[3:]

    def readJson(self):
        """
        Read JSON data from iso-country.json file and store into a dictionary.
        :return: Dictionary containing country to iso2 mapping
        """
        json_file = Path(os.path.dirname(__file__)).joinpath('resources/iso-country.json').__str__()
        with open(json_file) as f:
            data = f.read()
            data_dict = json.loads(data)
        return data_dict

    def on_combobox_text_changed(self, country_iso):
        """
        Action when current text of country_combobox is changed
        :param country_iso: ISO2 of Current text (country) in country_combobox
        :return: None
        """
        config = ConfigParser()
        config.read(self.config_file.__str__())
        config['Settings']['lan'] = country_iso
        with open(self.config_file.__str__(), 'w') as file:
            config.write(file)
        self.warning_label.setText('Relaunch application!')

    def create_config(self):
        """
        Create '~/.config/linuxdialer/linuxdialer.conf' file to store Settings.
        :return: None
        """
        config = ConfigParser()
        config['Settings'] = {'lan': 'US'}
        if not self.config_dir.exists():
            os.makedirs(self.config_dir.__str__())
        with open(self.config_file.__str__(), 'w') as file:
            config.write(file)

    def buttons(self):
        """
        Method for creating buttons, uses data from button_framework.py module
        :return: Layout containing buttons
        """
        buttons = len(self.data)
        self.button = []
        outer_box = QVBoxLayout()
        hbox = QHBoxLayout()
        for i in range(buttons):
            if i % 5 is 0:
                outer_box.addLayout(hbox)
                hbox = QHBoxLayout()
            self.button.append(QPushButton())
            self.button[i].setFixedHeight(60)
            self.button[i].setFixedWidth(60)
            self.button[i].setIcon(QIcon(str(self.data[i].icon)))
            self.button[i].clicked.connect(lambda state, idx=i: self.data[idx].launch(self, self.phonenumber))
            self.button[i].setToolTip(self.data[i].name)
            self.button[i].setIconSize(QSize(40, 40))
            hbox.addWidget(self.button[i])
        outer_box.addLayout(hbox)

        if not self.phonenumber or not is_valid_number(self.phonenumber):
            for b in self.button:
                b.setEnabled(False)
        return outer_box
