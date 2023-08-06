#!python
# -*- coding: utf-8 -*-

"""Script to rescue version string from files without importing.

Authors:
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2016/12/25

"""

import codecs
import os
import re


def find_version(filename):
    """Get version string from file.

    Args:
        filename (str): File path.

    Raises:
        RuntimeError: If match string is not found.

    Returns:
        str: Version string.

    """
    version_file = read(filename)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if not version_match:
        raise RuntimeError("Unable to find version string.")

    return version_match.group(1)


def read(filename):
    """Return the contents of a file.

    Args:
        filename (str): File path.

    Returns:
        str: The file's content.

    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, filename), 'r') as f:
        return f.read()


version = find_version('../mrsprint/__init__.py')

with open('got_version.temp', 'w') as f:
    f.write(version)
