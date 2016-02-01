#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from android_backup import AndroidBackup

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('IN', type=AndroidBackup)

    args = parser.parse_args()

    infile = args.IN

    infile.parse()

    infile.unpack()
