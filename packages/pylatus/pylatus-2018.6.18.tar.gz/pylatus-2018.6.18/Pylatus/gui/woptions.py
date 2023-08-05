#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui
from ..controller.config import Config
from ..controller.utils import hash_pass
from .ui.ui_options import Ui_Ui_Settings


class WOptions(QtWidgets.QDialog, Ui_Ui_Settings):
    sigConfig = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.password = ''
        self.setUI()

    def setUI(self):
        self.setupUi(self)
        self.editReadout1.setValidator(QtGui.QDoubleValidator())
        self.editReadout2.setValidator(QtGui.QDoubleValidator())
        self.editSeparator.setValidator(QtGui.QIntValidator())
        self.editNoBeamCounts.setValidator(QtGui.QIntValidator())
        self.editMusstTimeout1.setValidator(QtGui.QDoubleValidator())
        self.editMusstTimeout2.setValidator(QtGui.QDoubleValidator())
        self.editNumberOfFilters.setValidator(QtGui.QIntValidator())
        self.editBeamstopOn.setValidator(QtGui.QDoubleValidator())
        self.editBeamstopOff.setValidator(QtGui.QDoubleValidator())
        self.editScanTime.setValidator(QtGui.QDoubleValidator())
        self.editScanRange.setValidator(QtGui.QDoubleValidator())
        self.editScanStep.setValidator(QtGui.QIntValidator())
        self.editScanFilter.setValidator(QtGui.QIntValidator())
        self.editMonitorMult.setValidator(QtGui.QDoubleValidator())
        self.editTimescan.setValidator(QtGui.QDoubleValidator())
        self.editMonoOffset.setValidator(QtGui.QDoubleValidator())
        self.editMonoDspacing.setValidator(QtGui.QDoubleValidator())
        self.editMonMeasTime.setValidator(QtGui.QDoubleValidator())
        self.editThresholdTimeout.setValidator(QtGui.QDoubleValidator())
        self.editShutterClosed.setValidator(QtGui.QDoubleValidator())
        self.editShutterCollimated.setValidator(QtGui.QDoubleValidator())
        self.editShutterOpen.setValidator(QtGui.QDoubleValidator())

    def loadSettings(self):
        s = Config.Settings
        self.restoreGeometry(s.value('WOptions/Geometry', b''))
        for fullname, widget in self.__dict__.items():
            name = fullname[4:]
            value = getattr(Config, name, None)
            if value is None:
                continue
            if isinstance(widget, QtWidgets.QLineEdit):
                type_ = str
                lambda_ = widget.setText
            elif isinstance(widget, QtWidgets.QCheckBox):
                type_ = bool
                lambda_ = widget.setChecked
            else:
                continue
            value = s.value(f'WOptions/{name}', value, type_)
            lambda_(value)
            setattr(Config, name, value)
        self.saveSettings()

    def saveSettings(self):
        s = Config.Settings
        s.setValue('WOptions/Geometry', self.saveGeometry())
        for fullname, widget in self.__dict__.items():
            name = fullname[4:]
            if isinstance(widget, QtWidgets.QLineEdit):
                value = widget.text()
            elif isinstance(widget, QtWidgets.QCheckBox):
                value = widget.isChecked()
            else:
                continue
            s.setValue(f'WOptions/{name}', value)
            setattr(Config, name, value)
        self.sigConfig.emit()

    @QtCore.pyqtSlot()
    def on_applyButton_clicked(self):
        if self.password:
            self.editRootHash.setText(hash_pass(self.password))
            self.password = ''
        self.saveSettings()
        self.close()

    @QtCore.pyqtSlot()
    def on_cancelButton_clicked(self):
        self.close()

    def showEvent(self, event):
        self.password = ''
        self.loadSettings()
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.hide()
        self.saveSettings()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            pass
        else:
            super().keyPressEvent(event)

    @QtCore.pyqtSlot(str)
    def on_editRootHash_textEdited(self, text):
        self.password = text
