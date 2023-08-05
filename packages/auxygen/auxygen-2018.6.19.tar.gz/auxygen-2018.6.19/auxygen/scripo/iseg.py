#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from .utils import customable


class Iseg(QtCore.QObject):
    _sigWaitFromSeq = QtCore.pyqtSignal(dict, object)
    _sigCreateIsegAction = QtCore.pyqtSignal(int, int, bool)
    _sigCreateIsegWaitAction = QtCore.pyqtSignal(dict, object, bool)
    specialWords = {'iseg.setVoltage', 'iseg.wait', 'iseg.voltage'}

    def __init__(self):
        super().__init__()
        self._voltage = 0
        self._max_voltage = 0

    @customable
    def setVoltage(self, voltage, ramp, **kwargs):
        if not 0 <= voltage <= self._max_voltage:
            raise ValueError(f'Iseg voltage must be between 0 and {self._max_voltage}')
        if not 2 <= ramp <= 255:
            raise ValueError('Iseg ramp rate must be between 2 and 255')
        self._sigCreateIsegAction.emit(voltage, ramp, kwargs.get('now', False))

    @customable
    def wait(self, **kwargs):
        now = kwargs.get('now', False)
        self._sigCreateIsegWaitAction.emit({'Wait for the Iseg voltage': 'waitOnTemp=1'}, self._sigWaitFromSeq, now)

    def _setVoltage(self, voltage):
        self._voltage = voltage

    @property
    def voltage(self):
        return self._voltage

    def _setMaxVoltage(self, max_voltage):
        self._max_voltage = max_voltage
