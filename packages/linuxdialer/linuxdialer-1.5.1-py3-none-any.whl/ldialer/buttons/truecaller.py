"""
Module for Truecaller Implementation
"""
from pathlib import Path
from webbrowser import open

from phonenumbers.phonenumberutil import region_code_for_country_code

name = 'Truecaller'
icon = Path(__file__).parent / 'icons' / 'truecaller.png'


def generate_url(phonenumber_obj):
    """
    Generate truecaller search url.
    :param country_code: country code to generate two letter ISO code.
    :param phonenumber: phone number
    :return: truecaller search url
    """
    country_code = phonenumber_obj.country_code
    phonenumber = str(phonenumber_obj.national_number)

    iso_code = region_code_for_country_code(int(country_code)).lower()
    url = 'https://www.truecaller.com/search/' + iso_code + '/' + phonenumber
    return url


def launch(parent, phonenumber_obj):
    """
    Open truecaller search url in default browser.

    :param parent: Unused
    :param phonenumber_obj: PhoneNumber class object
    :return: None
    """
    open(generate_url(phonenumber_obj))
