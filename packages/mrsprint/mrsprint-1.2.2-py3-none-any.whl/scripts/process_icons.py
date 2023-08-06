#!python
# -*- coding: utf-8 -*-

"""A simple python script for processing icons.

Authors:
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2016/12/25

"""

from __future__ import absolute_import
from __future__ import print_function

import argparse
import os
import shutil
from subprocess import call
import sys


def main(arguments):
    "Main function for process icons."

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--icons-dir', help="Icons directory", default='../icons', type=str)
    parser.add_argument('--ui-dir', help="UI directory", default='../mrsprint/gui', type=str)

    args = parser.parse_args(arguments)
    print(args)

    print('Changing directory to:', args.icons_dir)
    os.chdir(args.icons_dir)

    qrc_file = 'mrsprint.qrc'
    tmp_file = 'mrsprint_rc.tmp'
    bkp_file = 'mrsprint_rc.bkp'
    py_file = 'mrsprint_rc.py'

    print('Generating mrsprint.qrc from icon files in folder: ', 'icons')
    print('Calling generate_qrc from scripts...')
    call(['python', '../scripts/generate_qrc.py', '.', '-o', qrc_file])

    print('Converting {} to {} ...'.format(qrc_file, tmp_file))
    call(['pyrcc4', '-py3', qrc_file, '-o', tmp_file])

    print('Moving {} to: '.format(tmp_file), args.ui_dir)
    try:
        os.remove(os.path.join(args.ui_dir, bkp_file))
    except OSError:
        print('No old backup found...')
    try:
        print('Creating backup ...')
        os.rename(os.path.join(args.ui_dir, py_file), os.path.join(args.ui_dir, bkp_file))
    except OSError:
        print('No old file found...')
    shutil.move(tmp_file, args.ui_dir)
    os.rename(os.path.join(args.ui_dir, tmp_file), os.path.join(args.ui_dir, py_file))

    with open(os.path.join(args.ui_dir, py_file), 'r') as file:
        filedata = file.read()

    # Replace the target string from imports
    filedata = filedata.replace('PyQt4', 'pyqtgraph.Qt')

    with open(os.path.join(args.ui_dir, py_file), 'w') as file:
        file.write(filedata)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
