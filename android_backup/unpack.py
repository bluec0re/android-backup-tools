#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: Apache-2.0
import argparse
from android_backup import AndroidBackup
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
   #|     |#   Unpacker
   #|_____|#
      # #
"""
    else:
        desc = """
\033[92m    \\.---./
    / . . \\
   #|     |#   \033[94mAndroid Backup\033[92m
   #|     |#   \033[94mUnpacker\033[92m
   #|_____|#
      # #\033[0m
"""

    return desc[1:]  # skip empty line


def main():
    parser = argparse.ArgumentParser(description=_description(),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-p', '--password')
    parser.add_argument('-t', '--target-dir')
    parser.add_argument('IN', type=AndroidBackup)

    args = parser.parse_args()

    with args.IN as infile:
        if args.list:
            infile.list(
                password=args.password
                )
        else:
            infile.unpack(
                target_dir=args.target_dir,
                password=args.password
                )


if __name__ == "__main__":
    main()
