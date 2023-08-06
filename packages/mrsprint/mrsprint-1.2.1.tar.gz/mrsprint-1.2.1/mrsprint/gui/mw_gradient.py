# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mw_gradient.ui'
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

class Ui_Gradient(object):
    def setupUi(self, Gradient):
        Gradient.setObjectName(_fromUtf8("Gradient"))
        Gradient.resize(194, 258)
        self.centralwidget = QtGui.QWidget(Gradient)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBoxApplyOn = QtGui.QGroupBox(self.centralwidget)
        self.groupBoxApplyOn.setObjectName(_fromUtf8("groupBoxApplyOn"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBoxApplyOn)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.radioButtonColumn = QtGui.QRadioButton(self.groupBoxApplyOn)
        self.radioButtonColumn.setObjectName(_fromUtf8("radioButtonColumn"))
        self.gridLayout_2.addWidget(self.radioButtonColumn, 1, 1, 1, 1)
        self.radioButtonRow = QtGui.QRadioButton(self.groupBoxApplyOn)
        self.radioButtonRow.setObjectName(_fromUtf8("radioButtonRow"))
        self.gridLayout_2.addWidget(self.radioButtonRow, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBoxApplyOn, 0, 0, 1, 1)
        self.groupBoxRange = QtGui.QGroupBox(self.centralwidget)
        self.groupBoxRange.setObjectName(_fromUtf8("groupBoxRange"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBoxRange)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.doubleSpinBoxStart = QtGui.QDoubleSpinBox(self.groupBoxRange)
        self.doubleSpinBoxStart.setObjectName(_fromUtf8("doubleSpinBoxStart"))
        self.gridLayout_3.addWidget(self.doubleSpinBoxStart, 0, 1, 1, 1)
        self.doubleSpinBoxEnd = QtGui.QDoubleSpinBox(self.groupBoxRange)
        self.doubleSpinBoxEnd.setObjectName(_fromUtf8("doubleSpinBoxEnd"))
        self.gridLayout_3.addWidget(self.doubleSpinBoxEnd, 1, 1, 1, 1)
        self.labelStart = QtGui.QLabel(self.groupBoxRange)
        self.labelStart.setObjectName(_fromUtf8("labelStart"))
        self.gridLayout_3.addWidget(self.labelStart, 0, 0, 1, 1)
        self.labelEnd = QtGui.QLabel(self.groupBoxRange)
        self.labelEnd.setObjectName(_fromUtf8("labelEnd"))
        self.gridLayout_3.addWidget(self.labelEnd, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBoxRange, 1, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)
        Gradient.setCentralWidget(self.centralwidget)

        self.retranslateUi(Gradient)
        QtCore.QMetaObject.connectSlotsByName(Gradient)

    def retranslateUi(self, Gradient):
        Gradient.setWindowTitle(_translate("Gradient", "Grandient", None))
        self.groupBoxApplyOn.setTitle(_translate("Gradient", "Apply on", None))
        self.radioButtonColumn.setText(_translate("Gradient", "Columns", None))
        self.radioButtonRow.setText(_translate("Gradient", "Rows", None))
        self.groupBoxRange.setTitle(_translate("Gradient", "Range", None))
        self.labelStart.setText(_translate("Gradient", "Start", None))
        self.labelEnd.setText(_translate("Gradient", "End", None))

from mrsprint.gui import mrsprint_rc
