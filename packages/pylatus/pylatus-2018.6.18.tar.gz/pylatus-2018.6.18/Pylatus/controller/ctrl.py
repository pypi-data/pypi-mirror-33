#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import math
import json
from PyQt5 import QtCore
import auxygen
import integracio
from . import chunks
from ..gui import wmain, wstatus, wuserstatus, wrelmove, walign
from ..gui import wscan, woptions
from ..gui.gutils import GUtils
from ..devices import diffractometer, monitor
from .config import Config
from .. import scripo
from .rmq import RabbitMQ


class Controller(QtCore.QObject):
    sigConnectMotors = QtCore.pyqtSignal(list)
    sigConnectMotor = QtCore.pyqtSignal(str)
    sigMax2Theta = QtCore.pyqtSignal(float, float)
    sigDCTime = QtCore.pyqtSignal(int, int, int, float)
    sigExpTimeLeft = QtCore.pyqtSignal(str)
    sigGUIStarted = QtCore.pyqtSignal()
    sigStartExperiment = QtCore.pyqtSignal(object)
    sigExperimentChunk = QtCore.pyqtSignal(object)
    sigUpdateWavelength = QtCore.pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.createObjects()
        self.createRabbitMQ()
        self.createWindows()
        self.createDevices()
        self.createScripo()
        self.connectSignals()

    def createObjects(self):
        Config.Settings = QtCore.QSettings()
        self.started = False
        self.motors = []
        self.expTime = 0
        self.expStarted = 0
        self.expPaused = 0
        self.wavelength = 0
        self.lakeshoreSensor = 'A'
        self.p = None
        self.expTimer = QtCore.QTimer()
        self.expTimer.setInterval(1000)

    def createRabbitMQ(self):
        self.rabbitmq = RabbitMQ()
        self.threadRabbitmq = QtCore.QThread()
        self.rabbitmq.moveToThread(self.threadRabbitmq)
        self.rmqConnected = False

    def createWindows(self):
        self.wmain = wmain.WMain()
        self.wlogging = auxygen.gui.wlogging.WLogging(self.wmain)
        self.wstatus = wstatus.WStatus(self.wmain)
        self.wuserstatus = wuserstatus.WUserStatus(self.wmain)
        self.wrelmove = wrelmove.WRelMove(self.wmain)
        self.walign = walign.WAlign(self.wmain)
        self.wscan = wscan.WScan(self.wmain)
        self.wlakeshore = auxygen.gui.wlakeshore.WLakeshore(self.wmain)
        self.wblower = auxygen.gui.wblower.WBlower(self.wmain)
        self.wcryo = auxygen.gui.wcryo.WCryo(self.wmain)
        self.wseq = auxygen.gui.wseq.WSeq(self.wmain)
        self.woptions = woptions.WOptions(self.wmain)
        self.wiseg = auxygen.gui.wiseg.WIseg(self.wmain)

    def createScripo(self):
        self.scripts = {
            'diffractometer': scripo.diffractometer.Diffractometer(),
            'blower': self.wblower.script,
            'cryostream': self.wcryo.script,
            'lakeshore': self.wlakeshore.script,
            'motor': auxygen.scripo.motor.Motor(),
            'musst': scripo.musst.Musst(),
            'iseg': self.wiseg.script,
        }
        self.wscripted = auxygen.gui.wscripted.WScriptEd(self.wmain, self.scripts)

    def createDevices(self):
        self.logger = auxygen.devices.logger.Logger('Pylatus')
        self.diffractometer = diffractometer.Diffractometer()
        self.monitor = monitor.Monitor()

    def connectSignals(self):
        self.connectInternalSignals()
        self.connectActionSignals()
        self.connectMotorSignals()
        self.connectGUISignals()
        self.connectDiffractometerSignals()
        self.connectBlowerSignals()
        self.connectIsegSignals()
        self.connectCryoSignals()
        self.connectScanSignals()
        self.connectLakeshoreSignals()
        self.connectSequenceSignals()
        self.connectScriptSignals()
        self.connectMonitorSignals()
        self.connectRabbitMQSignals()
        self.diffractometer.connectSignals()

    # noinspection PyUnresolvedReferences
    def connectInternalSignals(self):
        self.expTimer.timeout.connect(self.calcExpTime)
        self.woptions.sigConfig.connect(self.wrelmove.setConfig)
        self.woptions.sigConfig.connect(self.wstatus.setConfig)
        self.woptions.sigConfig.connect(self.wuserstatus.setConfig)
        self.woptions.sigConfig.connect(self.walign.setConfig)
        self.woptions.sigConfig.connect(self.wscan.setConfig)
        self.woptions.sigConfig.connect(self.diffractometer.setConfig)
        self.woptions.sigConfig.connect(self.diffractometer.pilatus.setConfig)
        self.woptions.sigConfig.connect(self.monitor.setConfig)
        self.woptions.sigConfig.connect(self.diffractometer.musst.setConfig)
        self.woptions.sigConfig.connect(self.rabbitmq.setConfig)
        self.woptions.sigConfig.connect(self.continueStart)
        self.logger.logger.sigPostLogMessage.connect(self.wlogging.postLogMessage)
        self.sigStartExperiment.connect(self.diffractometer.startExperiment)
        self.sigStartExperiment.connect(self.setExperimentTime)
        self.sigExperimentChunk.connect(self.rabbitmq.sendChunk)

    def connectActionSignals(self):
        self.wmain.sigClose.connect(self.stop)
        self.wmain.actionLogging.toggled[bool].connect(self.wlogging.setVisible)
        self.wlogging.sigClosed.connect(lambda: self.wmain.actionLogging.setChecked(False))
        self.wstatus.sigClosed.connect(lambda: self.wmain.actionStatus.setChecked(False))
        self.wmain.actionStatus.toggled[bool].connect(self.showStatusWindow)
        self.wuserstatus.sigClosed.connect(lambda: self.wmain.actionUserStatus.setChecked(False))
        self.wuserstatus.sigShowRelativeWindow.connect(self.wmain.actionRelMove.trigger)
        self.wmain.actionUserStatus.toggled[bool].connect(self.wuserstatus.setVisible)
        self.wrelmove.sigClosed.connect(lambda: self.wmain.actionRelMove.setChecked(False))
        self.wmain.actionRelMove.toggled[bool].connect(self.wrelmove.setVisible)
        self.walign.sigClosed.connect(lambda: self.wmain.actionAlignment.setChecked(False))
        self.wmain.actionAlignment.toggled[bool].connect(self.showAlignWindow)
        self.wscan.sigClosed.connect(lambda: self.wmain.actionGeneralScan.setChecked(False))
        self.wmain.actionGeneralScan.toggled[bool].connect(self.wscan.setVisible)
        self.wseq.sigClosed.connect(lambda: self.wmain.actionSequence.setChecked(False))
        self.wmain.actionSequence.toggled[bool].connect(self.wseq.setVisible)
        self.wscripted.sigClosed.connect(lambda: self.wmain.actionScriptEditor.setChecked(False))
        self.wmain.actionScriptEditor.toggled[bool].connect(self.wscripted.setVisible)
        self.wmain.settingsButton.clicked.connect(self.woptions.exec)

    def connectMotorSignals(self):
        self.wmain.sigReconnectMotors.connect(self.diffractometer.connectSpec)
        self.sigConnectMotors.connect(self.diffractometer.setMotors)
        self.sigConnectMotors.connect(self.wmain.showMotorsList)
        self.sigConnectMotors.connect(self.wrelmove.setMotors)
        self.sigConnectMotors.connect(self.wscan.addMotors)
        self.sigConnectMotors.connect(self.scripts['motor']._addMotors)
        self.wmain.sigConnectMotor.connect(self.addMotor)
        self.sigConnectMotor.connect(self.wmain.showMotor)
        self.sigConnectMotor.connect(self.diffractometer.connectGUIMotor)
        self.sigConnectMotor.connect(self.wrelmove.setMotor)
        self.sigConnectMotor.connect(self.wscan.addMotor)
        self.sigConnectMotor.connect(self.scripts['motor']._addMotor)
        self.sigConnectMotor.connect(self.wuserstatus.setConfig)
        self.sigConnectMotor.connect(self.wstatus.setConfig)
        self.wmain.sigRemoveMotor.connect(self.removeMotor)
        self.wmain.sigRemoveMotor.connect(self.diffractometer.deleteMotor)
        self.wmain.sigRemoveMotor.connect(self.wrelmove.removeMotor)
        self.wmain.sigRemoveMotor.connect(self.wscan.removeMotor)
        self.wmain.sigRemoveMotor.connect(self.scripts['motor']._removeMotor)
        self.diffractometer.sigWavelength.connect(self.setWavelength)
        self.diffractometer.sigWavelength.connect(self.wuserstatus.setWavelength)
        self.diffractometer.sigEnergy.connect(self.wuserstatus.setEnergy)
        self.diffractometer.sigMotorMoved.connect(self.wuserstatus.updateMotorPosition)
        self.diffractometer.sigMotorMoved.connect(self.wstatus.updateMotorPosition)
        self.diffractometer.sigMotorMoved.connect(self.walign.updateMotorPosition)
        self.diffractometer.sigMotorMoved.connect(self.wrelmove.updateMotorPosition)
        self.diffractometer.sigMotorMoved.connect(self.wscan.updateMotorPosition)
        self.wrelmove.sigUpdateMotorViews.connect(self.diffractometer.updateMotorViews)
        self.wrelmove.sigCreateSeqAction.connect(lambda: self.wmain.actionSequence.setChecked(True))
        self.wrelmove.sigCreateSeqAction.connect(self.wseq.appendActionToSeqList)
        self.wrelmove.sigCreateSeqAction.connect(self.scripts['motor']._wait)
        self.wuserstatus.sigUpdateMotorViews.connect(self.diffractometer.updateMotorViews)
        self.wscan.sigUpdateMotorViews.connect(self.diffractometer.updateMotorViews)
        self.wrelmove.sigMoveMotorRelative.connect(self.diffractometer.moveMotorRelative)
        self.wrelmove.sigMoveMotor.connect(self.diffractometer.moveMotor)
        self.wrelmove.sigStopAllMotors.connect(self.diffractometer.stopAllMotors)
        self.wuserstatus.sigStopAllMotors.connect(self.diffractometer.stopAllMotors)
        self.wstatus.sigStopAllMotors.connect(self.diffractometer.stopAllMotors)
        self.walign.sigStopAllMotors.connect(self.diffractometer.stopAllMotors)
        self.wuserstatus.sigMoveMotor.connect(self.diffractometer.moveMotor)
        self.wstatus.sigMoveMotor.connect(self.diffractometer.moveMotor)
        self.walign.sigMoveMotor.connect(self.diffractometer.moveMotor)
        self.wmain.sigUpdateWavelength.connect(self.diffractometer.updateWavelength)
        self.sigUpdateWavelength.connect(self.diffractometer.updateWavelength)
        self.diffractometer.sigAllMotorsStopped.connect(self.scripts['motor']._allMotorsStopped)
        self.diffractometer.sigMotorStepSize.connect(self.scripts['motor']._setStepSize)

    def connectGUISignals(self):
        self.sigGUIStarted.connect(self.diffractometer.pilatus.setGuiStarted)
        self.sigMax2Theta.connect(self.wmain.showMax2Theta)
        self.wmain.pixelxSpinBox.valueChanged[float].connect(self.calcMax2Theta)
        self.wmain.beamxSpinBox.valueChanged[float].connect(self.calcMax2Theta)
        self.wmain.detectorxSpinBox.valueChanged[int].connect(self.calcMax2Theta)
        self.wmain.plvertSpinBox.valueChanged[float].connect(self.calcMax2Theta)
        self.wmain.pldistdSpinBox.valueChanged[float].connect(self.calcMax2Theta)
        self.wmain.zeroSpinBox.valueChanged[float].connect(self.calcMax2Theta)
        self.wmain.pldistfSpinBox.valueChanged[float].connect(self.calcMax2Theta)
        self.wmain.plrotSpinBox.valueChanged[float].connect(self.calcMax2Theta)
        self.wmain.exposureSpinBox.valueChanged[float].connect(self.calcDCTime)
        self.wmain.nframesSpinBox.valueChanged[int].connect(self.calcDCTime)
        self.wmain.nperiodsSpinBox.valueChanged[int].connect(self.calcDCTime)
        self.sigDCTime.connect(self.wmain.showDCTime)
        self.wmain.pauseBeamOffCheckBox.toggled[bool].connect(self.diffractometer.setMakePause)
        self.wmain.sigSetMinPlvert.connect(self.diffractometer.setMinPlvert)
        self.wmain.omegaMaxSpinBox.valueChanged[float].connect(self.diffractometer.setOmegaMaxVelocity)
        self.wmain.phiMaxSpinBox.valueChanged[float].connect(self.diffractometer.setPhiMaxVelocity)
        self.wmain.prphiMaxSpinBox.valueChanged[float].connect(self.diffractometer.setPrphiMaxVelocity)
        self.wmain.sigSetPhiScan.connect(self.diffractometer.setPhiScan)
        self.wmain.sigSetPhiScan.connect(self.wuserstatus.setOmegaPhi)
        self.wmain.sigSetPhiScan.connect(self.wrelmove.setOmegaPhi)
        self.wmain.sigSetPhiScan.connect(self.scripts['diffractometer']._setPhiScan)
        self.wmain.sigSetOmegaScan.connect(self.diffractometer.setOmegaScan)
        self.wmain.sigSetOmegaScan.connect(self.wuserstatus.setOmegaPhi)
        self.wmain.sigSetOmegaScan.connect(self.wrelmove.setOmegaPhi)
        self.wmain.sigSetOmegaScan.connect(self.scripts['diffractometer']._setOmegaScan)
        self.wmain.sigSetPrphiScan.connect(self.diffractometer.setPrphiScan)
        self.wmain.sigSetPrphiScan.connect(self.wuserstatus.setPrphi)
        self.wmain.sigSetPrphiScan.connect(self.wrelmove.setPrphi)
        self.wmain.sigSetPrphiScan.connect(self.scripts['diffractometer']._setOmegaScan)
        self.wmain.sigConnectDetector.connect(self.diffractometer.pilatus.connectDetector)
        self.wmain.sigStartExperiment.connect(self.startExperiment)
        self.sigExpTimeLeft.connect(self.wmain.showTimeLeft)
        self.wmain.sigPoni.connect(self.openPoni)

    def connectDiffractometerSignals(self):
        self.diffractometer.sigExperimentResumed.connect(self.setExperimentTime)
        self.diffractometer.sigExperimentFinished.connect(lambda: self.sigExperimentChunk.emit(
                                                                    chunks.PylatusExperimentFinished()))
        self.diffractometer.sigExperimentFinished.connect(self.wmain.experimentFinished)
        self.diffractometer.sigExperimentFinished.connect(self.expTimer.stop)
        self.diffractometer.sigExperimentFinished.connect(self.monitor.abort)
        self.diffractometer.sigExperimentParameters.connect(self.rabbitmq.sendChunk)
        self.diffractometer.sigExperimentStarted.connect(lambda: self.monitor.run(self.p.expPeriod))
        self.diffractometer.sigExperimentStarted.connect(self.expTimer.start)
        self.diffractometer.sigExperimentStarted.connect(self.wmain.experimentStarted)
        self.wmain.sigAbort.connect(self.diffractometer.abortExperiment)
        self.diffractometer.sigExperimentPaused.connect(self.pausedExperiment)
        self.wstatus.sigOpenShutter.connect(self.diffractometer.openShutter)
        self.wstatus.sigCloseShutter.connect(self.diffractometer.closeShutter)

    def connectMonitorSignals(self):
        self.monitor.sigBeamOn.connect(self.diffractometer.resumeExperiment)
        self.monitor.sigBeamOn.connect(self.wmain.setGreenLamp)
        self.monitor.sigBeamOff.connect(self.diffractometer.pauseExperiment)
        self.monitor.sigBeamOff.connect(self.wmain.setRedLamp)
        self.monitor.sigValue.connect(lambda v: self.sigExperimentChunk.emit(chunks.PylatusFlux(v)))
        self.monitor.sigValue.connect(self.wuserstatus.showMonitor)
        self.monitor.sigError.connect(self.logger.error)
        self.monitor.sigConnected.connect(lambda _: self.logger.info(f'Monitor {_} is connected'))

    def connectBlowerSignals(self):
        self.wblower.sigClosed.connect(lambda: self.wmain.actionBlower.setChecked(False))
        self.wmain.actionBlower.toggled[bool].connect(self.wblower.setVisible)
        self.diffractometer.sigExperimentResumed.connect(self.wblower.device.resume)
        self.diffractometer.sigExperimentPaused.connect(self.wblower.device.pause)
        self.diffractometer.sigExperimentPaused.connect(self.wblower.pause)
        self.diffractometer.sigExperimentResumed.connect(self.wblower.resume)
        self.wblower.device.sigTemperature.connect(lambda v: self.sigExperimentChunk.emit(chunks.PylatusBlower(v)))
        self.wblower.device.sigError.connect(self.logger.error)
        self.wblower.device.sigConnected.connect(lambda: self.logger.info('Blower is connected'))
        self.wblower.sigCreateSeqAction.connect(self.wseq.appendActionToSeqList)
        self.wblower.sigCreateSeqAction.connect(lambda: self.wmain.actionSequence.setChecked(True))
        self.wblower.script._sigCreateBlowerWaitAction.connect(self.wseq.appendActionToSeqList)
        self.wseq.sigBlowerWait.connect(self.wblower.script.wait)

    def connectIsegSignals(self):
        self.wiseg.sigClosed.connect(lambda: self.wmain.actionIsegHV.setChecked(False))
        self.wmain.actionIsegHV.toggled[bool].connect(self.wiseg.setVisible)
        self.wiseg.device.sigError.connect(self.logger.error)
        self.wiseg.device.sigConnected.connect(lambda: self.logger.info('Iseg is connected'))
        self.wiseg.sigCreateSeqAction.connect(self.wseq.appendActionToSeqList)
        self.wiseg.sigCreateSeqAction.connect(lambda: self.wmain.actionSequence.setChecked(True))
        self.wiseg.script._sigCreateIsegWaitAction.connect(self.wseq.appendActionToSeqList)
        self.wseq.sigIsegWait.connect(self.wiseg.script.wait)

    def connectCryoSignals(self):
        self.wcryo.device.sigStatus.connect(lambda v: self.sigExperimentChunk.emit(
                                                        chunks.PylatusTemperature(v['SampleTemp'])))
        self.wcryo.device.sigError.connect(self.logger.error)
        self.diffractometer.sigExperimentPaused.connect(self.wcryo.pause)
        self.diffractometer.sigExperimentResumed.connect(self.wcryo.resume)
        self.wcryo.script._sigCreateSeqWaitAction.connect(self.wseq.appendActionToSeqList)
        self.wcryo.sigCreateSeqAction.connect(self.wseq.appendActionToSeqList)
        self.wcryo.sigCreateSeqAction.connect(lambda: self.wmain.actionSequence.setChecked(True))
        self.wcryo.sigClosed.connect(lambda: self.wmain.actionCryostream.setChecked(False))
        self.wmain.actionCryostream.toggled[bool].connect(self.wcryo.setVisible)
        self.wseq.sigCryostreamWait.connect(self.wcryo.script.wait)

    def connectScanSignals(self):
        self.wscan.sigRun.connect(self.diffractometer.runScan)
        self.wscan.sigAbort.connect(self.diffractometer.abortScan)
        self.diffractometer.scanman.sigPoint.connect(self.wscan.plotCurve)
        self.diffractometer.scanman.sigFit.connect(self.wscan.plotGauss)
        self.diffractometer.scanman.sigScanStarted.connect(self.sigExperimentChunk.emit)
        self.diffractometer.scanman.sigScanStarted.connect(self.rabbitmq.scanStarted)
        self.diffractometer.sigScanFinished.connect(lambda: self.sigExperimentChunk.emit(
                                                                    chunks.PylatusExperimentFinished()))
        self.diffractometer.sigScanFinished.connect(self.wscan.scanFinished)
        self.diffractometer.sigScanFinished.connect(self.rabbitmq.scanFinished)

    def connectLakeshoreSignals(self):
        self.wlakeshore.sigClosed.connect(lambda: self.wmain.actionLakeshore.setChecked(False))
        self.wmain.actionLakeshore.toggled[bool].connect(self.wlakeshore.setVisible)
        self.wlakeshore.sigStoreSensor.connect(self.setLakeshoreSensor)
        self.wlakeshore.device.sigTemperature.connect(self.parseLakeshoreTemperature)
        self.wlakeshore.device.sigError.connect(self.logger.error)
        self.wlakeshore.sigCreateSeqAction.connect(self.wseq.appendActionToSeqList)
        self.wlakeshore.sigCreateSeqAction.connect(lambda: self.wmain.actionSequence.setChecked(True))
        self.wlakeshore.script._sigCreateSeqAction.connect(self.wseq.appendActionToSeqList)
        self.wseq.sigLakeshoreWait.connect(self.wlakeshore.script.wait)

    def connectSequenceSignals(self):
        self.wmain.sigCreateSeqAction.connect(self.wseq.appendActionToSeqList)
        self.wseq.sigStop.connect(self.diffractometer.abortExperiment)
        self.wmain.sigCreateSeqAction.connect(lambda: self.wmain.actionSequence.setChecked(True))
        self.scripts['diffractometer']._sigCreateSeqScanAction.connect(self.wmain.runFromScript)
        self.scripts['diffractometer']._sigCreateSeqAction.connect(self.wseq.appendActionToSeqList)
        self.scripts['diffractometer']._sigSetScanTypeInGUI.connect(self.wmain.setScanType)
        self.scripts['motor']._sigDiffWait.connect(self.diffractometer.waitForMotorsMovementFromScript)
        self.scripts['motor']._sigMoveFromSeq.connect(self.diffractometer.moveMotor)
        self.scripts['motor']._sigMoveRelFromSeq.connect(self.diffractometer.moveMotorRelative)
        self.scripts['motor']._sigCreateSeqAction.connect(self.wseq.appendActionToSeqList)
        self.wseq.sigSleep.connect(self.scripts['diffractometer'].sleep)
        self.scripts['musst']._sigCreateSeqAction.connect(self.wseq.appendActionToSeqList)
        self.scripts['musst']._sigOpenShutter.connect(self.diffractometer.openShutter)
        self.scripts['musst']._sigCloseShutter.connect(self.diffractometer.closeShutter)
        self.scripts['musst']._sigTrigChannel.connect(self.diffractometer.musst.trigChannel)

    def connectScriptSignals(self):
        self.wscripted.sigStart.connect(lambda: self.wmain.actionSequence.setChecked(True))

    # noinspection PyUnresolvedReferences
    def connectRabbitMQSignals(self):
        self.threadRabbitmq.started.connect(self.rabbitmq.start)
        self.threadRabbitmq.finished.connect(self.rabbitmq.stop)
        self.rabbitmq.sigConnected.connect(self.setRmqConnected)
        self.rabbitmq.sigDisconnected.connect(self.setRmqDisconnected)
        self.rabbitmq.sigScanValue.connect(self.diffractometer.scanman.addValue)

    def start(self):
        self.loadSettings()
        self.woptions.loadSettings()

    def continueStart(self):
        self.logger.logger.setFile(Config.LogFile)
        if self.started:
            return
        self.started = True
        self.threadRabbitmq.start()
        self.diffractometer.start()
        self.monitor.start()
        self.wmain.loadSettings()
        self.wuserstatus.loadSettings()
        self.wstatus.loadSettings()
        self.walign.loadSettings()
        self.wscan.loadSettings()
        self.wrelmove.loadSettings()
        self.wlakeshore.loadSettings()
        self.wseq.loadSettings()
        self.wblower.loadSettings()
        self.wiseg.loadSettings()
        self.wscripted.loadSettings()
        self.wcryo.loadSettings()
        self.wlogging.loadSettings()
        self.calcMax2Theta()
        self.calcDCTime()
        self.wmain.show()
        self.wlogging.show()
        self.wuserstatus.show()
        self.sigGUIStarted.emit()

    def loadSettings(self):
        s = Config.Settings
        motors = json.loads(s.value('Controller/Motors', '[]'))
        self.sigConnectMotors.emit(motors)
        self.motors = motors

    def saveSettings(self):
        s = Config.Settings
        s.setValue('Controller/Motors', json.dumps(self.motors))

    def stop(self):
        self.threadRabbitmq.quit()
        self.diffractometer.stop()
        self.monitor.abort()
        self.saveSettings()
        self.wmain.close()
        self.wlogging.close()
        self.wstatus.close()
        self.wuserstatus.close()
        self.wrelmove.close()
        self.walign.close()
        self.wscan.close()
        self.wlakeshore.close()
        self.wblower.close()
        self.wiseg.close()
        self.wcryo.close()
        self.wseq.close()
        self.wscripted.close()
        self.woptions.close()
        self.threadRabbitmq.wait()

    def showStatusWindow(self, checked):
        self.showWindowWithPassword(checked, self.wstatus, self.wmain.actionStatus)

    def showAlignWindow(self, checked):
        self.showWindowWithPassword(checked, self.walign, self.wmain.actionAlignment)

    def showWindowWithPassword(self, checked, window, action):
        checked = checked and GUtils.askPass(self.wmain)
        window.setVisible(checked)
        action.setChecked(checked)

    def addMotor(self, host, spec, motor):
        if host and spec and motor:
            motor = f'{host}->{spec}->{motor}'
            if motor not in self.motors:
                self.motors.append(motor)
                self.sigConnectMotor.emit(motor)
                self.saveSettings()

    def removeMotor(self, motor):
        self.motors.remove(motor)
        self.saveSettings()

    def calcMax2Theta(self):
        try:
            angle, d = self._calcMax2Theta()
        except ZeroDivisionError:
            angle, d = 0, 0
        self.sigMax2Theta.emit(angle, d)

    def _calcMax2Theta(self):
        pix = self.wmain.pixelxSpinBox.value() * 1e-3
        beamx = self.wmain.beamxSpinBox.value()
        r = (self.wmain.detectorxSpinBox.value() - (beamx - self.wmain.plvertSpinBox.value() / pix)) * pix
        s = self.wmain.zeroSpinBox.value() + self.wmain.pldistdSpinBox.value() + self.wmain.pldistfSpinBox.value()
        angle = math.atan(r / s)
        d = self.wavelength / 2 / math.sin(angle / 2)
        return math.degrees(angle), d

    def calcDCTime(self):
        t = self.wmain.nframesSpinBox.value() * self.wmain.exposureSpinBox.value() * self.wmain.nperiodsSpinBox.value()
        days, hours, minutes = auxygen.utils.calcTime(t)
        self.sigDCTime.emit(days, hours, minutes, t)

    def setWavelength(self, wavelength):
        self.wavelength = wavelength
        self.calcMax2Theta()

    def startExperiment(self, p):
        self.p = p
        if not self.rmqConnected:
            self.logger.error('RabbitMQ server is not connected, we cannot work like that.')
            return
        p.path = os.path.join(Config.UserDir, p.userSubDir)
        try:
            os.makedirs(p.path, exist_ok=True)
        except OSError as err:
            self.logger.error(f'Cannot create user directory {p.path}: {err}')
            return
        self.sigStartExperiment.emit(p)

    def setExperimentTime(self, p=None):
        if p:
            self.expTime = p.nframes * p.expPeriod * p.periods
        self.expStarted = time.time()
        self.expPaused = 0

    def calcExpTime(self):
        if self.expStarted:
            timeLeft = self.expTime - time.time() + self.expStarted
            days, hours, minutes = auxygen.utils.calcTime(timeLeft)
            msg = 'Time left'
        elif self.expPaused:
            timeStand = time.time() - self.expPaused
            days, hours, minutes = auxygen.utils.calcTime(timeStand)
            msg = 'Paused for'
        else:
            return
        if days:
            t = f'{msg}: {days:d}d {hours:d}h {minutes:d}m'
        elif hours:
            t = f'{msg}: {hours:d}h {minutes:d}m'
        else:
            t = f'{msg}: {minutes:d}m'
        self.sigExpTimeLeft.emit(t)

    def pausedExperiment(self):
        self.expStarted = 0
        self.expPaused = time.time()

    def setRmqConnected(self):
        self.rmqConnected = True

    def setRmqDisconnected(self):
        self.rmqConnected = False

    def setLakeshoreSensor(self, value):
        self.lakeshoreSensor = value

    def parseLakeshoreTemperature(self, sensor, value):
        if sensor == self.lakeshoreSensor:
            self.sigExperimentChunk.emit(chunks.PylatusLakeshore(value))

    def openPoni(self, filename):
        try:
            poni = integracio.Poni.open(filename)
        except integracio.PoniError:
            self.logger.error(f'The poni file {filename} cannot be open')
            return
        self.wmain.beamySpinBox.setValue(poni.beamy)
        self.wmain.beamxSpinBox.setValue(poni.beamx)
        self.wmain.zeroSpinBox.setValue(poni.direct_distance)
        self.wmain.pixelxSpinBox.setValue(poni.pixel1 * 1e6)
        self.wmain.pixelySpinBox.setValue(poni.pixel2 * 1e6)
        self.wmain.wlSpinBox.setValue(poni.wavelength)
        self.sigUpdateWavelength.emit(poni.wavelength)
