#!python
# -*- coding: utf-8 -*-

"""A simple python script for processing ui files.

Authors:
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2016/12/25

"""

from __future__ import absolute_import
from __future__ import print_function

import argparse
import glob
import os
from subprocess import call
import sys


def main(arguments):
    "Main function for process UI files."

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--ui_dir', help="UI directory", default='../mrsprint/gui', type=str)

    args = parser.parse_args(arguments)

    print('Changing directory to: ', args.ui_dir)
    os.chdir(args.ui_dir)

    print('Converting .ui to .py ...')

    for ui_file in glob.glob('*.ui'):
        py_file = os.path.splitext(ui_file)[0] + '.py'
        print(ui_file, py_file)
        call(['pyuic4', ui_file, '-o', py_file])

        # Changing imports
        with open(py_file, 'r') as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace('PyQt4', 'pyqtgraph.Qt')

        # Replace the target string
        filedata = filedata.replace('import mrsprint_rc', 'from mrsprint.gui import mrsprint_rc')

        with open(py_file, 'w') as file:
            # Write the file out again
            file.write(filedata)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
