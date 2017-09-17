#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import getpass
import android_backup

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('OUT')
    parser.add_argument('-p', '--password')
    parser.add_argument('-e', '--encrypt', action='store_true')

    args = parser.parse_args()

    password = args.password

    ab = android_backup.AndroidBackup()
    ab.version = 3
    ab.compression = android_backup.CompressionType.ZLIB
    ab.encryption = android_backup.EncryptionType.NONE
    if args.encrypt:
        ab.encryption = android_backup.EncryptionType.AES256
    ab.pack(args.OUT, password)
