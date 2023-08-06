"""
Information about button 1
"""
from pathlib import Path

from phonenumbers import format_number, PhoneNumberFormat

name = 'Print Phonenumber Once'
icon = Path(__file__).parent / 'icons' / '1.png'


def say(phonenumber):
    print(phonenumber)


def launch(ref, phonenumber_obj):
    phonenumber = format_number(phonenumber_obj, PhoneNumberFormat.E164)
    say(phonenumber)
