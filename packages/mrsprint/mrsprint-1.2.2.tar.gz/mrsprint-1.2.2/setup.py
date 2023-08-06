# python
# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath('.'))

import mrsprint as pkg_project
from setuptools import setup, find_packages


def read(filename):
    """Return the contents of a file.

    Args:
        filename (str): File path.

    Returns:
        str: The file's content.

    """
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: C++']

requires = ['numpy>=1.13',
            'nmrglue>=0.6',
            'scipy>=1.1',
            'h5py>=2.8',
            'pyqtgraph>=0.10',
            'pyopengl>=3.1']

setup(name=pkg_project.package,
      version=pkg_project.__version__,
      description=pkg_project.description,
      long_description=read('README.rst'),
      author=pkg_project.authors_string,
      author_email=pkg_project.emails_string,
      maintainer=pkg_project.authors[0],
      maintainer_email=pkg_project.emails[0],
      url=pkg_project.url,
      classifiers=classifiers,
      packages=find_packages(),
      zip_safe=False,  # don't use eggs
      entry_points={"gui_scripts": ["mrsprint=mrsprint.__main__:main"]},
      install_requires=requires,
      license=pkg_project.license
      )
