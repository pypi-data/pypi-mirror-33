#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from collections import deque
from PyQt5 import QtCore, QtNetwork


class Iseg(QtCore.QObject):
    sigError = QtCore.pyqtSignal(str)
    sigDisconnected = QtCore.pyqtSignal()
    sigConnected = QtCore.pyqtSignal()
    sigVoltage = QtCore.pyqtSignal(int)
    sigCurrent = QtCore.pyqtSignal(float)
    sigRamp = QtCore.pyqtSignal(int)
    sigStatusInfo = QtCore.pyqtSignal(str)
    sigIdentifier = QtCore.pyqtSignal(int, str, int, int)
    sigQuality = QtCore.pyqtSignal(bool)
    sigMeasure = QtCore.pyqtSignal(bool)
    sigExceeded = QtCore.pyqtSignal(bool)
    sigInhibit = QtCore.pyqtSignal(bool)
    sigKill = QtCore.pyqtSignal(bool)
    sigHV = QtCore.pyqtSignal(bool)
    sigPolarity = QtCore.pyqtSignal(bool)
    sigControl = QtCore.pyqtSignal(bool)

    ModuleStatusUI: int = 1
    ModuleStatusControl: int = 2
    ModuleStatusPolarity: int = 4
    ModuleStatusHV: int = 8
    ModuleStatusKILL: int = 16
    ModuleStatusINHIBIT: int = 32
    ModuleStatusERR: int = 64
    ModuleStatusQUA: int = 128

    status_info: dict = {
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
        'S2=ON': 'Output 2 voltage according to set voltage',
        'S2=OFF': 'Channel 2 front panel switch off',
        'S2=MAN': 'Channel 2 is on, set to manual mode',
        'S2=ERR': 'Channel 2 Vmax or Imax is / was exceeded',
        'S2=INH': 'Channel 2 inhibit signal was / is active',
        'S2=QUA': 'Quality of output 2 voltage not guaranteed at present',
        'S2=L2H': 'Output 2 voltage increasing',
        'S2=H2L': 'Output 2 voltage decreasing',
        'S2=LAS': 'Look at Status of channel 2 (only after G-command)',
        'S2=TRP': 'Current trip was active on channel 2',
    }

    def __init__(self):
        super().__init__()
        self.channel: int = 1
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
            'U2': self.parseVoltage,
            'I2': self.parseCurrent,
            'S2': self.parseStatusInfo,
            'G2': self.parseStatusInfo,
            'V2': self.parseRamp,
            'T2': self.parseModuleStatus,
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
        self.send(f'S{self.channel}')
        self.send(f'T{self.channel}')
        self.send(f'U{self.channel}')
        self.send(f'I{self.channel}')
        self.send(f'V{self.channel}')

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
                if '=' in chunk and not chunk.startswith('S1') and not chunk.startswith('S2'):
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
            self.sigVoltage.emit(int(value))
        except ValueError as err:
            self.fatal(f'Unparsable voltage: {value}: {err}')

    def parseRamp(self, value: str):
        try:
            self.sigRamp.emit(int(value))
        except ValueError as err:
            self.fatal(f'Unparsable ramp: {value}: {err}')

    def parseCurrent(self, value: str):
        if '-' in value:
            mantissa, exponent = value.split('-')
            sign = -1
        elif '+' in value:
            mantissa, exponent = value.split('+')
            sign = 1
        else:
            mantissa, exponent, sign = value, 1, 1
        try:
            current = float(mantissa) * (10 ** (sign * float(exponent)))
        except ValueError as err:
            self.fatal(f'Unparsable current: {value}: {err}')
        else:
            self.sigCurrent.emit(current)

    def parseStatusInfo(self, value: str):
        try:
            self.sigStatusInfo.emit(self.status_info[value])
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
            return self.fatal(f'Wrong identifier: {value} -> {err}')
        self.sigConnected.emit()
        self.sigIdentifier.emit(sn, firmware, self.max_voltage, current)

    def parseModuleStatus(self, value: str):
        try:
            bf = int(value)
        except ValueError as err:
            return self.fatal(f'Unparsable module status: {value}: {err}')
        self.sigQuality.emit(bool(bf & self.ModuleStatusQUA))
        self.sigExceeded.emit(bool(bf & self.ModuleStatusERR))
        self.sigInhibit.emit(bool(bf & self.ModuleStatusINHIBIT))
        self.sigKill.emit(bool(bf & self.ModuleStatusKILL))
        self.sigHV.emit(bool(bf & self.ModuleStatusHV))  # OFF is 1, actually
        self.sigPolarity.emit(bool(bf & self.ModuleStatusPolarity))
        self.sigControl.emit(bool(bf & self.ModuleStatusControl))  # manual is 1

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

    def start(self, device: str = ''):
        self.sigVoltage.emit(0)
        self.sigCurrent.emit(0)
        self.createSocket()
        self.connectSignals()
        host, port = device.split(':')
        try:
            self.socket.connectToHost(host, int(port))
        except ValueError:
            self.fatal(f'ISEG error: tcp port {port} is wrong')

    def isConnected(self) -> bool:
        return self.timer.isActive() and self.socket.isValid()

    def setVoltage(self, voltage: int, ramp: int):
        if voltage > self.max_voltage:
            return self.sigError.emit(f'Set voltage {voltage} exceeds maximum Iseg voltage {self.max_voltage}')
        if not 2 <= ramp <= 255:
            return self.sigError.emit(f'Ramp of {ramp} is not valid, it should be in [2; 255]')
        self.send(f'V{self.channel}={ramp:03d}')
        self.send(f'D{self.channel}={voltage:04d}')
        self.send(f'G{self.channel}')

    def setChannel(self, channel: int):
        if channel not in (1, 2):
            return self.fatal(f'Channel cannot be {channel}, it must be 1(A) or 2(B)')
        self.stop()
        self.channel = channel
