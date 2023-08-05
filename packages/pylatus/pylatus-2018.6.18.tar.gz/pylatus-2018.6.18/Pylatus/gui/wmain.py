#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import sip
from PyQt5 import QtCore, QtGui, QtWidgets
import auxygen
from qtsnbl.widgets import FixedWidget
from ..controller.chunks import PylatusExperimentParams
from .ui.ui_wmain import Ui_WPylatus
from .wabout import WAbout
from .gutils import GUtils
from ..controller.config import Config


class WMain(QtWidgets.QMainWindow, Ui_WPylatus, FixedWidget):
    sigClose = QtCore.pyqtSignal()
    sigConnectMotor = QtCore.pyqtSignal(str, str, str)
    sigRemoveMotor = QtCore.pyqtSignal(str)
    sigStopAllMotors = QtCore.pyqtSignal()
    sigConnectDetector = QtCore.pyqtSignal()
    sigReconnectMotors = QtCore.pyqtSignal()
    sigAbort = QtCore.pyqtSignal()
    sigUpdateWavelength = QtCore.pyqtSignal(float)
    sigSetMinPlvert = QtCore.pyqtSignal(float)
    sigSetPhiScan = QtCore.pyqtSignal()
    sigSetOmegaScan = QtCore.pyqtSignal()
    sigSetPrphiScan = QtCore.pyqtSignal()
    sigStartExperiment = QtCore.pyqtSignal(object)
    sigCreateSeqAction = QtCore.pyqtSignal(dict, object)
    sigShowSeqAction = QtCore.pyqtSignal(dict, object)
    sigPoni = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixWindow()
        self.sigSeqDone = None
        self.running = False
        self.lastdir = ''
        self.logger = auxygen.devices.logger.Logger('GUI')
        self.setUI()
        self.actionHideMainWindow.setChecked(not sys.platform.startswith('linux'))
        self.motorsList.keyPressEvent = self.motorsListKeyPressEvent
        self.sigShowSeqAction.connect(self.showSequenceAction)

    def setUI(self):
        self.setupUi(self)
        # imported from auxygen
        self.actionStopMotors.setIcon(QtGui.QIcon(':/stop'))
        self.abortButton.setIcon(QtGui.QIcon(':/stop'))
        self.addSeqButton.setIcon(QtGui.QIcon(':/macro'))
        self.actionSequence.setIcon(QtGui.QIcon(':/macro'))
        self.actionCryostream.setIcon(QtGui.QIcon(':/cryo'))
        self.actionLakeshore.setIcon(QtGui.QIcon(':/lakeshore'))
        self.actionBlower.setIcon(QtGui.QIcon(':/blower'))
        self.actionIsegHV.setIcon(QtGui.QIcon(':/iseg'))
        self.actionScriptEditor.setIcon(QtGui.QIcon(':/scripted'))
        self.addDeviceButton.setIcon(QtGui.QIcon(':/add'))
        self.measureButton.setIcon(QtGui.QIcon(':/run'))
        style = QtWidgets.QApplication.style()
        self.actionAboutQt.setIcon(style.standardIcon(style.SP_TitleBarMenuButton))
        self.actionOpen_poni.setIcon(style.standardIcon(style.SP_DialogOpenButton))
        self.actionAboutPylatus.setIcon(style.standardIcon(style.SP_MessageBoxInformation))
        self.selectFolderButton.setIcon(style.standardIcon(style.SP_DirOpenIcon))

    def showLamp(self, show):
        self.lampLabel.setVisible(show)
        self.lampTextLabel.setVisible(show)

    def setRedLamp(self):
        self.lampLabel.setPixmap(QtGui.QPixmap(':/rlamp'))

    def setGreenLamp(self):
        self.lampLabel.setPixmap(QtGui.QPixmap(':/lamp'))

    def closeEvent(self, event):
        self.saveSettings()
        self.sigClose.emit()

    def saveSettings(self):
        s = Config.Settings
        s.setValue('WMain/Geometry', self.saveGeometry())
        s.setValue('WMain/filename', self.filenameLineEdit.text())
        s.setValue('WMain/exposition', self.exposureSpinBox.value())
        s.setValue('WMain/nframes', self.nframesSpinBox.value())
        s.setValue('WMain/dOmega', self.dOmegaSpinBox.value())
        s.setValue('WMain/sOmega', self.omegaSpinBox.value())
        s.setValue('WMain/phi', self.phiSpinBox.value())
        s.setValue('WMain/kappa', self.kappaSpinBox.value())
        s.setValue('WMain/folder', self.folderLineEdit.text())
        s.setValue('WMain/isKappa', self.kappaCheckBox.isChecked())
        s.setValue('WMain/phiScan', self.phiScanCheckBox.isChecked())
        s.setValue('WMain/pauseExp', self.pauseBeamOffCheckBox.isChecked())
        s.setValue('WMain/nperiods', self.nperiodsSpinBox.value())
        s.setValue('WMain/pldistd', self.pldistdSpinBox.value())
        s.setValue('WMain/pldistf', self.pldistfSpinBox.value())
        s.setValue('WMain/plrot', self.plrotSpinBox.value())
        s.setValue('WMain/plvert', self.plvertSpinBox.value())
        s.setValue('WMain/mod', self.modSpinBox.value())
        s.setValue('WMain/mod2', self.mod2SpinBox.value())
        s.setValue('WMain/zeroDist', self.zeroSpinBox.value())
        s.setValue('WMain/beamx', self.beamxSpinBox.value())
        s.setValue('WMain/beamy', self.beamySpinBox.value())
        s.setValue('WMain/detx', self.detectorxSpinBox.value())
        s.setValue('WMain/dety', self.detectorySpinBox.value())
        s.setValue('WMain/pixx', self.pixelxSpinBox.value())
        s.setValue('WMain/pixy', self.pixelySpinBox.value())
        s.setValue('WMain/prphiMax', self.prphiMaxSpinBox.value())
        s.setValue('WMain/phiMax', self.phiMaxSpinBox.value())
        s.setValue('WMain/omegaMax', self.omegaMaxSpinBox.value())
        s.setValue('WMain/wavelength', self.wlSpinBox.value())
        s.setValue('WMain/minplvert', self.minPlvertSpinBox.value())
        s.setValue('WMain/lastdir', self.lastdir)

    def loadSettings(self):
        s = Config.Settings
        self.restoreGeometry(s.value('WMain/Geometry', b''))
        self.filenameLineEdit.setText(s.value('WMain/filename', '', str))
        self.exposureSpinBox.setValue(s.value('WMain/exposition', 0, float))
        self.nframesSpinBox.setValue(s.value('WMain/nframes', 1, int))
        self.dOmegaSpinBox.setValue(s.value('WMain/dOmega', 0, float))
        self.omegaSpinBox.setValue(s.value('WMain/sOmega', 0, float))
        self.phiSpinBox.setValue(s.value('WMain/phi', 0, float))
        self.kappaSpinBox.setValue(s.value('WMain/kappa', 0, float))
        self.folderLineEdit.setText(s.value('WMain/folder', '', str))
        self.kappaCheckBox.setChecked(s.value('WMain/isKappa', True, bool))
        self.phiScanCheckBox.setChecked(s.value('WMain/phiScan', False, bool))
        self.nperiodsSpinBox.setValue(s.value('WMain/nperiods', 1, int))
        self.pldistdSpinBox.setValue(s.value('WMain/pldistd', 0, float))
        self.pldistfSpinBox.setValue(s.value('WMain/pldistf', 0, float))
        self.plrotSpinBox.setValue(s.value('WMain/plrot', 0, float))
        self.plvertSpinBox.setValue(s.value('WMain/plvert', 0, float))
        self.modSpinBox.setValue(s.value('WMain/mod', 0, int))
        self.mod2SpinBox.setValue(s.value('WMain/mod2', 0, int))
        self.zeroSpinBox.setValue(s.value('WMain/zeroDist', 156.88, float))
        self.beamxSpinBox.setValue(s.value('WMain/beamx', 542.414, float))
        self.beamySpinBox.setValue(s.value('WMain/beamy', 732.4, float))
        self.detectorxSpinBox.setValue(s.value('WMain/detx', 1679, int))
        self.detectorySpinBox.setValue(s.value('WMain/dety', 1475, int))
        self.pixelxSpinBox.setValue(s.value('WMain/pixx', 172, float))
        self.pixelySpinBox.setValue(s.value('WMain/pixy', 172, float))
        self.prphiMaxSpinBox.setValue(s.value('WMain/prphiMax', 10, float))
        self.phiMaxSpinBox.setValue(s.value('WMain/phiMax', 10, float))
        self.omegaMaxSpinBox.setValue(s.value('WMain/omegaMax', 10, float))
        self.wlSpinBox.setValue(s.value('WMain/wavelength', 0.69, float))
        self.minPlvertSpinBox.setValue(s.value('WMain/minplvert', -20, float))
        self.pauseBeamOffCheckBox.setChecked(s.value('WMain/pauseExp', False, bool))
        self.lastdir = s.value('WMain/lastdir', '', str)

    @QtCore.pyqtSlot(bool)
    def on_actionHideMainWindow_toggled(self, checked):
        self.tabWidget.setHidden(checked)
        self.statusbar.setHidden(checked)
        QtCore.QTimer.singleShot(10, lambda: self.resize(0, 0))

    @QtCore.pyqtSlot()
    def on_actionStopMotors_toggled(self):
        self.sigStopAllMotors.emit()

    def experimentFinished(self):
        self.running = False
        self.showLamp(False)
        self.statusbar.showMessage('Experiment has been finished')
        if self.sigSeqDone:
            signal = self.sigSeqDone
            self.sigSeqDone = None
            signal.emit()

    def experimentStarted(self):
        self.running = True
        self.showLamp(True)
        self.statusbar.showMessage('Experiment has been started')

    @QtCore.pyqtSlot()
    def on_measureButton_clicked(self, nop=False):
        cbfBaseName = self.filenameLineEdit.text()
        if not cbfBaseName:
            self.logger.error('Give the base file name!')
            return
        if cbfBaseName.endswith('.cbf'):
            cbfBaseName = cbfBaseName[:-4]
            self.filenameLineEdit.setText(cbfBaseName)
        userSubDir = self.folderLineEdit.text()
        if not userSubDir:
            self.logger.error('Choose the data folder!')
            return
        p = PylatusExperimentParams()
        p.periods = self.nperiodsSpinBox.value()
        p.cbfBaseName = cbfBaseName
        p.nframes = self.nframesSpinBox.value()
        p.userSubDir = userSubDir.strip('/\\')
        p.expPeriod = self.exposureSpinBox.value()
        p.startAngle = self.omegaSpinBox.value()
        p.step = self.dOmegaSpinBox.value()
        p.omegaphi = self.phiSpinBox.value()
        p.kappa = self.kappaSpinBox.value()
        p.mod = self.modSpinBox.value()
        p.mod2 = self.mod2SpinBox.value()
        p.zeroDistance = self.zeroSpinBox.value()
        p.beamX = self.beamxSpinBox.value()
        p.beamY = self.beamySpinBox.value()
        p.pixelX = self.pixelxSpinBox.value()
        p.pldistf = self.pldistfSpinBox.value()
        p.pldistd = self.pldistdSpinBox.value()
        p.plvert = self.plvertSpinBox.value()
        p.plrot = self.plrotSpinBox.value()
        p.nop = nop
        self.sigStartExperiment.emit(p)

    @QtCore.pyqtSlot()
    def on_actionConnectToPilatus_triggered(self):
        self.sigConnectDetector.emit()

    @QtCore.pyqtSlot()
    def on_actionConnectToMotors_triggered(self):
        self.sigReconnectMotors.emit()

    def showDCTime(self, days, hours, minutes, total):
        self.expTime = total
        if days:
            t = f'{days:d}d {hours:d}h {minutes:d}m'
        elif hours:
            t = f'{hours:d}h {minutes:d}m'
        else:
            t = f'{minutes:d}m'
        self.timeLabel.setText(t)

    def showMax2Theta(self, angle, d):
        self.max2ThetaLabel.setText(f'<html><body>{angle:.1f}&deg;|{d:.3f} &Aring;' '</body></html>')

    @QtCore.pyqtSlot()
    def on_selectFolderButton_clicked(self):
        txt = self.folderLineEdit.text()
        if txt.startswith('/'):
            txt = txt[1:]
        dirr = os.path.join(Config.UserDir, txt)
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select folder for the data', dirr)
        if not folder:
            return
        elif not folder.startswith(Config.UserDir):
            QtWidgets.QMessageBox.critical(self, 'Wrong parent folder',
                                           f'The chosen folder must be within {Config.UserDir}')
            return
        n = len(Config.UserDir)
        if Config.UserDir.endswith('/'):
            n -= 1
        dataDir = folder[n:]
        self.folderLineEdit.setText(dataDir)

    @QtCore.pyqtSlot()
    def on_abortButton_clicked(self):
        self.sigAbort.emit()

    @QtCore.pyqtSlot()
    def on_actionAboutQt_triggered(self):
        QtWidgets.QMessageBox.aboutQt(self)

    @QtCore.pyqtSlot()
    def on_actionAboutPylatus_triggered(self):
        WAbout(self).exec()

    @QtCore.pyqtSlot()
    def on_actionQuit_triggered(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_addSeqButton_clicked(self, nop=False):
        aw = {f'no periods: {nop}': f'nop={nop}'}
        for label in self.__dict__.values():
            if not isinstance(label, QtWidgets.QLabel) or not label.isEnabled():
                continue
            buddy = label.buddy()
            if buddy is not None:
                value = buddy.text()
                labelText = re.sub(r'<[^>]*>', '', label.text())
                aw[f'{labelText}: {value}'] = f'{buddy.objectName()}={value}'
        aw[f'Time for action (sec): {self.expTime}'] = str(self.expTime)
        self.sigCreateSeqAction.emit({f'Data collection for {self.timeLabel.text()}': aw}, self.sigShowSeqAction)

    def showSequenceAction(self, action, signal):
        nop = False
        for elem in list(action.values())[0].values():
            if '=' in elem:
                name, value = elem.split('=')
                if name in self.__dict__:
                    widget = self.__dict__[name]
                    if isinstance(widget, QtWidgets.QSpinBox):
                        widget.setValue(int(value))
                    elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                        widget.setValue(float(value))
                    elif isinstance(widget, QtWidgets.QLineEdit):
                        widget.setText(value)
                elif name == 'nop':
                    nop = value != 'False'
        if signal:
            self.sigSeqDone = signal
            self.on_measureButton_clicked(nop)

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, index):
        self.kappaGroupBox.setDisabled(True)
        self.musstGroupBox.setDisabled(True)
        self.beamGroupBox.setDisabled(True)
        self.detectorGroupBox.setDisabled(True)
        self.devicesGroupBox.setDisabled(True)
        self.prphiMaxSpinBox.setDisabled(True)
        self.phiMaxSpinBox.setDisabled(True)
        self.omegaMaxSpinBox.setDisabled(True)
        self.minPlvertSpinBox.setDisabled(True)
        self.settingsButton.setDisabled(True)
        if self.running:
            return
        if index == 1 and GUtils.askPass(self):
            self.kappaGroupBox.setEnabled(True)
            self.musstGroupBox.setEnabled(True)
            self.beamGroupBox.setEnabled(True)
            self.detectorGroupBox.setEnabled(True)
            self.pauseBeamOffCheckBox.setEnabled(True)
        elif index == 2 and GUtils.askPass(self):
            self.devicesGroupBox.setEnabled(True)
            self.prphiMaxSpinBox.setEnabled(True)
            self.phiMaxSpinBox.setEnabled(True)
            self.omegaMaxSpinBox.setEnabled(True)
            self.minPlvertSpinBox.setEnabled(True)
            self.settingsButton.setEnabled(True)
        self.saveSettings()

    @QtCore.pyqtSlot(bool)
    def on_kappaCheckBox_toggled(self, checked):
        self.phiSpinBox.setEnabled(checked)
        self.phiLabel.setEnabled(checked)
        self.kappaSpinBox.setEnabled(checked)
        self.kappaLabel.setEnabled(checked)
        self.phiScanCheckBox.setEnabled(checked)
        self.phiScanCheckBox.setChecked(False)
        if checked:
            self.sigSetOmegaScan.emit()
        else:
            self.sigSetPrphiScan.emit()

    @QtCore.pyqtSlot(bool)
    def on_phiScanCheckBox_toggled(self, checked):
        an1, an2 = ('&phi;', '&omega;') if checked else ('&omega;', '&phi;')
        self.dAngleLabel.setText(f'<html><head/><body><p>&Delta;{an1} per image (deg)</p></body></html>')
        self.startingAngleLabel.setText(f'<html><head/><body><p>Starting {an1}<span style="vertical-align:sub;">0'
                                        f'</span> (deg)</p></body></html>')
        self.phiLabel.setText(f'<html><head/><body><p>Position of {an2} (deg)</p></body></html>')
        if checked:
            self.sigSetPhiScan.emit()
        else:
            self.sigSetOmegaScan.emit()

    def runFromScript(self, args):
        for label in self.__dict__.values():
            if not isinstance(label, QtWidgets.QLabel) or not label.isEnabled():
                continue
            control = label.buddy()
            if control is None:
                continue
            controlName = control.objectName()
            for argName in args:
                if argName in controlName:
                    if isinstance(control, QtWidgets.QSpinBox):
                        control.setValue(int(args[argName]))
                    elif isinstance(control, QtWidgets.QDoubleSpinBox):
                        control.setValue(float(args[argName]))
                    elif isinstance(control, QtWidgets.QLineEdit):
                        control.setText(args[argName])
                    break
        self.on_addSeqButton_clicked(args.get('nop', False))

    @QtCore.pyqtSlot()
    def on_addDeviceButton_clicked(self):
        host = self.specServerLineEdit.text()
        spec = self.specSessionLineEdit.text()
        motor = self.specMotorLineEdit.text()
        self.sigConnectMotor.emit(host, spec, motor)

    def motorsListKeyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            for item in self.motorsList.selectedItems():
                self.sigRemoveMotor.emit(item.text())
                sip.delete(item)
        else:
            QtWidgets.QListWidget.keyPressEvent(self.motorsList, event)

    @QtCore.pyqtSlot(float)
    def on_minPlvertSpinBox_valueChanged(self, value):
        self.plvertSpinBox.setMinimum(value)
        self.sigSetMinPlvert.emit(value)

    @QtCore.pyqtSlot()
    def on_updateButton_clicked(self):
        self.sigUpdateWavelength.emit(self.wlSpinBox.value())

    def showMotorsList(self, motors):
        self.motorsList.insertItems(0, motors)

    def showMotor(self, motor):
        self.motorsList.insertItem(0, motor)

    def showEvent(self, event):
        super().showEvent(event)
        self.on_tabWidget_currentChanged(0)
        self.experimentFinished()

    def showTimeLeft(self, message):
        self.lampTextLabel.setText(message)

    def setScanType(self, scanType):
        if self.kappaCheckBox.isChecked():
            if scanType == 'omega':
                self.phiScanCheckBox.setChecked(False)
            elif scanType == 'phi':
                self.phiScanCheckBox.setChecked(True)

    @QtCore.pyqtSlot()
    def on_actionOpen_poni_triggered(self):
        poni = QtWidgets.QFileDialog.getOpenFileName(self, 'Open poni file...', self.lastdir, 'Poni (*.poni)')[0]
        if poni:
            self.lastdir = os.path.dirname(poni)
            self.sigPoni.emit(poni)
