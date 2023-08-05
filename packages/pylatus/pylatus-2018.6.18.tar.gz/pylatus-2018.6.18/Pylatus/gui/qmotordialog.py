#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from qtsnbl.widgets import FixedWidget
from ..controller.config import Config


class QMotorDialog(QtWidgets.QDialog, FixedWidget):
    sigClosed = QtCore.pyqtSignal()
    sigUpdateMotorViews = QtCore.pyqtSignal()
    sigMoveMotor = QtCore.pyqtSignal(str, float)
    sigStopAllMotors = QtCore.pyqtSignal()

    def __init__(self, parent, keyword):
        super().__init__(parent=parent)
        self.fixWindow()
        self.keyword = keyword

    def setupMotors(self):
        self.defineMotors()

    def defineMotors(self):
        self.motors = {}
        for widgetName, widget in self.__dict__.items():
            if isinstance(widget, QtWidgets.QAbstractSpinBox):
                # Take the motor name from 'sl01bSpinBox' cutting 'SpinBox': item[:-7]
                guiName = widgetName[:-len(self.keyword)]
                specName = getattr(Config, guiName.title(), guiName)
                self.motors[specName] = guiName

    def updateMotors(self):
        self.sigUpdateMotorViews.emit()

    def updateMotorPosition(self, name, position):
        if name in self.motors:
            sb = getattr(self, f'{self.motors[name]}{self.keyword}')
            if sb:
                sb.setValue(position)

    @QtCore.pyqtSlot()
    def on_sendButton_clicked(self):
        for name in self.motors:
            spinBox = getattr(self, f'{self.motors[name]}{self.keyword}')
            self.sigMoveMotor.emit(name, spinBox.value())

    @QtCore.pyqtSlot()
    def on_updateButton_clicked(self):
        self.updateMotors()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_F5:
            self.updateMotors()
        elif key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            widget = QtWidgets.QApplication.focusWidget()
            if not isinstance(widget, QtWidgets.QAbstractSpinBox):
                return
            name = widget.objectName()[:-len(self.keyword)]
            for specName, guiName in self.motors.items():
                if guiName == name:
                    self.sigMoveMotor.emit(specName, widget.value())
                    break

    def setConfig(self):
        self.setupMotors()
        self.updateMotors()
