#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
from .controller.ctrl import Controller


app = None


def main():
    global app
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    controller = Controller()
    controller.start()
    sys.exit(app.exec())
