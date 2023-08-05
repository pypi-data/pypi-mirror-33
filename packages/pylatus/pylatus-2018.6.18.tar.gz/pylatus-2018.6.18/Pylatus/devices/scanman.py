#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid
import math
import auxygen
from PyQt5 import QtCore
import numpy as np
from scipy import optimize
from ..controller.config import Config


class Gauss:
    c1 = 4 * math.log(2)
    c2 = math.sqrt(c1 / math.pi)

    def __call__(self, x, xc, w, a, y0):
        return y0 + a * self.c2 / w * np.exp(-self.c1 * ((x - xc) / w) ** 2)


class ScanManager(QtCore.QObject):
    sigPoint = QtCore.pyqtSignal(np.ndarray, np.ndarray)
    sigError = QtCore.pyqtSignal(str)
    sigMoveMotor = QtCore.pyqtSignal(str, float)
    sigScanFinished = QtCore.pyqtSignal(bool)
    sigShot = QtCore.pyqtSignal(str)
    sigFit = QtCore.pyqtSignal(np.ndarray, np.ndarray, float)
    sigScanStarted = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.logger = auxygen.devices.logger.Logger('ScanMan')
        self.gauss = Gauss()
        self.position = 0
        self.names = self.images = []
        self.indices = {}
        self.running = False
        self.imageName = ''

    def addValue(self, name, value):
        if not self.running:
            return
        self.logger.info(f'Scan value {value} for {name}')
        if self.imageName == name:
            QtCore.QTimer.singleShot(0, self.moveMotor)
        try:
            index = self.indices[name]
        except KeyError:
            return
        self.scanY[index] = value
        self.sigPoint.emit(self.scanX, self.scanY)
        self.names.remove(name)
        self.checkNames()

    def checkNames(self):
        if self.names:
            return
        if self.params.auto:
            self.fit()
        self.running = False
        self.imageName = ''
        self.names = self.images = []
        self.indices = {}
        self.sigScanFinished.emit(self.params.auto)
        self.logger.info('Scan has been finished')

    def fit(self):
        x, y = self.scanX, self.scanY
        xc = (x * y).sum() / y.sum()
        w = np.sqrt(np.abs((y * (x - xc) ** 2).sum() / y.sum()))
        a = y.max()
        y0 = 0
        try:
            # noinspection PyTypeChecker
            res, cov = optimize.curve_fit(self.gauss, self.scanX, self.scanY, (xc, w, a, y0))
        except RuntimeError as err:
            self.sigError.emit(f'Fit could not be done: {str(err)}')
            self.sigMoveMotor.emit(self.params.axis, self.params.backup)
            return
        fitfunc = self.gauss(x, *res)
        xc = float(res[0])
        self.sigFit.emit(self.scanX, fitfunc, xc)
        if xc > self.params.stop:
            self.sigError.emit(f'The Gauss maximum is too right at {xc:.5f}, we move to {self.params.stop:.5f}')
            xc = self.params.stop
        elif xc < self.params.start:
            self.sigError.emit(f'The Gauss maximum is too left at {xc:.5f}, we move to {self.params.start:.5f}')
            xc = self.params.start
        else:
            self.sigError.emit(f'The Gauss maximum is found to be at {xc:.5f}')
        self.sigMoveMotor.emit(self.params.axis, xc)

    def run(self, params):
        if self.running:
            self.sigError.emit('Scan is running already')
            self.sigScanFinished.emit(self.params.auto)
            return
        self.params = params
        if self.params.auto:
            range_ = float(Config.ScanRange)
            self.params.start = self.params.backup - range_
            self.params.stop = self.params.backup + range_
            self.params.step = int(Config.ScanStep)
        self.scanX = np.linspace(self.params.start, self.params.stop, self.params.step)
        if not self.scanX.size:
            self.sigError.emit('Scan error: there are not points to scan, check the signs')
            self.sigScanFinished.emit(self.params.auto)
            return
        self.scanY = np.zeros_like(self.scanX)
        self.points = [float(i) for i in self.scanX]
        self.images = [f'{uuid.uuid4()}.cbf' for _ in range(len(self.points))]
        self.names = self.images[:]
        self.indices = {name: index for index, name in enumerate(self.images)}
        self.params.images = set(self.images)
        self.params.nframes = len(self.params.images)
        self.running = True
        self.sigScanStarted.emit(self.params)
        QtCore.QTimer.singleShot(0, self.moveMotor)

    def moveMotor(self):
        if self.running and self.images:
            self.position = self.points.pop(0)
            self.imageName = self.images.pop(0)
            self.sigMoveMotor.emit(self.params.axis, self.position)

    def motorArrived(self):
        if self.running:
            self.sigShot.emit(self.imageName)

    def abortScan(self):
        if self.running:
            self.running = False
            if self.params.auto:
                self.sigMoveMotor.emit(self.params.axis, self.params.backup)
            self.sigScanFinished.emit(self.params.auto)
