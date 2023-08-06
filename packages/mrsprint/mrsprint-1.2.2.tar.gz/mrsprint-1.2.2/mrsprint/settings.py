#! python
# -*- coding: utf-8 -*-

"""Module responsible for the configuration of settings of all other modules.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

Todo:
    Insert log inside functions.

"""


import logging
import os


import h5py
import pyqtgraph.parametertree as pt
from pyqtgraph.Qt import QtCore, QtGui

from mrsprint.gui.mw_settings import Ui_Settings
from mrsprint.simulator.simulator import Simulator
from mrsprint.subject.sample import SampleConfig, SampleElementConfig
from mrsprint.system.gradient import Gradient
from mrsprint.system.magnet import MagnetConfig
from mrsprint.system.rf import RF

_logger = logging.getLogger(__name__)


class Settings(QtGui.QMainWindow):
    """Main window for settings.

    Todo:
        Include restore default settings.
        Create a better check for values.

    """

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)

        self.sample_config_group = SampleConfig()
        self.sample_element_config_group = SampleElementConfig()
        self.magnet_config_group = MagnetConfig()
        self.gradient_group = Gradient()
        self.rf_group = RF()
        self.simulator_group = Simulator()

        self.tree = pt.ParameterTree(self)
        self.tree.addParameters(self.sample_config_group)
        self.tree.addParameters(self.sample_element_config_group)
        self.tree.addParameters(self.magnet_config_group)
        self.tree.addParameters(self.gradient_group)
        self.tree.addParameters(self.rf_group)
        self.tree.addParameters(self.simulator_group)
        self.ui.verticalLayoutSettings.addWidget(self.tree)

        self.ui.actionSettingsOpen.triggered.connect(lambda: self.openFile())
        self.ui.actionSettingsSave.triggered.connect(lambda: self.save(self.ui.lineEditSettings.text()))
        self.ui.actionSettingsSaveAs.triggered.connect(lambda: self.saveFile())
        self.ui.actionSettingsImport.triggered.connect(lambda: self.openFile(set_file=False))
        self.ui.actionSettingsExport.triggered.connect(lambda: self.saveFile(set_file=False))
        self.ui.buttonBoxSettings.accepted.connect(lambda: self.save(self.ui.lineEditSettings.text()))
        self.ui.buttonBoxSettings.accepted.connect(lambda: self.setVisible(False))
        self.ui.buttonBoxSettings.rejected.connect(self.close)

    def check(self):
        """Evaluate if parameters are between its limits before saving them.

        Returns:
            bool: True if OK.

        Todo:
            Reduce complexity and check all value limits.

        """
        error_message = ""

        # sample
        if self.sample_config_group.maxSizeX.value() < self.sample_config_group.SizeX.value():
            error_message += "'Size X Max' must be greater than or equal to 'Size X Default'\n"
        if self.sample_config_group.maxSizeY.value() < self.sample_config_group.SizeY.value():
            error_message += "'Size Y Max' must be greater than or equal to 'Size Y Default'\n"
        if self.sample_config_group.maxSizeZ.value() < self.sample_config_group.SizeZ.value():
            error_message += "'Size Z Max' must be greater than or equal to 'Size Z Default'\n"
        if self.sample_config_group.maxN.value() < self.sample_config_group.Nx.value():
            error_message += "'Max Number of points' must be greater than 'Nx Default'"
        if self.sample_config_group.maxN.value() < self.sample_config_group.Ny.value():
            error_message += "'Max Number of points' must be greater than 'Ny Default'"
        if self.sample_config_group.maxN.value() < self.sample_config_group.Nz.value():
            error_message += "'Max Number of points' must be greater than 'Nz Default'"
        if (self.sample_element_config_group.maxT1.value() < self.sample_element_config_group.t1.value() or
                self.sample_element_config_group.t1.value() < self.sample_element_config_group.minT1.value()):
            error_message += "'T1 Default' must be in between 'T1 Max Value' and 'T1 Min Value'\n"
        if (self.sample_element_config_group.maxT2.value() < self.sample_element_config_group.t2.value() or
                self.sample_element_config_group.t2.value() < self.sample_element_config_group.minT2.value()):
            error_message += "'T2 Default' must be in between 'T2 Max Value' and 'T2 Min Value'\n"
        if (self.sample_element_config_group.maxRho.value() < self.sample_element_config_group.rho.value() or
                self.sample_element_config_group.rho.value() < self.sample_element_config_group.minRho.value()):
            error_message += "'Rho Default' must be in between 'Rho Max Value' and 'Rho Min Value'\n"

        if error_message:
            error_dialog = QtGui.QMessageBox()
            error_dialog.setWindowTitle("Settings error")
            error_dialog.setText("It was found the following error(s):\n" + error_message)
            error_dialog.exec()
            _logger.warning('Settings error: %s', error_message)
            return False
        else:
            return True

    def saveFile(self, set_file=True):
        """Open a dialog to select the config file to be saved."""
        if not self.check():
            return

        file_dialog = QtGui.QFileDialog(caption="Save ...")
        file_dialog.setNameFilter("*.hd5")
        file_dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            file_path = os.path.splitext(str(file_path))[0] + '.hd5'
            if file_path:
                self.save(file_path, set_file)

    def save(self, file_path, set_file=True):
        """Save a HDF5 settings file.

        Args:
            file_path (str): Path to a file containing the settings.
            set_file (bool): set path file if true, otherwise just export.

        """
        if not file_path:
            self.saveFile()

        file_ = h5py.File(file_path, 'w')
        settings_group = file_.create_group("SettingsGroup")
        simulator = [param.value() for param in self.simulator_group]

        if simulator[0] == "From Start":
            simulator[0] = 0
        elif simulator[0] == "Steady State":
            simulator[0] = 1

        if simulator[1] == "All Points":
            simulator[1] = 0
        elif simulator[1] == "End Points":
            simulator[1] = 1

        # Creating datasets
        settings_group.create_dataset("sample_config", data=[param.value() for param in self.sample_config_group])
        settings_group.create_dataset("sample_element_config", data=[param.value() for param in self.sample_element_config_group])
        settings_group.create_dataset("magnet_config", data=[param.value() for param in self.magnet_config_group])
        settings_group.create_dataset("gradient", data=[param.value() for param in self.gradient_group])
        settings_group.create_dataset("rf", data=[param.value() for param in self.rf_group])
        settings_group.create_dataset("simulator", data=simulator)

        file_.flush()
        file_.close()

        if set_file:
            _logger.info("Saving settings file: %s", file_path)
            self.ui.lineEditSettings.setText(file_path)
        else:
            _logger.info("Exporting settings file: %s", file_path)

    def openFile(self, set_file=True):
        """Open a dialog to select the config file to be opened."""
        file_dialog = QtGui.QFileDialog(caption="Open ...")
        file_dialog.setNameFilter("*.hd5")
        file_dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            if file_path:
                self.open(file_path, set_file)

    def blockUnblockSignals(self, value):
        """Block or unblock signals defined by value.

        Args:
            value (bool): True to block, false otherwise.

        """
        self.tree.blockSignals(value)
        self.sample_config_group.blockSignals(value)
        self.sample_element_config_group.blockSignals(value)
        self.magnet_config_group.blockSignals(value)
        self.gradient_group.blockSignals(value)
        self.rf_group.blockSignals(value)
        self.simulator_group.blockSignals(value)

    def open(self, file_path, set_file=True):
        """Open a HDF5 settings file.

        Args:
            file_path (str): Path to a file containing the settings.
            set_file (bool): set path file if true, otherwise just import.

        """
        if not file_path:
            self.openFile()

        file_ = h5py.File(file_path, 'r')
        settings_group = file_.require_group("SettingsGroup")

        self.blockUnblockSignals(True)

        # Reading datasets
        sample_config_value = settings_group.require_dataset("sample_config", exact=True, shape=(10,), dtype=float).value
        sample_element_config_value = settings_group.require_dataset("sample_element_config", exact=True, shape=(9,), dtype=float).value
        magnet_config_value = settings_group.require_dataset("magnet_config", exact=True, shape=(13,), dtype=float).value
        gradient_value = settings_group.require_dataset("gradient", exact=True, shape=(6,), dtype=float).value
        rf_value = settings_group.require_dataset("rf", exact=True, shape=(6,), dtype=float).value
        simulator = settings_group.require_dataset("simulator", exact=True, shape=(13,), dtype=float).value

        file_.close()

        simulator_value = []
        if simulator[0] == 0:
            simulator_value += ["From Start"]
        elif simulator[0] == 1:
            simulator_value += ["Steady State"]

        if simulator[1] == 0:
            simulator_value += ["All Points"]
        elif simulator[1] == 1:
            simulator_value += ["End Points"]

        for i in range(2, len(simulator)):
            simulator_value.append(simulator[i])

        # Updating changes
        groups = [self.magnet_config_group,
                  self.sample_config_group,
                  self.sample_element_config_group,
                  self.magnet_config_group,
                  self.rf_group,
                  self.simulator_group]

        values = [magnet_config_value,
                  sample_config_value,
                  sample_element_config_value,
                  gradient_value,
                  rf_value,
                  simulator_value]

        for j in range(len(groups)):
            i = 0
            _logger.debug('Group: %s', groups[j].name())
            for param in groups[j]:
                try:
                    _logger.debug('Parameter: %s = %s', param.name(), param.value())
                    param.setValue(values[j][i])
                    i += 1
                except Exception:
                    pass
        if set_file:
            _logger.info('Opening settings file: %s', file_path)
            self.ui.lineEditSettings.setText(file_path)
        else:
            _logger.info('Importing settings file: %s', file_path)
        self.blockUnblockSignals(False)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = Settings()
    window.show()
    window.resize(450, 600)
    app.exec_()
