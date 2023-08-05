#!/usr/bin/python
# -*- coding: utf-8 -*-

from .qmotordialog import QMotorDialog
from .ui.ui_walign import Ui_WBeamAlign
from ..controller.config import Config


class WAlign(QMotorDialog, Ui_WBeamAlign):
    def __init__(self, parent):
        super().__init__(parent, 'SpinBox')
        self.setupUi(self)

    def closeEvent(self, event):
        self.hide()
        self.saveSettings()
        self.sigClosed.emit()

    def saveSettings(self):
        s = Config.Settings
        s.setValue('WAlign/Geometry', self.saveGeometry())

    def loadSettings(self):
        s = Config.Settings
        self.restoreGeometry(s.value('WAlign/Geometry', b''))
