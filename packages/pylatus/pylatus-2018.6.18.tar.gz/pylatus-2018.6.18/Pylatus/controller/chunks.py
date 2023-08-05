#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class PylatusChunkObject:
    kind = 0
    sent = False

    def __init__(self):
        self.timestamp = time.time()
        self._d = {'Timestamp': int(self.timestamp * 1e9), 'Kind': self.kind}

    def _json(self):
        pass

    def json(self):
        self._json()
        return self._d


class PylatusExperimentFinished(PylatusChunkObject):
    kind = 1


class PylatusExperimentParams(PylatusChunkObject):
    kind = 2
    beamX = 0
    beamY = 0
    cbf = ''
    cbfBaseName = ''
    cbfName = ''
    expPeriod = 0
    kappa = 0
    mod = 0
    mod2 = 0
    nframes = 0
    nop = False
    omegaphi = 0
    oscAxis = ''
    path = ''
    period = 0
    periods = 0
    pixelX = 0
    pldistd = 0
    pldistf = 0
    plrot = 0
    plvert = 0
    startAngle = 0
    step = 0
    userSubDir = ''
    zeroDistance = 0
    omega = 0
    omegastep = 0
    phi = 0
    phistep = 0

    def _json(self):
        self._d.update({
            'Omega': self.omega,
            'OscAxis': self.oscAxis,
            'Step': self.step,
            'Path': self.path,
            'NFrames': self.nframes,
        })


class PylatusExperimentValue(PylatusChunkObject):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def _json(self):
        self._d.update({'Value': self.value})

    def key(self):
        return self.__class__.__name__[7:]

    def __repr__(self):
        return f'{self.timestamp}: {self.value}'


class PylatusFlux(PylatusExperimentValue):
    kind = 3


class PylatusTemperature(PylatusExperimentValue):
    kind = 4


class PylatusBlower(PylatusExperimentValue):
    kind = 5


class PylatusLakeshore(PylatusExperimentValue):
    kind = 6


class PylatusScanParams(PylatusExperimentParams):
    kind = 7
    auto = True
    axis = ''
    start = 0
    stop = 0
    nfilter = 0
    backup = 0
    images = set()
