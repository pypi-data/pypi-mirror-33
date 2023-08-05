#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import aspic
from ..controller.config import Config


class Monitor(QtCore.QObject):
    sigConnected = QtCore.pyqtSignal(str)
    sigValue = QtCore.pyqtSignal(int)
    sigError = QtCore.pyqtSignal(str)
    sigBeamOff = QtCore.pyqtSignal()
    sigBeamOn = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ready = False
        self.running = False
        self.started = False
        self.address = None
        self.sec = None
        self.mon = None
        self.userTime = 0
        self.countTime = 0
        self.setConfig()

    def run(self, countTime):
        self.userTime = countTime
        if self.timescan:
            self.countTime = self.timescan
        elif self.measTime:
            self.countTime = self.measTime
        else:
            self.countTime = countTime
        self.running = True
        self.count()

    def abort(self):
        self.running = False

    def start(self):
        self.started = True
        self.connectToSpec()

    def setConfig(self):
        self.mult = float(Config.MonitorMult) if Config.MonitorMult else 1
        self.timescan = float(Config.Timescan) if Config.Timescan else 0
        self.secName = Config.MonSecName
        self.measTime = float(Config.MonMeasTime) if Config.MonMeasTime else 0
        self.noBeamCounts = int(Config.NoBeamCounts) if Config.NoBeamCounts else 0
        if self.timescan and self.measTime:
            self.sigError.emit('Monitor: both measuring time and timescan are set, which is wrong. Set one of them'
                               'to zero. If not, we prefer timescan.')
            self.measTime = 0
        if self.address != Config.MonitorSpec:
            self.address = Config.MonitorSpec
            if self.started:
                self.connectToSpec()

    def connectToSpec(self):
        if self.address and self.secName:
            try:
                host, spec, counter = Config.MonitorSpec.split(':')
            except IndexError:
                self.sigError.emit(f'Monitor address {Config.MonitorSpec} could not be parsed. It should be in the '
                                   f'following form: spec_host:spec_name:counter.')
            else:
                self.sec = aspic.Qounter((host, spec), self.secName)
                self.sec.sigValueChanged.connect(self.monChanged)
                self.mon = aspic.Qounter((host, spec), counter)
                self.mon.sigValueChanged.connect(self.monChanged)
                self.mon.sigConnected.connect(self.sigConnected.emit)
                self.mon.sigError.connect(self.sigError.emit)
                return
        self.running = False
        self.sec = None
        self.mon = None

    def monChanged(self, name, counts):
        if self.running and self.secName:
            if name == self.secName and counts >= self.countTime:
                self.ready = True
            elif name == self.mon.name() and self.ready:
                self.ready = False
                counts *= self.mult
                if counts / self.countTime <= self.noBeamCounts:
                    self.sigBeamOff.emit()
                    counts = 0
                else:
                    self.sigBeamOn.emit()
                    counts = int(counts / self.countTime * self.userTime)
                self.sigValue.emit(counts)
                self.count()

    def connected(self):
        return self.sec and self.sec.isConnected() and self.mon and self.mon.isConnected()

    def count(self):
        if not self.timescan and self.running and self.connected():
            self.mon.count(self.countTime)
