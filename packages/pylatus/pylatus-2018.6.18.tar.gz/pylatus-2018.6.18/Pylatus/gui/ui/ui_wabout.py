# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/satarsa/projects/python/pylatus/Pylatus/gui/ui/ui_wabout.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WAbout(object):
    def setupUi(self, WAbout):
        WAbout.setObjectName("WAbout")
        WAbout.setWindowModality(QtCore.Qt.ApplicationModal)
        WAbout.resize(656, 624)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(WAbout.sizePolicy().hasHeightForWidth())
        WAbout.setSizePolicy(sizePolicy)
        WAbout.setMaximumSize(QtCore.QSize(10000, 10000))
        WAbout.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout = QtWidgets.QVBoxLayout(WAbout)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(WAbout)
        self.label.setMaximumSize(QtCore.QSize(644, 259))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/snbl"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(WAbout)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.closeButton = QtWidgets.QPushButton(WAbout)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WAbout)
        QtCore.QMetaObject.connectSlotsByName(WAbout)

    def retranslateUi(self, WAbout):
        _translate = QtCore.QCoreApplication.translate
        WAbout.setWindowTitle(_translate("WAbout", "About Pylatus"))
        self.label_2.setText(_translate("WAbout", "<html><head/><body><p>Pylatus 2.0</p><p>Author: Vadim Dyadkin</p><p>Design: Dmitry Chernyshov</p><p>Special thanks to Roberto Homes</p><p>This program is licensed under GPL v3</p><p>More information at <a href=\"http://www.snbl.eu\"><span style=\" text-decoration: underline; color:#0000ff;\">www.snbl.eu</span></a></p><p><br/></p></body></html>"))
        self.closeButton.setText(_translate("WAbout", "Close"))

from . import resources_rc
