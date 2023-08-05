#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from qtsnbl.widgets import FixedWidget
from .ui.ui_wabout import Ui_WAbout


class WAbout(QtWidgets.QDialog, Ui_WAbout, FixedWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.fixWindow()
        if QtWidgets.QApplication.screens()[0].logicalDotsPerInch() <= 120:  # Hack for HiDPI displays
            self.label.setMaximumSize(QtCore.QSize(322, 130))

    @QtCore.pyqtSlot()
    def on_closeButton_clicked(self):
        self.close()
