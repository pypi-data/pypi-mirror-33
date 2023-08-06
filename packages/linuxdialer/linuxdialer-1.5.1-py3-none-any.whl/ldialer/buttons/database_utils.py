"""
Module is shared by both add_to_addressbook and translate_to_email buttons.
"""
import sqlite3
from pathlib import Path


class DatabaseUtils:
    """
    Class for performing operations on GNOME-Contacts/Evolution database.
    """

    def __init__(self, path=None):
        """
        Connect to GNOME-Contacts/Evolution database. Raise FileNotFoundError if database doesn't exist,
        :param path: Default path will be used when path=None, otherwise manually specified will be used.
        """
        if path is None:
            path = Path('~/.local/share/evolution/addressbook/system/contacts.db').expanduser()
        else:
            path = Path(path)
        if not (path.exists() and path.is_file()):
            raise FileNotFoundError
        self.connection = sqlite3.connect(str(path.absolute()))

    def generate_new_uid(self):
        """
        Generates a new UID ( A Primary key that is used in GNOME-Contacts/Evolution database to identify a contact.
        uniquely )
        :return: newly generated UID
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT uid FROM folder_id')
        uidlist = []
        for uid in cursor:
            uidlist.append(uid[0])
        if len(uidlist) is 0:
            return 'pas-id-5B10CA9D00000016'
        lastuid = uidlist[len(uidlist) - 1]
        lastuid = int(lastuid[7:], 16)
        newuid_hex = lastuid + 1
        while True:
            newuid = 'pas-id-' + str(hex(newuid_hex).upper())[2:]
            if newuid not in uidlist:
                break
            newuid_hex = newuid_hex + 1
        return newuid

    def add_to_addressbook(self, uid, phonenumber, email, vcard):
        """
        Add contact into GNOME-Contacts/Evolution database.
        :param uid: A Primary key that is used in GNOME-Contacts/Evolution database to identify a contact uniquely
        :param phonenumber: phone number of Person
        :param email: email of Person
        :param vcard: vcard data of Contact
        :return: None
        """
        self.connection.execute('INSERT INTO folder_id(uid, vcard) VALUES(?, ?)', (uid, vcard))

        if phonenumber is not '':
            self.connection.execute('INSERT INTO folder_id_phone_list VALUES(?, ?)', (uid, phonenumber))

        if email is not '':
            self.connection.execute('INSERT INTO folder_id_email_list VALUES(?, ?)', (uid, email))

        self.connection.commit()

    def translate_to_email(self, phone_number):
        """
        Translate a phone number into email using GNOME-Contacts/Evolution database.
        :param phone_number: Phone number of a person
        :return: -1, If phone number not found. Otherwise return list of emails ( Can be empty if contact doesn't has email)
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT uid FROM folder_id_phone_list WHERE value=?', (phone_number,))
        uid = None
        for uid in cursor:
            uid = uid[0]

        if uid is None:
            return -1

        cursor.execute('SELECT value FROM folder_id_email_list WHERE uid=?', (uid,))
        emails = []
        for email in cursor:
            emails.append(email[0])

        return emails

    def close_connection(self):
        """
        Close database connnection.
        :return: None
        """
        self.connection.close()
