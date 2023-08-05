#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from collections import deque
from PyQt5 import QtCore, QtNetwork


class Iseg(QtCore.QObject):
    sigError = QtCore.pyqtSignal(str)
    sigDisconnected = QtCore.pyqtSignal()
    sigConnected = QtCore.pyqtSignal()
    sigVoltage1 = QtCore.pyqtSignal(int)
    sigCurrent1 = QtCore.pyqtSignal(float)
    sigRamp1 = QtCore.pyqtSignal(int)
    sigStatusInfo1 = QtCore.pyqtSignal(str)
    sigIdentifier = QtCore.pyqtSignal(int, str, int, int)
    sigQuality = QtCore.pyqtSignal(bool)
    sigMeasure = QtCore.pyqtSignal(bool)
    sigExceeded = QtCore.pyqtSignal(bool)
    sigInhibit = QtCore.pyqtSignal(bool)
    sigKill = QtCore.pyqtSignal(bool)
    sigHV = QtCore.pyqtSignal(bool)
    sigPolarity = QtCore.pyqtSignal(bool)
    sigControl = QtCore.pyqtSignal(bool)

    ModuleStatusUI = 1
    ModuleStatusControl = 2
    ModuleStatusPolarity = 4
    ModuleStatusHV = 8
    ModuleStatusKILL = 16
    ModuleStatusINHIBIT = 32
    ModuleStatusERR = 64
    ModuleStatusQUA = 128

    def __init__(self):
        super().__init__()
        self.skip: bool = False
        self.max_voltage: int = 0
        self.last_cmd: str = ''
        self.buffer: bytes = b''
        self.awaiting: bool = False
        self.command_parser: dict = {
            '#': self.parseIdentifier,
            'U1': self.parseVoltage,
            'I1': self.parseCurrent,
            'S1': self.parseStatusInfo,
            'G1': self.parseStatusInfo,
            'V1': self.parseRamp,
            'T1': self.parseModuleStatus,
        }
        self.status_info: dict = {
            'S1=ON': 'Output 1 voltage according to set voltage',
            'S1=OFF': 'Channel 1 front panel switch off',
            'S1=MAN': 'Channel 1 is on, set to manual mode',
            'S1=ERR': 'Channel 1 Vmax or Imax is / was exceeded',
            'S1=INH': 'Channel 1 inhibit signal was / is active',
            'S1=QUA': 'Quality of output 1 voltage not guaranteed at present',
            'S1=L2H': 'Output 1 voltage increasing',
            'S1=H2L': 'Output 1 voltage decreasing',
            'S1=LAS': 'Look at Status of channel 1 (only after G-command)',
            'S1=TRP': 'Current trip was active on channel 1',
        }
        self.queue = deque()
        self.createSocket()
        self.connectSignals()

    def createSocket(self):
        self.timer = QtCore.QTimer()
        self.socket = QtNetwork.QTcpSocket()
        self.socket.setProxy(QtNetwork.QNetworkProxy(QtNetwork.QNetworkProxy.NoProxy))

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.timer.timeout.connect(self.pollQueue)
        self.socket.connected.connect(self.connectedToSocket)
        self.socket.readyRead.connect(self.readSocket)
        self.socket.disconnected.connect(self.stop)
        self.socket.error.connect(self.serverHasError)

    def connectedToSocket(self):
        self.timer.start(10)
        self.send('#')
        self.requestFullStatus(time.time())

    def requestFullStatus(self, timestamp: float):
        self.last_sent: float = timestamp
        self.send('S1')
        self.send('T1')
        self.send('U1')
        self.send('I1')
        self.send('V1')

    def send(self, packet: str):
        self.queue.append(f'{packet}\r\n'.encode('ascii'))

    def readSocket(self):
        if not self.socket.isValid():
            return
        self.buffer += bytes(self.socket.readAll())
        self.parseBuffer()

    def pollQueue(self):
        if self.awaiting:
            return
        current = time.time()
        if current - self.last_sent >= 1:
            self.requestFullStatus(current)
        if not self.queue:
            return
        packet = self.queue.popleft()
        self.socket.write(packet)
        self.awaiting = True

    def parseBuffer(self):
        while True:
            i = self.buffer.find(b'\r\n')
            if i == -1:
                return
            if self.skip:
                self.skip = False
                self.awaiting = False
            else:
                chunk = self.buffer[:i].decode().strip()
                if '=' in chunk and not chunk.startswith('S1'):
                    self.skip = True
                elif self.last_cmd:
                    self.command_parser[self.last_cmd](chunk)
                    self.last_cmd = ''
                    self.awaiting = False
                else:
                    self.last_cmd = chunk
            self.buffer = self.buffer[i + 2:]  # i + 2 is to skip b'\r\n'

    def parseVoltage(self, value: str):
        try:
            self.sigVoltage1.emit(int(value))
        except ValueError as err:
            self.fatal(f'Unparsable voltage: {value}: {err}')

    def parseRamp(self, value: str):
        try:
            self.sigRamp1.emit(int(value))
        except ValueError as err:
            self.fatal(f'Unparsable ramp: {value}: {err}')

    def parseCurrent(self, value: str):
        if '-' in value:
            mantissa, exponent = value.split('-')
        elif '+' in value:
            mantissa, exponent = value.split('+')
        else:
            mantissa, exponent = value, 1
        try:
            current = float(mantissa) * (10 ** float(exponent))
        except ValueError as err:
            self.fatal(f'Unparsable current: {value}: {err}')
        else:
            self.sigCurrent1.emit(current)

    def parseStatusInfo(self, value: str):
        try:
            self.sigStatusInfo1.emit(self.status_info[value])
        except KeyError as err:
            self.fatal(f'Unparsable status: {value}: {err}')

    def parseIdentifier(self, value: str):
        items = value.split(';')
        try:
            sn = int(items[0])
            firmware = items[1]
            self.max_voltage = int(items[2][:-1])
            i = items[3].find('mA')
            if i == -1:
                i = items[3].find('A')
                if i == -1:
                    raise ValueError('unparsable current')
                c = 1e3
            else:
                c = 1
            current = int(float(items[3][:i]) * c)
        except (ValueError, IndexError) as err:
            self.fatal(f'Wrong identifier: {value} -> {err}')
            return
        self.sigConnected.emit()
        self.sigIdentifier.emit(sn, firmware, self.max_voltage, current)

    def parseModuleStatus(self, value: str):
        try:
            bf = int(value)
        except ValueError as err:
            self.fatal(f'Unparsable module status: {value}: {err}')
            return
        self.sigQuality.emit(bool(bf & self.ModuleStatusQUA))
        self.sigExceeded.emit(bool(bf & self.ModuleStatusERR))
        self.sigInhibit.emit(bool(bf & self.ModuleStatusINHIBIT))
        self.sigKill.emit(bool(bf & self.ModuleStatusKILL))
        self.sigHV.emit(bool(bf & self.ModuleStatusHV))              # OFF is 1, actually
        self.sigPolarity.emit(bool(bf & self.ModuleStatusPolarity))
        self.sigControl.emit(bool(bf & self.ModuleStatusControl))    # manual is 1

    def stop(self):
        self.timer.stop()
        self.socket.disconnectFromHost()
        self.buffer = b''
        self.sigDisconnected.emit()

    def serverHasError(self):
        self.fatal(f'Cannot connect to ISEG: {self.socket.errorString()}')

    def fatal(self, msg: str):
        self.sigError.emit(msg)
        self.stop()

    def start(self, device: str):
        self.createSocket()
        self.connectSignals()
        host, port = device.split(':')
        try:
            port = int(port)
        except ValueError:
            self.fatal(f'ISEG error: tcp port {port} is wrong')
        else:
            self.socket.connectToHost(host, port)

    def isConnected(self) -> bool:
        return self.timer.isActive() and self.socket.isValid()

    def setVoltage(self, voltage: int, ramp: int):
        if voltage > self.max_voltage:
            self.sigError.emit(f'Set voltage {voltage} exceeds maximum Iseg voltage {self.max_voltage}')
            return
        if not 2 <= ramp <= 255:
            self.sigError.emit(f'Ramp of {ramp} is not valid, it should be in [2; 255]')
            return
        self.send(f'V1={ramp:03d}')
        self.send(f'D1={voltage:04d}')
        self.send('G1')
