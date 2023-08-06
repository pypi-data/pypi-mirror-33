import pytest
from vobject.vcard import Name, Address

from ..vcard import create_vcard

testcases = (
    (
        dict(uid='pas-id-5B10CA9D00000016',
             name=Name(family='Smith', given='James'),
             phonenumber=('+19988776655', 'WORK'),
             email=None,
             address=None),
        '''\
BEGIN:VCARD
VERSION:3.0
UID:pas-id-5B10CA9D00000016
FN:James Smith
N:Smith;James;;;
TEL;TYPE=WORK:+19988776655
END:VCARD
'''.replace('\n', '\r\n')
    ),

    (
        dict(uid='pas-id-5B10CA9D00000017',
             name=Name(family='Hernandez', given='Maria'),
             phonenumber=('+19966558877', 'Work'),
             email=('mariahernandex@email.com', 'WORK'),
             address=None),
        '''\
BEGIN:VCARD
VERSION:3.0
UID:pas-id-5B10CA9D00000017
EMAIL;TYPE=WORK:mariahernandex@email.com
FN:Maria Hernandez
N:Hernandez;Maria;;;
TEL;TYPE=Work:+19966558877
END:VCARD
'''.replace('\n', '\r\n')
    ),

    (
        dict(uid='pas-id-5B10CA9D00000018',
             name=Name(family='Chen', given='Sandie', additional='Angulo'),
             phonenumber=('+19977885566', 'HOME'),
             email=('sandieangulochen@email.com', 'HOME'),
             address=(Address(street='991 Daphne Street', city='Boise', region='Idaho', code='83646',
                              country='US'), 'HOME')),
        '''\
BEGIN:VCARD
VERSION:3.0
UID:pas-id-5B10CA9D00000018
ADR;TYPE=HOME:;;991 Daphne Street;Boise;Idaho;83646;US
EMAIL;TYPE=HOME:sandieangulochen@email.com
FN:Sandie Angulo Chen
N:Chen;Sandie;Angulo;;
TEL;TYPE=HOME:+19977885566
END:VCARD
'''.replace('\n', '\r\n')
    )
)


@pytest.mark.parametrize('inputs, outputs', testcases)
def test_create_vcard(inputs, outputs):
    """
    Test create_vcard method from vcard.py module.
    :param inputs: arguments of create_vcard method
    :param outputs: expected output of create_vcard method
    :return: None
    """
    obs = create_vcard(**inputs)
    print(obs)
    assert obs == outputs
