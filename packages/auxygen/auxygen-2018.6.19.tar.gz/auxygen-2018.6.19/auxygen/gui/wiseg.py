#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg
from qtsnbl.widgets import FixedWidget
from .ui.ui_wiseg import Ui_WIseg
from .. import utils
from .. import devices, scripo


class WIseg(QtWidgets.QDialog, Ui_WIseg, FixedWidget):
    sigClosed = QtCore.pyqtSignal()
    sigShowSeqAction = QtCore.pyqtSignal(dict, object)
    sigCreateSeqAction = QtCore.pyqtSignal(dict, object, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.signalOnHold = None
        self.holdVoltage = 0
        self.chunkSize = 200
        self.maxChunks = 10
        self.startTime = pg.ptime.time()
        self.script = scripo.iseg.Iseg()
        self.device = devices.iseg.Iseg()
        self.cleanData()
        self.setUI()
        self.connectSignals()

    def cleanData(self):
        self.curves = [[], []]
        self.data = [np.empty((self.chunkSize + 1, 2)), np.empty((self.chunkSize + 1, 2))]
        self.ptr = [0, 0]

    def connectSignals(self):
        self.device.sigConnected.connect(self.connectionSucceed)
        self.device.sigDisconnected.connect(self.connectionFailed)
        self.device.sigError.connect(self.fatal)
        self.device.sigIdentifier.connect(self.setDeviceInfo)
        self.device.sigControl.connect(self.setRemoteFlag)
        self.device.sigPolarity.connect(self.setPolarityFlag)
        self.device.sigHV.connect(self.setHVFlag)
        self.device.sigInhibit.connect(self.setInhibitFlag)
        self.device.sigKill.connect(self.setKillFlag)
        self.device.sigExceeded.connect(self.setExceededFlag)
        self.device.sigStatusInfo.connect(self.labelStatus.setText)
        self.device.sigVoltage.connect(self.setVoltage)
        self.device.sigVoltage.connect(self.script._setVoltage)
        self.device.sigCurrent.connect(self.setCurrent)
        self.device.sigRamp.connect(self.setRamp)
        self.script._sigCreateIsegAction.connect(self.createAction)
        self.script._sigWaitFromSeq.connect(self.setSignalOnHold)
        self.sigShowSeqAction.connect(self.showSeqAction)
        # noinspection PyUnresolvedReferences
        self.rgroup.buttonClicked[int].connect(self.setChannel)

    def setUI(self):
        self.setupUi(self)
        self.rgroup = QtWidgets.QButtonGroup()
        self.rgroup.addButton(self.radioA, 1)
        self.rgroup.addButton(self.radioB, 2)
        self.tabWidget.setCurrentIndex(0)
        self.editError.setValidator(QtGui.QDoubleValidator())
        self.editComTimeout.setValidator(QtGui.QIntValidator())
        self._style = QtWidgets.QApplication.style()
        self.buttonClose.setIcon(self._style.standardIcon(self._style.SP_DockWidgetCloseButton))
        self.connectionFailed()
        self.vplot = self.plotVoltage.addPlot()
        self.vplot.setLabel('bottom', 'Time', 's')
        self.vplot.setLabel('left', 'Voltage', 'V')
        self.vplot.num = 0
        self.cplot = self.plotCurrent.addPlot()
        self.cplot.setLabel('bottom', 'Time', 's')
        self.cplot.setLabel('left', 'Current', 'A')
        self.cplot.num = 1

    def saveSettings(self):
        _ = QtCore.QSettings().setValue
        _('WIseg/Geometry', self.saveGeometry())
        _('WIseg/address', self.editAddress.text())
        _('WIseg/timeout', self.editComTimeout.text())
        _('WIseg/error', self.editError.text())
        _('WIseg/voltage', self.sbVoltage.value())
        _('WIseg/ramp', self.sbRamp.value())
        _('WIseg/channel', self.rgroup.checkedId())

    def loadSettings(self):
        _ = QtCore.QSettings().value
        self.restoreGeometry(_('WIseg/Geometry', b''))
        self.editError.setText(_('WIseg/error', str(utils.DEFAULT_ERROR), str))
        self.editComTimeout.setText(_('WIseg/timeout', str(utils.DEFAULT_TIMEOUT), str))
        self.editAddress.setText(_('WIseg/address', 'localhost:7900', str))
        self.sbVoltage.setValue(_('WIseg/voltage', 0, int))
        self.sbRamp.setValue(_('WIseg/ramp', 2, int))
        channel: int = _('WIseg/channel', 1, int)
        self.rgroup.button(channel).setChecked(True)
        self.setChannel(channel)

    @QtCore.pyqtSlot()
    def on_buttonClose_clicked(self):
        self.close()

    def closeEvent(self, event):
        self.device.stop()
        self.on_buttonDisconnect_clicked()
        self.saveSettings()
        self.sigClosed.emit()

    @QtCore.pyqtSlot()
    def on_buttonConnect_clicked(self):
        address = self.editAddress.text()
        if not address:
            self.fatal('Address cannot be empty')
            return
        self.device.start(address)

    @QtCore.pyqtSlot()
    def on_buttonDisconnect_clicked(self):
        self.device.stop()
        self.connectionFailed()

    def connectionSucceed(self):
        self.buttonConnect.hide()
        self.buttonDisconnect.show()

    def connectionFailed(self):
        self.buttonConnect.show()
        self.buttonDisconnect.hide()
        self.setDeviceInfo(0, '', 2000, 6)
        self.setRemoteFlag(True)
        self.labelPolarityFlag.setText('0')
        self.setHVFlag(True)
        self.setInhibitFlag(False)
        self.setKillFlag(False)
        self.setExceededFlag(False)
        self.labelStatus.setText('Status unknown')

    def fatal(self, msg):
        QtWidgets.QMessageBox.critical(self, 'Iseg error', msg)
        self.on_buttonDisconnect_clicked()

    def setDeviceInfo(self, sn: int, firmware: str, max_volts: int, current: int):
        self.labelName.setText(f'Iseg NHQ {sn} {firmware}')
        self.labelMaxVoltage.setText(f'{max_volts}')
        self.labelMaxCurrent.setText(f'{current}')
        self.sbVoltage.setMaximum(max_volts)
        self.script._setMaxVoltage(max_volts)

    def setRemoteFlag(self, manual: bool):
        pixmap = self._style.SP_DialogNoButton if manual else self._style.SP_DialogYesButton
        self.labelRemoteFlag.setPixmap(self._style.standardPixmap(pixmap))

    def setPolarityFlag(self, polarity: bool):
        self.labelPolarityFlag.setText('+' if polarity else '-')

    def setHVFlag(self, hv: bool):
        pixmap = self._style.SP_DialogNoButton if hv else self._style.SP_DialogYesButton
        self.labelHVFlag.setPixmap(self._style.standardPixmap(pixmap))

    def setInhibitFlag(self, inh: bool):
        pixmap = self._style.SP_DialogYesButton if inh else self._style.SP_DialogNoButton
        self.labelInhibitFlag.setPixmap(self._style.standardPixmap(pixmap))

    def setKillFlag(self, kill: bool):
        pixmap = self._style.SP_DialogYesButton if kill else self._style.SP_DialogNoButton
        self.labelKillFlag.setPixmap(self._style.standardPixmap(pixmap))

    def setExceededFlag(self, exc: bool):
        pixmap = self._style.SP_DialogYesButton if exc else self._style.SP_DialogNoButton
        self.labelExceededFlag.setPixmap(self._style.standardPixmap(pixmap))
        self.labelExceeded.setStyleSheet(f'QLabel{{color: {"red" if exc else "green"};}}')

    def setVoltage(self, voltage: int):
        self.labelVoltage.setText(f'Voltage: {voltage} V')
        self.drawCurve(self.vplot, voltage)

    def setCurrent(self, current: float):
        self.labelCurrent.setText(f'Current: {current:.2e} A')
        self.drawCurve(self.cplot, current)

    def setRamp(self, ramp: int):
        self.labelRamp.setText(f'{ramp}')

    @QtCore.pyqtSlot()
    def on_buttonRun_clicked(self):
        self.device.setVoltage(self.sbVoltage.value(), self.sbRamp.value())

    def drawCurve(self, plot, value):
        if plot == self.vplot:
            self.checkSignalOnHold(value)
        now = pg.ptime.time()
        for c in self.curves[plot.num]:
            c.setPos(-(now - self.startTime), 0)
        i = self.ptr[plot.num] % self.chunkSize
        if i == 0:
            curve = plot.plot()
            self.curves[plot.num].append(curve)
            last = self.data[plot.num][-1] if self.ptr[plot.num] != 0 else value
            self.data[plot.num] = np.empty((self.chunkSize + 1, 2))
            self.data[plot.num][0] = last
            while len(self.curves[plot.num]) > self.maxChunks:
                c = self.curves[plot.num].pop(0)
                self.plots[plot.num].removeItem(c)
        else:
            curve = self.curves[plot.num][-1]
        self.data[plot.num][i + 1, 0] = now - self.startTime
        self.data[plot.num][i + 1, 1] = value
        curve.setData(x=self.data[plot.num][:i + 2, 0],
                      y=self.data[plot.num][:i + 2, 1],
                      pen=pg.mkPen(width=3, color='r'))
        self.ptr[plot.num] += 1
        plot.setXRange(-60, 0)

    @QtCore.pyqtSlot()
    def on_buttonToSeq_clicked(self):
        self.createAction(self.sbVoltage.value(), self.sbRamp.value(), False)

    def createAction(self, voltage, ramp, now):
        d = {
            f'Iseg NHQ: to {voltage} V with rate {ramp} V/s':
                {
                    f'Voltage: {voltage} V': f'sbVoltage={voltage}',
                    f'Ramp: {ramp} V/s': f'sbRamp={ramp}'
                }
        }
        self.sbVoltage.setValue(voltage)
        self.sbRamp.setValue(ramp)
        self.sigCreateSeqAction.emit(d, self.sigShowSeqAction, now)

    def showSeqAction(self, action, signal):
        for v in list(action.values())[0].values():
            name, val = v.split('=')
            self.__dict__[name].setValue(int(val))
        if not signal:
            return
        self.holdVoltage = self.sbVoltage.value()
        self.on_buttonRun_clicked()
        signal.emit()

    def setSignalOnHold(self, action, signal):
        if not signal:
            return
        self.isegAction = action
        try:
            timeout = int(self.editComTimeout.text())
        except ValueError:
            timeout = utils.DEFAULT_TIMEOUT
        QtCore.QTimer.singleShot(timeout, lambda: setattr(self, 'signalOnHold', signal))

    def checkSignalOnHold(self, value: int):
        try:
            error = float(self.editError.text())
        except ValueError:
            error = utils.DEFAULT_ERROR
        if not self.signalOnHold or abs(value - self.holdVoltage) > error:
            return
        signal = self.signalOnHold
        self.signalOnHold = None
        signal.emit()

    def setChannel(self, channel: int):
        self.device.setChannel(channel)
