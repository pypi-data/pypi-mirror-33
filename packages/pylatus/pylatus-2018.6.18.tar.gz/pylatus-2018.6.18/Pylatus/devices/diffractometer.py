#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import aspic
import auxygen
from ..controller import utils
from ..gui.gutils import GUtils
from . import scanman, musst, pilatus
from ..controller.config import Config


class Diffractometer(QtCore.QObject):
    sigMotorMoved = QtCore.pyqtSignal(str, float)
    sigWavelength = QtCore.pyqtSignal(float)
    sigEnergy = QtCore.pyqtSignal(float)
    sigExperimentFinished = QtCore.pyqtSignal()
    sigExperimentStarted = QtCore.pyqtSignal()
    sigExperimentPaused = QtCore.pyqtSignal()
    sigExperimentResumed = QtCore.pyqtSignal()
    sigAllMotorsStopped = QtCore.pyqtSignal()
    sigMotorStepSize = QtCore.pyqtSignal(str, float)
    sigExperimentParameters = QtCore.pyqtSignal(object)
    sigScanFinished = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.motorsList = []
        self.fixedMotors = []
        self.motors = {}
        self.p = None
        self.logger = auxygen.devices.logger.Logger('Pylatus')
        self.running = False
        self.phiMaxVelocity = 10
        self.prphiMaxVelocity = 10
        self.omegaMaxVelocity = 10
        self.maxVelocity = 10
        self.minPlvert = -20
        self.energy = 0
        self.wavelength = 0
        self.mono = None
        self.makePause = False
        self.scanType = 'Omega'
        self.paused = False
        self.oldFilter = None
        self.shutterMotor = ''
        self.setConfig()
        self.createDevices()

    def setMakePause(self, checked):
        self.makePause = checked

    def connectSignals(self):
        self.pilatus.sigScanStepReady.connect(self.scanman.moveMotor)
        self.scanman.sigError.connect(self.logger.error)
        self.scanman.sigMoveMotor.connect(self.moveMotorAndWait)
        self.scanman.sigScanFinished.connect(self.stopScan)
        self.scanman.sigShot.connect(self.pilatus.scanShot)
        self.pilatus.sigExperimentFinished.connect(self.experimentFinishedByPilatus)
        self.sigEnergy.connect(self.pilatus.setEnergy)
        self.musst.sigIdle.connect(self.musstIsIdle)
        self.sigExperimentStarted.connect(self.pilatus.setMeasuring)
        self.sigScanFinished.connect(self.pilatus.setFinished)
        self.sigExperimentFinished.connect(self.pilatus.setFinished)
        self.scanman.sigScanStarted.connect(self.pilatus.setMeasuring)

    def createDevices(self):
        self.musst = musst.Musst()
        self.pilatus = pilatus.Pilatus()
        self.scanman = scanman.ScanManager()

    def pauseExperiment(self):
        if self.makePause and not self.paused:
            self.paused = True
            self.logger.error('!There is no beam! We abort the current data collection and wait until the beam gets '
                              'back')
            self.stopAllMotors()
            self.musst.abort()
            self.pilatus.abort()
            self.sigExperimentPaused.emit()

    def resumeExperiment(self):
        if self.makePause and self.paused:
            self.paused = False
            self.logger.info('The beam has come back. The last data collection is being restarted. '
                             'It is recommended to perform the general scan after')
            self.sigExperimentResumed.emit()
            self.period -= 1
            self.startNextPeriod()

    def experimentFinishedByPilatus(self):
        if not self.musst.isConnected():
            self.musstIsIdle()

    def musstIsIdle(self):
        if self.scanman.running:
            return
        self.closeShutter()
        if self.running and not self.paused:
            self.startNextPeriod()

    def startNextPeriod(self):
        if not self.p:
            return
        self.setCurrentPeriod()
        self.runCurrentScan()
        if self.stopped:
            self.stopExperiment()

    def setMotors(self, motors):
        self.motorsList = motors

    def connectMotors(self):
        for motor in self.motorsList:
            self.connectGUIMotor(motor)

    def updateMotorViews(self):
        for m in self.motors:
            motor = self.motors[m]
            self.sigMotorMoved.emit(motor.name(), motor.position())

    def connectGUIMotor(self, motor):
        host, session, name = motor.split('->')
        self.connectMotor(host, session, name)

    def connectMotor(self, host, session, name):
        if name in self.motors:
            del self.motors[name]
        address = host, session
        motor = aspic.QMotor(address, name)
        motor.sigConnected.connect(lambda _: self.logger.info(f'Motor {_} has been connected'))
        motor.sigError.connect(self.logger.error)
        motor.sigLimitHit.connect(lambda _: self.logger.error(f'Motor {_} has hit the limit'))
        motor.sigNewPosition.connect(self.updateMotorPosition)
        motor.sigDisconnected.connect(lambda _: self.logger.warn(f'Motor {_} has been disconnected'))
        motor.sigStepSize.connect(self.sigMotorStepSize.emit)
        self.motors[name] = motor

    def updateMotorPosition(self, name, position):
        if name == Config.Mono:
            self.mono = position
            self.setWavelength()
        self.sigMotorMoved.emit(name, position)

    def setWavelength(self):
        if self.mono is None:
            return
        self.wavelength, self.energy = utils.wavelength_energy(self.mono)
        self.sigWavelength.emit(self.wavelength)
        self.sigEnergy.emit(self.energy)

    def setConfig(self):
        self.beamstopOn = float(Config.BeamstopOn)
        self.beamstopOff = float(Config.BeamstopOff)
        self.shutterClosed = float(Config.ShutterClosed)
        self.shutterOpen = float(Config.ShutterOpen)
        self.shutterCollimated = float(Config.ShutterCollimated)
        if self.shutterMotor != Config.ShutterMotor:
            self.shutterMotor = Config.ShutterMotor
        self.setWavelength()

    @auxygen.utils.split_motor_name
    def deleteMotor(self, name):
        if name in self.motors:
            del self.motors[name]

    def getMotor(self, name):
        if not name:
            return
        if isinstance(name, aspic.QMotor):
            return name
        motor = self.motors.get(name)
        if not motor:
            return
        if motor.isConnected() and not motor.isUnusable():
            return motor
        self.logger.warning(f'The motor {name} either is not connected or unusable. Skipped.')

    def getMotors(self, names):
        for name in names:
            yield self.getMotor(name)

    def setScanMotor(self, name):
        self.scanMotor = self.getMotor(name)
        if self.scanMotor:
            self.scanMotor.setDesiredPosition(self.p.startAngle)
        else:
            self.logger.error(f'Motor {name} is not connected. Skip it.')

    def preparePhiScan(self):
        self.setScanMotor(Config.Phi)
        if self.stopped or self.paused:
            return
        self.maxVelocity = self.phiMaxVelocity
        self.p.oscAxis = 'PHI'
        self.p.omega = self.p.omegaphi
        self.p.omegastep = 0
        self.p.phi = self.p.startAngle
        self.p.phistep = self.p.step
        motors = Config.Omega, Config.Kappa
        positions = self.p.omegaphi, self.p.kappa
        self.setFixedMotors(motors, positions)

    def prepareOmegaScan(self):
        self.setScanMotor(Config.Omega)
        if self.stopped or self.paused:
            return
        self.maxVelocity = self.omegaMaxVelocity
        self.p.oscAxis = 'OMEGA'
        self.p.phi = self.p.omegaphi
        self.p.phistep = 0
        self.p.omega = self.p.startAngle
        self.p.omegastep = self.p.step
        motors = Config.Phi, Config.Kappa
        positions = self.p.omegaphi, self.p.kappa
        self.setFixedMotors(motors, positions)

    def preparePrphiScan(self):
        self.setScanMotor(Config.Prphi)
        if self.stopped or self.paused:
            return
        self.maxVelocity = self.prphiMaxVelocity
        self.p.oscAxis = 'OMEGA'
        self.p.omegaphi = 0
        self.p.kappa = 0
        self.p.phi = self.p.omegaphi
        self.p.phistep = 0
        self.p.omega = self.p.startAngle
        self.p.omegastep = self.p.step

    def getAllMovingMotors(self):
        motors = []
        for name in self.motors:
            motor = self.motors[name]
            if motor.isConnected() and motor.isMoving():
                motors.append(motor)
        return motors

    def waitForMotorsMovement(self, motors=None):
        if not motors:
            motors = self.getAllMovingMotors()
        while motors:
            for motor in motors[:]:
                if self.stopped:
                    return
                if self.hasMotorReachedPosition(motor):
                    motors.remove(motor)
            GUtils.delay(100)

    def hasMotorReachedPosition(self, motor):
        if motor is None:
            return True
        if motor.isOnLimit():
            self.logger.error(f'Motor {motor.name()} is at the limit switch! Continue at the current position!')
            self.sigMotorMoved.emit(motor.name(), motor.position())
            return True
        if motor.isReady() and abs(motor.position() - motor.desiredPosition()) <= 1e-2:
            self.sigMotorMoved.emit(motor.name(), motor.position())
            return True
        motor.move(motor.desiredPosition())
        return False

    def waitForMotorsMovementFromScript(self):
        if self.running:
            return
        self.running = True
        self.waitForMotorsMovement()
        self.running = False
        self.sigAllMotorsStopped.emit()

    def getSlewRateMotors(self):
        motors = Config.Prphi, Config.Phi, Config.Omega
        maxVel = self.prphiMaxVelocity, self.phiMaxVelocity, self.omegaMaxVelocity
        return motors, maxVel

    def setMaxVelocity(self):
        for motorName, maxVelocity in zip(*self.getSlewRateMotors()):
            motor = self.getMotor(motorName)
            if not motor or not motor.isConnected() or motor.isUnusable():
                continue
            slew_rate = motor.stepSize() * maxVelocity
            if slew_rate == motor.slewRate():
                continue
            motor.setSlewRate(slew_rate)
            self.logger.info(f'slew_rate for motor {motor.name()} is set to {slew_rate}')

    def reconnectMotors(self):
        for motorName in self.motors:
            self.motors[motorName] = self.reconnectMotor(self.motors[motorName])
        self.musst.reset()
        self.connectMonitor()

    def stopAllMotors(self):
        self.logger.warn('Stopping all moving motors!')
        for name in self.motors:
            self.stopMotor(name)

    def stopMotor(self, name):
        motor = self.getMotor(name)
        if motor and motor.isMoving():
            self.logger.warn(f'Stop motor {name}')
            motor.stop()

    def startExperiment(self, p):
        if self.running:
            self.logger.error('Stop the current measurements first!')
            return
        self.running = True
        self.p = p
        self.period = 0
        self.sigExperimentStarted.emit()
        self.initFixedMotors()
        self.setCurrentPeriod()
        self.runCurrentScan()
        if self.paused:
            self.sigExperimentPaused.emit()
        if self.stopped:
            self.stopExperiment()

    def runCurrentScan(self):
        if self.stopped or self.paused:
            return
        self.setCurrentScan()
        self.moveMotorsToStartPosition()
        self.setScanMotorVelocity()
        self.prepareDetector()
        self.fire()

    def setCurrentScan(self):
        if self.stopped or self.paused:
            return
        if self.scanType == 'Phi':
            self.preparePhiScan()
        elif self.scanType == 'Omega':
            self.prepareOmegaScan()
        elif self.scanType == 'Prphi':
            self.preparePrphiScan()
        else:
            self.logger.error('Something wrong with the scan definition. Stopping now.')
            self.running = False
            return
        self.sigExperimentParameters.emit(self.p)

    def setCurrentPeriod(self):
        if self.paused:
            return
        if self.running and self.period < self.p.periods:
            self.period += 1
            self.p.period = self.period
            self.logger.info(f'Starting period {self.period:d} from {self.p.periods:d}.')
        else:
            self.running = False

    def stopExperiment(self):
        self.running = False
        self.setMaxVelocity()
        self.sigExperimentFinished.emit()
        self.logger.info('The data collection has been finished.')

    def setScanMotorVelocity(self):
        if self.stopped or self.paused or not self.scanMotor:
            return
        step_size = self.scanMotor.stepSize()
        velocity = step_size * self.p.step / self.p.expPeriod
        if velocity > step_size * self.maxVelocity:
            self.logger.error(f'Speed for {self.scanMotor.name()} is to high! Change exposure period. Stopping now.')
            self.running = False
            return
        self.logger.info(f'slew_rate for motor {self.scanMotor.name()} is set to {velocity}')
        self.scanMotor.setSlewRate(velocity)

    def prepareDetector(self):
        if self.stopped or self.paused:
            return
        if not self.pilatus.isConnected():
            self.logger.error('Detector is not connected. Check the camserver.')
            self.running = False
            return
        if self.p.nop:
            self.p.cbfName = f'{self.p.cbfBaseName}.cbf'
        else:
            self.p.cbfName = f'{self.p.cbfBaseName}_{self.period:04d}p.cbf'
        self.p.cbf = self.p.cbfName[:-4]
        ms = Config.Plvert, Config.Pldistd, Config.Pldistf
        v, dd, df = list(m.position() if m else 0 for m in self.getMotors(ms))
        beamy = self.p.beamY + v / self.p.pixelX * 1e3  # TODO: change to pixelY
        dist = (self.p.zeroDistance + df + dd) * 1e-3
        detSettings = {
            'Oscillation_axis': self.p.oscAxis,
            'Phi': self.p.phi,
            'Phi_increment': self.p.phistep,
            'Kappa': self.p.kappa,
            'Detector_distance': dist,
            'Detector_Voffset': v * 1e-3,
            'Wavelength': self.wavelength,
            'Beam_y': beamy,
            'Beam_x': self.p.beamX,
            'Start_angle': self.p.startAngle,
            'Angle_increment': self.p.step,
        }
        self.pilatus.initExperiment(self.p.expPeriod, self.p.nframes, detSettings)

    def fire(self):
        if self.stopped or self.paused:
            return
        if self.p.step and self.scanMotor:
            finalPosition = self.scanMotor.position() + self.p.step * self.p.nframes
            while self.scanMotor.state() == self.scanMotor.StateReady:
                GUtils.delay(100)
                if self.stopped:
                    return
                self.scanMotor.move(finalPosition)
                self.logger.info(f'Motor {self.scanMotor.name()} has been sent to {finalPosition:.5f}')
        self.musst.runScan(self.p.step, self.p.nframes, self.p.expPeriod, self.p.mod, self.p.mod2)
        self.openShutter()
        if self.musst.isConnected():
            self.pilatus.exposure(self.p.cbfName)
        else:
            self.pilatus.shot(self.p.cbfName)

    def moveMotorsToStartPosition(self):
        self.logger.info('Moving motors to the start positions')
        self.setMaxVelocity()
        if self.scanMotor:
            self.fixedMotors.append(self.scanMotor)
        for motor in self.fixedMotors:
            motor.move(motor.desiredPosition())
        self.waitForMotorsMovement(self.fixedMotors)

    def setFixedMotors(self, motors, positions):
        for m, p in zip(motors, positions):
            motor = self.getMotor(m)
            if motor:
                motor.setDesiredPosition(p)
                self.fixedMotors.append(motor)

    def initFixedMotors(self):
        self.fixedMotors = []
        motors = Config.Pldistd, Config.Pldistf, Config.Plvert, Config.Plrot, Config.Bstop
        positions = (self.p.pldistd, self.p.pldistf, self.p.plvert, self.p.plrot,
                     float(Config.BeamstopOn))
        self.setFixedMotors(motors, positions)

    def setPrphiMaxVelocity(self, value):
        self.prphiMaxVelocity = value

    def setPhiMaxVelocity(self, value):
        self.phiMaxVelocity = value

    def setPhiScan(self):
        self.scanType = 'Phi'

    def setOmegaScan(self):
        self.scanType = 'Omega'

    def setPrphiScan(self):
        self.scanType = 'Prphi'

    def setOmegaMaxVelocity(self, value):
        self.omegaMaxVelocity = value

    def abortCurrentExperiment(self):
        self.paused = False
        self.stopAllMotors()
        self.pilatus.abort()
        self.musst.abort()

    def abortExperiment(self):
        if self.stopped:
            return
        self.abortCurrentExperiment()
        self.stopExperiment()

    def moveShutterMotor(self, position: float):
        if not self.shutterMotor:
            return
        shutter = self.getMotor(self.shutterMotor)
        if not shutter:
            return
        shutter.move(position)
        self.waitForMotorsMovement([shutter])

    def openShutter(self):
        self.musst.openShutter()
        self.moveShutterMotor(self.shutterOpen)

    def closeShutter(self):
        self.musst.closeShutter()
        self.moveShutterMotor(self.shutterClosed)

    def start(self):
        self.connectSpec()
        self.pilatus.connectDetector()

    def connectSpec(self):
        self.connectMotors()
        self.musst.connectToSpec()

    def stop(self):
        self.abortExperiment()
        self.abortScan()
        self.running = False
        self.pilatus.stop()

    def moveMotor(self, motor, position, maxVelocity=True):
        if maxVelocity:
            self.setMaxVelocity()
        motor = self.getMotor(motor)
        if motor:
            motor.move(position)
            self.logger.info(f'Move motor {motor.name()} from {motor.position():.5f} to {position:.5f}')
        return motor

    def moveMotorAndWait(self, motor, position):
        motor = self.moveMotor(motor, position)
        if not motor:
            return
        old, self.running = self.running, True
        self.waitForMotorsMovement([motor])
        self.running = old
        self.scanman.motorArrived()

    def moveMotorRelative(self, motorName, position, maxVelocity=True):
        if maxVelocity:
            self.setMaxVelocity()
        motor = self.getMotor(motorName)
        if motor:
            self.logger.info(f'Move {motor.name()} from {motor.position():.5f} to {motor.position() + position:.5f}')
            motor.moveRelative(position)

    def runScan(self, params):
        if self.running:
            self.logger.error('Something is running, stop it before the scan!')
            return
        if params.auto:
            params.axis = Config.ScanAxis
            params.expPeriod = float(Config.ScanTime)
            params.nfilter = int(Config.ScanFilter)
        axis, bstop, fltr = self.getMotors((params.axis, Config.Bstop, Config.Filter))
        if not axis:
            self.logger.error(f'The scanning axis {params.axis} is not connected! Stopping')
            return
        if params.auto and not bstop:
            self.logger.error(f'The beamstop motor {Config.Bstop} is not connected! Stopping')
            return
        if params.auto and not fltr:
            self.logger.error(f'The filter motor {Config.Filter} is not connected! Stopping')
            return
        self.running = True
        if fltr:
            self.oldFilter = fltr.position()
            self.moveMotor(fltr, params.nfilter)
            self.waitForMotorsMovement([fltr])
        params.backup = axis.position()
        if self.stopped:
            return
        if params.auto:
            self.moveMotor(bstop, self.beamstopOff)
            self.waitForMotorsMovement([bstop])
            if self.stopped:
                return
        self.pilatus.initExperiment(params.expPeriod, 1)
        self.openShutter()
        self.scanman.run(params)

    def stopScan(self, auto):
        if self.stopped:
            return
        self.pilatus.scanShot()
        self.closeShutter()
        if auto:
            self.moveMotor(Config.Bstop, self.beamstopOn)
            self.waitForMotorsMovement()
            if self.oldFilter is not None:
                self.moveMotor(Config.Filter, self.oldFilter)
                self.oldFilter = None
        self.waitForMotorsMovement()
        self.running = False
        self.scanman.running = False
        self.sigScanFinished.emit(auto)

    def abortScan(self):
        if self.running:
            self.stopAllMotors()
            self.scanman.abortScan()

    def updateWavelength(self, value):
        mono = self.getMotor(Config.Mono)
        if mono:
            mono.setOffset(utils.angle(value) - mono.dialPosition())

    def setMinPlvert(self, value):
        self.minPlvert = value

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, running):
        self._running = running

    @property
    def stopped(self):
        return not self._running

    @stopped.setter
    def stopped(self, stopped):
        self._running = not stopped
