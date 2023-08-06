import os

from phonenumbers import parse

from ..add_to_addressbook import Window


def test_add_to_addressbook_qt(qtbot):
    """
    Test Add to addressbook Qt GUI
    :param qtbot: fixture to simulate user interaction with Qt widgets
    :return: None
    """
    phonenumber = parse('tel:+16108728537')
    dirname = os.path.dirname(__file__)
    database_testfile = os.path.join(dirname, 'database/db_add_to_addressbook.db')
    widget = Window(phonenumber, database_testfile)
    qtbot.addWidget(widget)

    assert widget.phonenumber_lineedit.text() == '+16108728537'
