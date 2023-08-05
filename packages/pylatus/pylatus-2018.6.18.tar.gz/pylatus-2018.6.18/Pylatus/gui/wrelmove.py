#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sip
from PyQt5 import QtCore, QtGui, QtWidgets
import auxygen
from .ui.ui_wrelmove import Ui_WRelMove
from .gutils import GUtils
from ..controller.config import Config


class WRelMove(QtWidgets.QDialog, Ui_WRelMove):
    sigClosed = QtCore.pyqtSignal()
    sigMoveMotor = QtCore.pyqtSignal(str, float)
    sigMoveMotorRelative = QtCore.pyqtSignal(str, float)
    sigStopAllMotors = QtCore.pyqtSignal(str)
    sigUpdateMotorViews = QtCore.pyqtSignal()
    sigCreateSeqAction = QtCore.pyqtSignal(dict, object)
    sigRunSeqAction = QtCore.pyqtSignal(dict, object)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.motors = set()
        self.userMotors = set()
        self.names = {}
        self.snames = []
        self.root = False
        self.kappa = True
        self.setUI()
        self.resizeToMinimum()
        self.connectSignals()

    def connectSignals(self):
        self.sigRunSeqAction.connect(self.runAction)

    def createAction(self, name: str, spin: QtWidgets.QDoubleSpinBox):
        self.sigCreateSeqAction.emit({
            f'Move motor {name} to {spin.value():.3f}': f'{name}={spin.value():.3f}'
        }, self.sigRunSeqAction)

    def runAction(self, action: dict, signal):
        if signal:
            item = list(action.values())[0]
            name, value = item.split('=')
            value = float(value)
            self.sigMoveMotor.emit(name, value)
            signal.emit()

    def showEvent(self, event: QtGui.QShowEvent):
        self.appendMotors(self.motors & self.userMotors)
        super().showEvent(event)

    def setUI(self):
        self.setupUi(self)
        self.addButton.setIcon(QtGui.QIcon(':/add'))

    def setConfig(self):
        self.userMotors = {
            Config.Pldistf,
            Config.Plrot,
            Config.Pldistd,
            Config.Plvert,
            Config.Prver,
            Config.Prhor
        }
        self.setOmegaPhi()

    def setMotors(self, motors):
        self.motors = set()
        for motor in motors:
            self.setMotor(motor)

    @auxygen.utils.split_motor_name
    def setMotor(self, name):
        self.motors.add(name)
        self.setKappa(self.kappa)

    @auxygen.utils.split_motor_name
    def removeMotor(self, name):
        self.motors.discard(name)
        self.setKappa(self.kappa)

    def setOmegaPhi(self):
        self.setKappa(True)

    def setPrphi(self):
        self.setKappa(False)

    def setKappa(self, isKappa):
        self.kappa = isKappa
        kappa = {Config.Kappa, Config.Phi, Config.Omega}
        prphi = {Config.Prphi}
        if isKappa:
            self.userMotors |= kappa
            self.userMotors ^= prphi
        else:
            self.userMotors ^= kappa
            self.userMotors |= prphi
        self.appendMotors(self.motors & self.userMotors)

    def appendMotors(self, motors=None):
        motors = motors or self.motors
        self.motorsComboBox.clear()
        self.motorsComboBox.addItems(sorted(motors))
        self.motorsComboBox.setCurrentIndex(-1)

    def closeEvent(self, event):
        self.hide()
        self.saveSettings()
        self.sigClosed.emit()
        super().closeEvent(event)

    def saveSettings(self):
        _ = Config.Settings.setValue
        _('WRelMove/Geometry', self.saveGeometry())
        _('WRelMove/motors', json.dumps(list(self.names.keys())))

    def loadSettings(self):
        _ = Config.Settings.value
        self.restoreGeometry(_('WRelMove/Geometry', b''))
        self.snames = json.loads(_('WRelMove/motors', '[]', str))
        self.restoreMotors()

    @QtCore.pyqtSlot(str)
    def on_motorsComboBox_activated(self, motorName):
        if motorName not in self.motors:
            return
        self.motorsComboBox.clearEditText()
        self.createMotorView(motorName)

    @QtCore.pyqtSlot()
    def on_addButton_clicked(self):
        self.on_motorsComboBox_activated(self.motorsComboBox.currentText())

    @QtCore.pyqtSlot()
    def on_rootButton_clicked(self):
        if GUtils.askPass(self):
            self.appendMotors(self.motors)

    def restoreMotors(self):
        for name in self.snames:
            self.createMotorView(name)

    def createMotorView(self, name):
        if name in self.names or name not in self.motors:
            return
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText(name)
        spinAbs = QtWidgets.QDoubleSpinBox()
        spinRel = QtWidgets.QDoubleSpinBox()
        self.names[name] = spinAbs
        spinAbs.setDecimals(4)
        spinAbs.setMaximum(100000)
        spinAbs.setMinimum(-100000)
        spinAbs.setSingleStep(0.1)
        spinAbs.setValue(0)
        spinAbs.editingFinished.connect(lambda: self.moveMotor(True, name, spinAbs))
        spinRel.setDecimals(4)
        spinRel.setMaximum(100000)
        spinRel.setMinimum(-100000)
        spinRel.setSingleStep(0.1)
        spinRel.setValue(0)
        spinRel.editingFinished.connect(lambda: self.moveMotorRelative(True, name, spinRel))
        buttonRunAbs = QtWidgets.QToolButton()
        buttonRunAbs.setIcon(QtGui.QIcon(':/run'))
        buttonRunAbs.clicked.connect(lambda: self.moveMotor(False, name, spinAbs))
        buttonSeq = QtWidgets.QToolButton()
        buttonSeq.setIcon(QtGui.QIcon(':/macro'))
        buttonSeq.clicked.connect(lambda: self.createAction(name, spinAbs))
        buttonRunRel = QtWidgets.QToolButton()
        buttonRunRel.setIcon(QtGui.QIcon(':/run'))
        buttonRunRel.clicked.connect(lambda: self.moveMotorRelative(False, name, spinRel))
        buttonStop = QtWidgets.QToolButton()
        buttonStop.setIcon(QtGui.QIcon(':/stop'))
        buttonStop.clicked.connect(lambda: self.sigStopAllMotors.emit(name))
        buttonDel = QtWidgets.QToolButton()
        style = QtWidgets.QApplication.style()
        buttonDel.setIcon(style.standardIcon(style.SP_DialogCancelButton))
        buttonDel.clicked.connect(lambda: self.removeMotorView(layout, name))
        layout.addWidget(label)
        layout.addWidget(buttonStop)
        layout.addWidget(spinAbs)
        layout.addWidget(buttonRunAbs)
        layout.addWidget(buttonSeq)
        layout.addWidget(spinRel)
        layout.addWidget(buttonRunRel)
        layout.addWidget(buttonDel)
        self.verticalLayout.addLayout(layout)
        self.sigUpdateMotorViews.emit()
        self.saveSettings()

    def resizeToMinimum(self):
        QtCore.QTimer.singleShot(10, lambda: self.resize(0, 0))

    def removeMotorView(self, layout, name):
        for widget in [layout.itemAt(i).widget() for i in range(layout.count())]:
            sip.delete(widget)
        del self.names[name]
        self.verticalLayout.removeItem(layout)
        self.resizeToMinimum()
        self.saveSettings()

    def moveMotor(self, checkFocus: bool, name: str, spinBox: QtWidgets.QDoubleSpinBox):
        if checkFocus and not spinBox.hasFocus():
            return
        self.sigMoveMotor.emit(name, spinBox.value())

    def moveMotorRelative(self, checkFocus: bool, name: str, spinBox: QtWidgets.QDoubleSpinBox):
        if checkFocus and not spinBox.hasFocus():
            return
        self.sigMoveMotorRelative.emit(name, spinBox.value())

    def updateMotorPosition(self, name: str, position: float):
        if name in self.names:
            self.names[name].setValue(position)

    def keyPressEvent(self, event):
        if event.key() != QtCore.Qt.Key_Escape:
            super().keyPressEvent(event)
