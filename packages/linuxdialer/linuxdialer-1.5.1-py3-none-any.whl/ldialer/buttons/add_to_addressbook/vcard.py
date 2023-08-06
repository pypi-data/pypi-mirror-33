"""
Module for performing vCard operations
"""
from vobject import vCard


def _set(var, data):
    """
    Unpack tuple and set vcard attr and type_param.
    :param var: vcard attr
    :param data: tuple -> (value, type_param)
    :return: None
    """
    value, type = data
    var.type_param = type
    var.value = value


def create_vcard(uid, name, phonenumber, email, address):
    """
    Method for creating vcard from given information.
    :param uid: A Primary key that is used in GNOME-Contacts/Evolution database to identify a contact uniquely
    :param name: Name of contact
    :param phonenumber: phonenumber tuple -> (phonenumber, type)
    :param email: email tuple -> (email, type)
    :param address: address tuple -> (address, type)
    :return: vcard data
    """
    vcard = vCard()
    vcard.add('uid')
    vcard.uid.value = uid
    vcard.add('fn')
    vcard.fn.value = ' '.join(filter(None, (name.given, name.additional, name.family)))
    vcard.add('n')
    vcard.n.value = name
    if phonenumber:
        vcard.add('tel')
        _set(vcard.tel, phonenumber)
    if email:
        vcard.add('email')
        _set(vcard.email, email)
    if address:
        vcard.add('adr')
        _set(vcard.adr, address)
    return vcard.serialize()
