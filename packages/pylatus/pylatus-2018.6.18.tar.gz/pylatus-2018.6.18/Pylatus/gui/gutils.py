#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from ..controller.config import Config
from ..controller.utils import hash_pass


class GUtils:
    @staticmethod
    def askPass(parent):
        if not Config.RootHash:
            return True
        pas, ok = QtWidgets.QInputDialog.getText(parent, 'Password required',
                                                 'This operation requires a special permission:',
                                                 QtWidgets.QLineEdit.Password)
        return Config.RootHash == hash_pass(pas) if ok else False

    @staticmethod
    def delay(msec):
        dieTime = QtCore.QTime.currentTime().addMSecs(msec)
        while QtCore.QTime.currentTime() < dieTime:
            QtCore.QCoreApplication.processEvents()
