# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mw_settings.ui'
#
# Created by: pyqtgraph.Qt UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from pyqtgraph.Qt import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName(_fromUtf8("Settings"))
        Settings.resize(326, 368)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/mrsprint/Settings.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Settings.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(Settings)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.labelSettings = QtGui.QLabel(self.centralwidget)
        self.labelSettings.setObjectName(_fromUtf8("labelSettings"))
        self.verticalLayout_2.addWidget(self.labelSettings)
        self.lineEditSettings = QtGui.QLineEdit(self.centralwidget)
        self.lineEditSettings.setEnabled(True)
        self.lineEditSettings.setText(_fromUtf8(""))
        self.lineEditSettings.setReadOnly(True)
        self.lineEditSettings.setObjectName(_fromUtf8("lineEditSettings"))
        self.verticalLayout_2.addWidget(self.lineEditSettings)
        self.verticalLayoutSettings = QtGui.QVBoxLayout()
        self.verticalLayoutSettings.setObjectName(_fromUtf8("verticalLayoutSettings"))
        self.verticalLayout_2.addLayout(self.verticalLayoutSettings)
        self.buttonBoxSettings = QtGui.QDialogButtonBox(self.centralwidget)
        self.buttonBoxSettings.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBoxSettings.setObjectName(_fromUtf8("buttonBoxSettings"))
        self.verticalLayout_2.addWidget(self.buttonBoxSettings)
        Settings.setCentralWidget(self.centralwidget)
        self.toolBar = QtGui.QToolBar(Settings)
        self.toolBar.setIconSize(QtCore.QSize(32, 32))
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        Settings.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionSettingsSaveAs = QtGui.QAction(Settings)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/mrsprint/FileSaveAs.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettingsSaveAs.setIcon(icon1)
        self.actionSettingsSaveAs.setObjectName(_fromUtf8("actionSettingsSaveAs"))
        self.actionSettingsOpen = QtGui.QAction(Settings)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/mrsprint/FileOpen.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettingsOpen.setIcon(icon2)
        self.actionSettingsOpen.setObjectName(_fromUtf8("actionSettingsOpen"))
        self.actionSettingsImport = QtGui.QAction(Settings)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/mrsprint/FileImport.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettingsImport.setIcon(icon3)
        self.actionSettingsImport.setObjectName(_fromUtf8("actionSettingsImport"))
        self.actionSettingsExport = QtGui.QAction(Settings)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/mrsprint/FileExport.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettingsExport.setIcon(icon4)
        self.actionSettingsExport.setObjectName(_fromUtf8("actionSettingsExport"))
        self.actionSettingsSave = QtGui.QAction(Settings)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/mrsprint/FileSave.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettingsSave.setIcon(icon5)
        self.actionSettingsSave.setObjectName(_fromUtf8("actionSettingsSave"))
        self.toolBar.addAction(self.actionSettingsOpen)
        self.toolBar.addAction(self.actionSettingsSave)
        self.toolBar.addAction(self.actionSettingsSaveAs)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSettingsImport)
        self.toolBar.addAction(self.actionSettingsExport)

        self.retranslateUi(Settings)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(_translate("Settings", "Settings", None))
        self.labelSettings.setText(_translate("Settings", "Current settings path:", None))
        self.lineEditSettings.setPlaceholderText(_translate("Settings", "/my/current/settings/path.hd5", None))
        self.toolBar.setWindowTitle(_translate("Settings", "toolBar", None))
        self.actionSettingsSaveAs.setText(_translate("Settings", "Save as", None))
        self.actionSettingsSaveAs.setToolTip(_translate("Settings", "Save settings file as ...", None))
        self.actionSettingsOpen.setText(_translate("Settings", "Open", None))
        self.actionSettingsOpen.setToolTip(_translate("Settings", "Open settings file", None))
        self.actionSettingsImport.setText(_translate("Settings", "Import", None))
        self.actionSettingsImport.setToolTip(_translate("Settings", "Import file content", None))
        self.actionSettingsExport.setText(_translate("Settings", "Export", None))
        self.actionSettingsExport.setToolTip(_translate("Settings", "Export file content", None))
        self.actionSettingsSave.setText(_translate("Settings", "Save", None))
        self.actionSettingsSave.setToolTip(_translate("Settings", "Save settings changes and set file", None))

from mrsprint.gui import mrsprint_rc
