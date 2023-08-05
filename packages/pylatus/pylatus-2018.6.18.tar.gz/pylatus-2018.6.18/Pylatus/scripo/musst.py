#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import auxygen


class Musst(QtCore.QObject):
    _sigOpenShutter = QtCore.pyqtSignal()
    __sigOpenShutterFromSeq = QtCore.pyqtSignal(dict, object)
    _sigCloseShutter = QtCore.pyqtSignal()
    __sigCloseShutterFromSeq = QtCore.pyqtSignal(dict, object)
    _sigTrigChannel = QtCore.pyqtSignal(int, float)
    __sigTrigChannelFromSeq = QtCore.pyqtSignal(dict, object)
    _sigCreateSeqAction = QtCore.pyqtSignal(dict, object, bool)
    specialWords = {'musst.openShutter', 'musst.closeShutter', 'musst.trigChannel'}

    def __init__(self):
        super().__init__()
        self.__sigTrigChannelFromSeq.connect(self.__trigChannelFromSeq)
        self.__sigCloseShutterFromSeq.connect(self.__closeShutterFromSeq)
        self.__sigOpenShutterFromSeq.connect(self.__openShutterFromSeq)

    @auxygen.scripo.utils.customable
    def openShutter(self, **kwargs):
        self._sigCreateSeqAction.emit(
            {'Open shutter': 'musstOpenShutter=1'},
            self.__sigOpenShutterFromSeq,
            kwargs.get('now', False)
        )

    @auxygen.scripo.utils.customable
    def closeShutter(self, **kwargs):
        self._sigCreateSeqAction.emit(
            {'Close shutter': 'musstCloseShutter=1'},
            self.__sigCloseShutterFromSeq,
            kwargs.get('now', False)
        )

    @auxygen.scripo.utils.customable
    def trigChannel(self, channel, trigtime=0.1, **kwargs):
        if not 8 <= channel <= 15:
            raise ValueError('The MUSST channel musst be between 8 and 15')
        elif trigtime < 0.01:
            raise ValueError('The MUSST triggering time is too low')
        d = {
            f'Trigger MUSST channel {channel:d} for {trigtime:.2f} seconds':
                f'trigChannel={channel:d};trigtime={trigtime:.2f}',
        }
        self._sigCreateSeqAction.emit(d, self.__sigTrigChannelFromSeq, kwargs.get('now', False))

    def __trigChannelFromSeq(self, dct, signal):
        if signal:
            channel, trigtime = list(dct.values())[0].split(';')
            channel = int(channel.split('=')[1])
            trigtime = float(trigtime.split('=')[1])
            self._sigTrigChannel.emit(channel, trigtime)
            signal.emit()

    def __closeShutterFromSeq(self, dct, signal):
        if dct and signal:
            self._sigCloseShutter.emit()
            signal.emit()

    def __openShutterFromSeq(self, dct, signal):
        if dct and signal:
            self._sigOpenShutter.emit()
            signal.emit()
