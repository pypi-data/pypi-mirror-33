# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/satarsa/projects/python/pylatus/Pylatus/gui/ui/ui_wrelmove.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WRelMove(object):
    def setupUi(self, WRelMove):
        WRelMove.setObjectName("WRelMove")
        WRelMove.resize(399, 364)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/relative"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WRelMove.setWindowIcon(icon)
        WRelMove.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(WRelMove)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.addButton = QtWidgets.QPushButton(WRelMove)
        self.addButton.setObjectName("addButton")
        self.gridLayout.addWidget(self.addButton, 1, 2, 1, 2)
        self.motorsComboBox = QtWidgets.QComboBox(WRelMove)
        self.motorsComboBox.setEditable(True)
        self.motorsComboBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.motorsComboBox.setMinimumContentsLength(0)
        self.motorsComboBox.setFrame(True)
        self.motorsComboBox.setObjectName("motorsComboBox")
        self.gridLayout.addWidget(self.motorsComboBox, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(WRelMove)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 2)
        self.rootButton = QtWidgets.QPushButton(WRelMove)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/hammer"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rootButton.setIcon(icon1)
        self.rootButton.setObjectName("rootButton")
        self.gridLayout.addWidget(self.rootButton, 1, 4, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2.addLayout(self.verticalLayout)
        spacerItem2 = QtWidgets.QSpacerItem(20, 341, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)

        self.retranslateUi(WRelMove)
        self.motorsComboBox.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(WRelMove)

    def retranslateUi(self, WRelMove):
        _translate = QtCore.QCoreApplication.translate
        WRelMove.setWindowTitle(_translate("WRelMove", "Pylatus relative movements"))
        self.addButton.setText(_translate("WRelMove", "Add"))
        self.label.setText(_translate("WRelMove", "Available motors"))
        self.rootButton.setText(_translate("WRelMove", "Root"))

from . import resources_rc
