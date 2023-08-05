# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/satarsa/projects/python/pylatus/Pylatus/gui/ui/ui_wscan.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WScan(object):
    def setupUi(self, WScan):
        WScan.setObjectName("WScan")
        WScan.resize(400, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/scan"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WScan.setWindowIcon(icon)
        WScan.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))

        self.retranslateUi(WScan)
        QtCore.QMetaObject.connectSlotsByName(WScan)

    def retranslateUi(self, WScan):
        _translate = QtCore.QCoreApplication.translate
        WScan.setWindowTitle(_translate("WScan", "Pylatus Scan"))

from . import resources_rc
