#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from .qmotordialog import QMotorDialog
from .ui.ui_wstatus import Ui_WStatus
from ..controller.config import Config


class WStatus(QMotorDialog, Ui_WStatus):
    sigOpenShutter = QtCore.pyqtSignal()
    sigCloseShutter = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent, 'SpinBox')
        self.setupUi(self)

    def closeEvent(self, event):
        self.hide()
        self.saveSettings()
        self.sigClosed.emit()

    def saveSettings(self):
        s = Config.Settings
        s.setValue('WStatus/Geometry', self.saveGeometry())

    def loadSettings(self):
        s = Config.Settings
        self.restoreGeometry(s.value('WStatus/Geometry', b''))

    @QtCore.pyqtSlot()
    def on_buttonOpen_clicked(self):
        self.sigOpenShutter.emit()

    @QtCore.pyqtSlot()
    def on_buttonClose_clicked(self):
        self.sigCloseShutter.emit()
