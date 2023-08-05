#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
import auxygen
from .gutils import GUtils
from ..controller.chunks import PylatusScanParams
from ..controller.config import Config
from .ui.ui_wscan import Ui_WScan
from .ui.ui_scan_groupbox import Ui_groupBoxScan


class ScanGroupBox(QtWidgets.QGroupBox, Ui_groupBoxScan):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)


class WScan(QtWidgets.QDialog, Ui_WScan):
    sigClosed = QtCore.pyqtSignal()
    sigRun = QtCore.pyqtSignal(object)
    sigAbort = QtCore.pyqtSignal()
    sigMoveMotor = QtCore.pyqtSignal(str, float)
    sigUpdateMotorViews = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.currentMotor = ''
        self.rootMode = False
        self.motors = []
        self.setUI()
        self.connectSignals()

    def connectSignals(self):
        self.g.buttonRoot.clicked.connect(self.on_buttonRoot_clicked)
        self.g.buttonStop.clicked.connect(self.sigAbort.emit)
        self.g.buttonShot.clicked.connect(self.on_buttonShot_clicked)
        self.g.buttonStart.clicked.connect(self.on_buttonStart_clicked)
        self.g.comboMotor.currentIndexChanged[str].connect(self.on_comboMotor_currentIndexChanged)

    def showMotors(self):
        self.motors.sort()
        self.g.comboMotor.clear()
        self.g.comboMotor.addItems(self.motors)
        self.rootMode = False

    @auxygen.utils.split_motor_name
    def addMotor(self, name):
        if name not in self.motors:
            self.motors.append(name)
        self.showMotors()

    def addMotors(self, motors):
        for motor in motors:
            self.addMotor(motor)

    @auxygen.utils.split_motor_name
    def removeMotor(self, name):
        if name in self.motors:
            self.motors.remove(name)
        self.showMotors()

    def setConfig(self):
        self.g.spinFilter.setMaximum(int(Config.NumberOfFilters))

    def setUI(self):
        self.setupUi(self)
        self.g = ScanGroupBox()
        self.plot = pg.PlotWidget()
        self.proxy = pg.SignalProxy(self.plot.plotItem.scene().sigMouseMoved, rateLimit=60, slot=self.plotMouseMoved)
        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.g)
        self.splitter.addWidget(self.plot)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.splitter)
        self.setLayout(layout)

    def plotMouseMoved(self, event):
        pos = event[0]
        if self.plot.plotItem.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.plotItem.vb.mapSceneToView(pos)
            self.g.labelXPos.setText(f'{mousePoint.x():.6f}')
            self.g.labelYPos.setText(f'{mousePoint.y():.6f}')

    def showEvent(self, event):
        self.rootMode = False
        self.g.spinFrom.setDisabled(True)
        self.g.spinTo.setDisabled(True)
        self.g.spinPoints.setDisabled(True)
        self.g.spinExposure.setDisabled(True)
        self.g.buttonShot.setDisabled(True)
        self.g.buttonStop.setDisabled(True)
        self.g.spinFilter.setDisabled(True)
        self.g.comboMotor.setDisabled(True)
        self.g.comboMotor.setCurrentIndex(self.g.comboMotor.findText(Config.ScanAxis))

    def on_buttonRoot_clicked(self):
        if GUtils.askPass(self):
            self.rootMode = True
            self.g.spinFrom.setEnabled(True)
            self.g.spinTo.setEnabled(True)
            self.g.spinPoints.setEnabled(True)
            self.g.spinExposure.setEnabled(True)
            self.g.buttonShot.setEnabled(True)
            self.g.buttonStop.setEnabled(True)
            self.g.spinFilter.setEnabled(True)
            self.g.comboMotor.setEnabled(True)

    def closeEvent(self, event):
        self.sigAbort.emit()
        self.hide()
        self.saveSettings()
        self.scanFinished()
        self.sigClosed.emit()

    def saveSettings(self):
        s = Config.Settings
        s.setValue('WScan/Geometry', self.saveGeometry())
        s.setValue('WScan/SplitterGeometry', self.splitter.saveGeometry())
        s.setValue('WScan/SplitterState', self.splitter.saveState())
        s.setValue('WScan/from', self.g.spinFrom.value())
        s.setValue('WScan/to', self.g.spinTo.value())
        s.setValue('WScan/points', self.g.spinPoints.value())
        s.setValue('WScan/exposure', self.g.spinExposure.value())
        s.setValue('WScan/filter', self.g.spinFilter.value())

    def loadSettings(self):
        s = Config.Settings
        self.restoreGeometry(s.value('WScan/Geometry', b''))
        self.splitter.restoreGeometry(s.value('WScan/SplitterGeometry', b''))
        self.splitter.restoreState(s.value('WScan/SplitterState', b''))
        self.g.spinFrom.setValue(s.value('WScan/from', 0, float))
        self.g.spinTo.setValue(s.value('WScan/to', 0, float))
        self.g.spinPoints.setValue(s.value('WScan/points', 0, float))
        self.g.spinExposure.setValue(s.value('WScan/exposure', 1, float))
        self.g.spinFilter.setValue(s.value('WScan/filter', 7, int))

    def startScan(self, params):
        self.x, self.y = [], []
        self.g.buttonStart.setDisabled(True)
        self.g.buttonShot.setDisabled(True)
        self.g.buttonStop.setEnabled(True)
        self.sigRun.emit(params)

    def scanFinished(self):
        self.g.buttonStart.setEnabled(True)
        if self.rootMode:
            self.g.buttonShot.setEnabled(True)
        self.g.buttonStop.setDisabled(True)

    def on_comboMotor_currentIndexChanged(self, motor):
        if self.g.comboMotor.currentIndex() > -1 and motor in self.motors:
            self.currentMotor = motor
            self.g.labelCurrentMotor.setText(f'{motor}:')
            self.sigUpdateMotorViews.emit()

    def on_buttonShot_clicked(self):
        pos = self.g.spinFrom.value()
        axis = self.g.comboMotor.currentText()
        self.sigMoveMotor.emit(axis, pos)

    def on_buttonStart_clicked(self):
        params = PylatusScanParams()
        if self.rootMode:
            params.auto = False
            params.axis = self.g.comboMotor.currentText()
            params.expPeriod = self.g.spinExposure.value()
            params.start = self.g.spinFrom.value()
            params.stop = self.g.spinTo.value()
            params.step = self.g.spinPoints.value()
            params.nfilter = self.g.spinFilter.value()
            if not params.axis:
                return
        self.startScan(params)

    def plotCurve(self, x, y):
        self.plot.plot(x, y, pen='g', clear=True)

    def plotGauss(self, x, y, xc):
        text = pg.TextItem(html=f'<div style="text-align: center"><span style="color: #FF0; font-size: 16pt;">'
                                f'Xc = {xc:f}</span></div>', anchor=(-0.3, 1.3), border='w', fill=(0, 0, 255, 100))
        self.plot.addItem(text)
        text.setPos(xc, y.max())
        self.plot.plot(x, y, pen='r', clear=False)

    def updateMotorPosition(self, name, position):
        if name == self.currentMotor:
            self.g.labelCurrentPosition.setText(f'{position:.5f}')
