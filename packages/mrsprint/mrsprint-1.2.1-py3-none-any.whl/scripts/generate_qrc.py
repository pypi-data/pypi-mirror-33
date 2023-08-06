#!python
# -*- coding: utf-8 -*-

"""A simple script to list all files and write as a Qt Resource file format.

Authors:
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2016/12/25

"""

from __future__ import absolute_import
from __future__ import print_function

import argparse
from glob import glob
import os
import sys

from qtpy import QtGui, QtCore


def main(arguments):
    "Main function for generate QRC."

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('root', help="Root path - Run this script inside the icon folder, and poits to mrsprint folder")
    parser.add_argument('-o', '--outfile', help="Output file", default='mrsprint.qrc')
    parser.add_argument('-e', '--extension', help="File extension to list", default='png')

    args = parser.parse_args(arguments)
    print(args)

    # walk on icons folder and get paths
    ext = '*.' + args.extension
    results = [y for x in os.walk(args.root) for y in glob(os.path.join(x[0], ext))]
    num_icons = len(results)

    # avoiding libpng warning: iCCP: known incorrect sRGB profile
    img = QtGui.QImage()
    print('Converting, if necessary, to PNG Qt compatible type to avoid libpng warning')
    # dpm = 300 DPI / pol
    dpm = int(300 / 0.0254)
    for result in results:
        img.load(result)
        # set DPM
        img.setDotsPerMeterX(dpm)
        img.setDotsPerMeterY(dpm)
        # set size in pixels (256x256)
        img_new = img.scaled(96, 96, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        if img != img_new:
            print('Image modified: %s' % result)
            img_new.save(result)

    # compares the real path to the list of classes
    text = "<RCC>\n\t<qresource prefix=\"/mrsprint\">\n"
    for result in results:
        result = os.path.basename(result)
        text += "\t\t<file>" + str(result) + "</file>\n"
    text += "\t</qresource>\n</RCC>"

    print('Number of icons found: ', num_icons)
    with open(args.outfile, "w") as text_file:
        text_file.write(text)
    text_file.close()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
