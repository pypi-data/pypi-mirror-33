#! python
# -*- coding: utf-8 -*-

"""Main GUI script.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

"""

import json
import logging
import logging.config
import os
import sys

from pyqtgraph.Qt import QtCore, QtGui

from mrsprint import __version__ as version
from mrsprint import org_domain, org_name, project
from mrsprint.mainwindow import MainWindow

_logger = logging.getLogger(__name__)


def setup_logging(
        default_path='logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'):
    """Setup logging configuration."""
    path = default_path
    value = os.getenv(env_key, None)

    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def main():

    setup_logging()

    app = QtGui.QApplication(sys.argv[1:])
    app.setStyle('Fusion')

    app.setApplicationVersion(version)
    app.setApplicationName(project)
    app.setOrganizationName(org_name)
    app.setOrganizationDomain(org_domain)

    try:
        import qdarkstyle
    except ImportError:
        _logger.info("No dark theme installed, use 'pip install qdarkstyle' to install.")
    else:
        try:
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())
        except Exception as err:
            _logger.warning("Problems using qdarkstyle.\nError: %s", str(err))

    window = MainWindow()
    window.setWindowTitle(project + ' v' + version)
    window.showMaximized()

    if "--test" in sys.argv:
        QtCore.QTimer.singleShot(2000, app.exit)

    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
