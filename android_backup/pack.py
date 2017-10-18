#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: Apache-2.0
import argparse
import android_backup
import sys


def _description():
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        desc = r"""
    \.---./
    / . . \
   #|     |#   Android Backup
   #|     |#   Packer
   #|_____|#
      # #
"""
    else:
        desc = """
\033[92m    \\.---./
    / . . \\
   #|     |#   \033[94mAndroid Backup\033[92m
   #|     |#   \033[94mPacker\033[92m
   #|_____|#
      # #\033[0m
"""

    return desc[1:] # skip empty line


def main():
    parser = argparse.ArgumentParser(description=_description(),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('OUT')
    parser.add_argument('-p', '--password')
    parser.add_argument('-s', '--source-dir')
    parser.add_argument('-e', '--encrypt', action='store_true')

    args = parser.parse_args()

    ab = android_backup.AndroidBackup()
    ab.version = 3
    ab.compression = android_backup.CompressionType.ZLIB
    ab.encryption = android_backup.EncryptionType.NONE
    if args.encrypt:
        ab.encryption = android_backup.EncryptionType.AES256
    
    ab.pack(
        fname=args.OUT,
        source_dir=args.source_dir,
        password=args.password
        )


if __name__ == "__main__":
    main()
