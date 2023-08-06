from PyQt5 import QtCore

from ldialer import Window
from . import hello_once, hello_twice


def test_button_framework(qtbot):
    """
    Test if buttons are created or not. custom buttons data is provided
    :param qtbot: fixture to simulate user interaction with Qt widgets
    :return: None
    """
    data = (hello_once, hello_twice)
    widget = Window('tel:+919988776655', data)
    qtbot.addWidget(widget)

    qtbot.mouseClick(widget.button[0], QtCore.Qt.LeftButton)
    qtbot.mouseClick(widget.button[1], QtCore.Qt.LeftButton)
    assert len(widget.button) == 2
    assert widget.button[0].toolTip() == 'Print Phonenumber Once'
    assert widget.button[1].toolTip() == 'Print Phonenumber Twice'
