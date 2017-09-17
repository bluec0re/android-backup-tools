#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import getpass
from android_backup import AndroidBackup

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-p', '--password')
    parser.add_argument('IN', type=AndroidBackup)

    args = parser.parse_args()

    infile = args.IN
    password = args.password

    infile.parse()

    if password is None and infile.is_encrypted:
        password = getpass.getpass("Password:")

    if args.list:
        print(infile.list(password))
    else:
        infile.unpack(password=password)
