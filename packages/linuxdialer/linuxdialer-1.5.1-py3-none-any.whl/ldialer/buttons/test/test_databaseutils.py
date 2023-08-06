import os
from sqlite3 import IntegrityError

import pytest
from vobject.vcard import Name, Address

from ..add_to_addressbook.vcard import create_vcard
from ..database_utils import DatabaseUtils

testcases_translate_to_email = (
    ('+15855473281', -1),
    ('+12535394641', []),
    ('+15755432832', ['jamessmith@gmail.com']),
    ('+16108728537', ['mrodriguez@yahoo.com', 'mariarodriguez@gmail.com'])
)


@pytest.mark.parametrize('inputs, outputs', testcases_translate_to_email)
def test_translate_to_email(inputs, outputs):
    """
    Test translate_to_email method from database_utils.py module. Uses './database/db_translate_to_email.db' database
    to perform operations.
    :param inputs: argument of translate_to_email method (phonenumber)
    :param outputs: expected output of translate_to_email method
    :return: None
    """
    dirname = os.path.dirname(__file__)
    database_testfile = os.path.join(dirname, 'database/db_translate_to_email.db')
    db = DatabaseUtils(path=database_testfile)
    obs = db.translate_to_email(inputs)
    db.close_connection()
    print(obs)
    assert obs == outputs


testcases_genrate_new_uid = (
    ('db_generate_new_uid1.db', 'pas-id-5B26751C00000003'),
    ('db_generate_new_uid2.db', 'pas-id-5B10CA9D00000016')
)


@pytest.mark.parametrize('inputs, outputs', testcases_genrate_new_uid)
def test_generate_new_uid(inputs, outputs):
    """
    Test generate_new_uid method from database_utils.py module. Uses database specified in the inputs to perform
    operations.
    :param inputs: a database file used to perform operations
    :param outputs: expected output of generate_new_uid method
    :return: None
    """
    dirname = os.path.dirname(__file__)
    database_testfile = os.path.join(dirname, 'database/' + inputs)
    db = DatabaseUtils(path=database_testfile)
    obs = db.generate_new_uid()
    db.close_connection()
    print(obs)
    assert obs == outputs


testcases_add_to_addressbook = (
    (dict(uid='',
          name=Name(family='Smith', given='James'),
          phonenumber=('+19988776655', 'WORK'),
          email=('smithjames@email.com', 'HOME'),
          address=None), None),

    (dict(uid='',
          name=Name(family='Hernandez', given='Maria'),
          phonenumber=('+19966558877', 'Work'),
          email=('mariahernandex@email.com', 'WORK'),
          address=None), None),

    (dict(uid='',
          name=Name(family='Chen', given='Sandie', additional='Angulo'),
          phonenumber=('+19977885566', 'HOME'),
          email=('sandieangulochen@email.com', 'HOME'),
          address=(Address(street='991 Daphne Street', city='Boise', region='Idaho', code='83646',
                           country='US'), 'HOME')), None)
)


@pytest.mark.parametrize('inputs, outputs', testcases_add_to_addressbook)
def test_add_to_addressbook(inputs, outputs):
    """
    Test add_to_addressbook method from database_utils.py module. Uses './database/db_add_to_addressbook.db' database
    to perform operations.
    :param inputs: arguments dictionary
    :param outputs: Nothing appropriate
    :return: None
    """
    dirname = os.path.dirname(__file__)
    database_testfile = os.path.join(dirname, 'database/db_add_to_addressbook.db')
    db = DatabaseUtils(path=database_testfile)
    uid = db.generate_new_uid()
    inputs['uid'] = uid
    vcard = create_vcard(**inputs)
    db.add_to_addressbook(uid, inputs['phonenumber'][0], inputs['email'][0], vcard)
    db.close_connection()


testcase_integrity_error = (
    (
        dict(uid='',
             name=Name(family='Hernandez', given='Maria'),
             phonenumber=('+19966558877', 'Work'),
             email=('mariahernandex@email.com', 'WORK'),
             address=None),

        dict(uid='',
             name=Name(family='Chen', given='Sandie', additional='Angulo'),
             phonenumber=('+19977885566', 'HOME'),
             email=('sandieangulochen@email.com', 'HOME'),
             address=(Address(street='991 Daphne Street', city='Boise', region='Idaho', code='83646',
                              country='US'), 'HOME'))
    ),
)


@pytest.mark.parametrize('input1, input2', testcase_integrity_error)
def test_integrity_error(input1, input2):
    """
    Test IntegrityError in special case ( IntegrityError Exception will raised because inserting two contacts with same UID)
    :param input1: Contact1 information
    :param input2: Contact2 information
    :return: None
    """
    dirname = os.path.dirname(__file__)
    database_testfile = os.path.join(dirname, 'database/db_integrity_error.db')
    db1 = DatabaseUtils(path=database_testfile)
    db2 = DatabaseUtils(path=database_testfile)
    uid1 = db1.generate_new_uid()
    uid2 = db2.generate_new_uid()
    input1['uid'] = uid1
    input2['uid'] = uid2
    vcard1 = create_vcard(**input1)
    vcard2 = create_vcard(**input2)
    with pytest.raises(IntegrityError):
        db1.add_to_addressbook(uid1, input1['phonenumber'][0], input1['email'][0], vcard1)
        db2.add_to_addressbook(uid2, input2['phonenumber'][0], input2['email'][0], vcard2)
    db1.close_connection()
    db2.close_connection()
