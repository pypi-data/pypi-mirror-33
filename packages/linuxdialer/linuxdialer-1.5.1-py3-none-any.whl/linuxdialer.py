#!/usr/bin/env python3
"""
Main script to run application.
"""
import sys
from argparse import ArgumentParser
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from ldialer import Window
from ldialer.vcard_parse import Window as vCardWindow

parser = ArgumentParser()
parser.add_argument('-t', '--tel', dest='telnum',
                    help='Parse tel: number', metavar='TEL:')
parser.add_argument('-v', '--vcard', dest='vcardname',
                    help='Extract phonenumber from vcard', metavar='VCARD')
parser.add_argument('-a', '--any', dest='anything',
                    help='Try to parse anything', metavar='ANYTHING')
args = parser.parse_args()

app = QApplication(sys.argv)

if args.telnum:
    window = Window(args.telnum)
elif args.vcardname:
    vcard_file = Path(args.vcardname).expanduser()
    if not vcard_file.exists():
        print('No such file!')
        exit(0)

    window = vCardWindow(vcard_file.absolute().__str__())
elif args.anything:
    arg = str(args.anything)
    if 'tel' in arg:
        window = Window(arg)
    elif Path(arg).expanduser().exists():
        window = vCardWindow(arg)
    else:
        print('File not exist.')
        exit(0)

if __name__ == '__main__':
    window.show()
    sys.exit(app.exec_())
