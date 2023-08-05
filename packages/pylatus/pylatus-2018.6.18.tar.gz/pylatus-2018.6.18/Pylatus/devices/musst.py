#!/usr/bin/python
# -*- coding: utf-8 -*-

import collections
from PyQt5 import QtCore
import aspic
from auxygen.devices import logger
from ..controller.config import Config


class Musst(QtCore.QObject):
    sigIdle = QtCore.pyqtSignal()
    sigData = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.queue = collections.deque()
        self.cmd = None
        self.con = None
        self.timeout1 = 0
        self.timeout2 = 0
        self.npts = 0
        self.step = 0
        self.data = ''
        self.dataCounter = 0
        self.callback = None
        self.oldCon = None
        self.logger = logger.Logger('MUSST')
        self.timerState = QtCore.QTimer()
        self.timerCmd = QtCore.QTimer()
        self.connectSignals()

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.timerState.setInterval(50)
        self.timerState.timeout.connect(lambda: self.runCommand('musst_comm("?STATE")', self.checkState))
        self.timerCmd.timeout.connect(self.checkQueue)

    def checkState(self, state):
        if state == 'IDLE':
            self.timerState.stop()
            self.queue.clear()
            self.callback = None
            if Config.MusstReadData:
                self.getData()
            else:
                self.sigIdle.emit()

    def setConfig(self):
        self.timeout1 = float(Config.MusstTimeout1) * 1e6 if Config.MusstTimeout1 else 0
        self.timeout2 = float(Config.MusstTimeout2) * 1e6 if Config.MusstTimeout2 else 0
        if self.oldCon != (Config.MusstSpec, Config.MusstFirmware):
            self.connectToSpec()

    def connectToSpec(self):
        if Config.MusstSpec and Config.MusstFirmware:
            try:
                host, port = Config.MusstSpec.split(':')
            except (IndexError, ValueError):
                self.logger.error('MUSST address is incorrect')
                return
            self.oldCon = Config.MusstSpec, Config.MusstFirmware
            address = host, port
            self.init_musst_commands = (
                # stop current program
                'musst_comm("ABORT")',
                'musst_comm("BTRIG 0")',
                'musst_comm("CLEAR")',
                'musst_comm("HSIZE 0")',
                # set buffer size
                'musst_comm("ESIZE 500000 1")',
                # upload the program
                f'musst_upload_program("musst", "{Config.MusstFirmware}", 1)',
            )
            self.queue.clear()
            self.callback = None
            self.con = aspic.manager.qonnect(address)
            self.con.sigConnectedToSpec.connect(self.reset)
            self.con.sigError.connect(self.logger.error)
            if self.con.connected:
                QtCore.QMetaObject.invokeMethod(self, 'reset', QtCore.Qt.QueuedConnection)
            self.cmd = aspic.Qommand(self.con)
            self.cmd.sigFinished.connect(self.commandFinished)
            self.cmd.sigError.connect(self.logger.error)
            self.timerCmd.start(10)
        else:
            self.timerCmd.stop()
            self.callback = None
            self.cmd = None
            self.con = None

    def commandFinished(self, response):
        if self.callback:
            callback = self.callback
            self.callback = None
            callback(response)

    @QtCore.pyqtSlot(name='reset')
    def reset(self):
        self.logger.info('Musst is connected')
        for musst_command in self.init_musst_commands:
            self.runCommand(musst_command)

    def checkQueue(self):
        if not self.callback and self.queue:
            cmd, self.callback = self.queue.popleft()
            self.cmd.run(cmd)

    def setVar(self, var, value):
        self.runCommand(f'musst_comm("VAR {var} {int(value):d}")')

    def runScan(self, step, nframes, exptime, mod1, mod2):
        self.step = step or 1
        params = {
            'STARTDELAY': self.timeout2,
            'NPOINTS': nframes,
            'CTIME': exptime * 1e6,
            'INITDELAY': self.timeout1,
            'NPOINTS2': mod1,
            'NPOINTS2A': mod2,
        }
        for var in params:
            self.setVar(var, params[var])
        self.runCommand('musst_comm("RUN SCAN")')
        self.timerState.start()

    def abort(self):
        self.runCommand('musst_comm("ABORT")', lambda _: self.logger.warn(f'Musst has been stopped! Message: {_}'))
        self.closeShutter()

    def openShutter(self):
        self.runCommand('musst_comm("RUN SHUTTER_OPEN")', lambda _: self.logger.info(f'Shutter is open: {_}'))

    def closeShutter(self):
        self.runCommand('musst_comm("RUN SHUTTER_CLOSE")', lambda _: self.logger.info(f'Shutter is closed: {_}'))

    def trigChannel(self, chan, trtime=0.1):
        self.runCommand(f'trigch {chan:d} {trtime:.2f}',
                        lambda _: self.logger.info(f'Musst triggers channel {chan:d} for {trtime:.2f} seconds: {_}'))

    def runCommand(self, command, callback=None):
        if self.isConnected():
            self.queue.append((command, callback))

    def isConnected(self):
        return self.cmd and self.con and self.con.connected

    def getData(self):
        self.runCommand('musst_comm("?VAR NPTS")', lambda npts: setattr(self, 'npts', npts))
        self.runCommand('musst_comm("?VAR DIMLINE")', self.dimlineReceived)

    def dimlineReceived(self, dimline):
        if not dimline or not self.npts:
            return
        self.data = ''
        self.dataCounter = 0
        # I do not know what happens here. This code has been copied from the SPEC macros testmusst_*.
        # Ask Roberto Homes
        maxnl = 255 // dimline
        for nl in range(0, self.npts, maxnl):
            nn = self.npts - nl
            if nn > maxnl:
                nn = maxnl
            self.runCommand(f'musst_comm("?EDAT {nn * dimline:d} 0 {nl * dimline:d}")', self.appendData)
            self.dataCounter += 1

    def appendData(self, data):
        self.data += data
        self.dataCounter -= 1
        if not self.dataCounter:
            self.npts = 0
            self.processData()

    def processData(self):
        # there is no guarantee that the data come in the right format: '0xff\n0xff\n...'
        # thus we have to do the workaround with the splitting
        numbers = [int(n, 16) for n in self.data.split('0x')[1:]]

        # now the data is a list of numbers in the next format:
        # [time, encoder_position, monitor_value, | time, encoder_position, monitor_value, | ...]
        # at the first point the time and monitor_value are 0, thus we do not need it
        # we do not need absolute encoder values but we need the differences between neighbours
        raw_encoders = numbers[1::3]
        encoders = []
        for i, enc in enumerate(raw_encoders[:-1]):
            diff = enc - raw_encoders[i+1]
            # if motor doesn't move there are some distortions in the encoder values
            if 0 <= abs(diff) <= 10:
                diff = abs(diff)
            # if difference is less than zero, then we have an overflow
            elif diff < 0:
                diff += 0x100000000
            encoders.append(diff / self.step)
        data = [(time, enc, mon) for time, enc, mon in zip(numbers[3::3], encoders, numbers[5::3])]
        self.sigData.emit(data)
        self.sigIdle.emit()
