import os

from phonenumbers import parse

from ..translate_to_email import Window


def test_translate_to_email_qt(qtbot):
    """
    Test translate to email Qt GUI
    :param qtbot: fixture to simulate user interaction with Qt widgets
    :return: None
    """
    phonenumber = parse('tel:+16108728537')
    dirname = os.path.dirname(__file__)
    database_testfile = os.path.join(dirname, 'database/db_translate_to_email.db')
    widget = Window(phonenumber, database_testfile)
    qtbot.addWidget(widget)

    assert widget.label.text() == 'Emails found :'
    assert widget.labels[0].text() == 'mrodriguez@yahoo.com'
    assert widget.labels[1].text() == 'mariarodriguez@gmail.com'
