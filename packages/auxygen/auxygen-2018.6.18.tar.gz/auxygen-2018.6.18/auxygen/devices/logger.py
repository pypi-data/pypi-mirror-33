#!/usr/bin/python
# -*- coding: utf-8 -*-

from functools import partial
from datetime import datetime
from PyQt5 import QtCore


class _Logger(QtCore.QObject):
    TimeoutFlush = 500  # msec
    sigPostLogMessage = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFile()
        self.sigPostLogMessage.connect(self._writeFile)

    def setFile(self, logFile=''):
        if logFile and logFile != self.outName:
            try:
                self.out = open(logFile, 'a+')
                self.outName = logFile
                self.timer = QtCore.QTimer()
                # noinspection PyUnresolvedReferences
                self.timer.timeout.connect(self._flush)
                self.timer.start(self.TimeoutFlush)
                return
            except OSError:
                pass
        self.out = None
        self.outName = ''
        self.readyToFlush = False
        self.timer = None

    def log(self, name, level, msg):
        message = f'{datetime.now():%Y-%m-%d %H:%M:%S.%f} {level}: {name}: {msg}\n'
        self.sigPostLogMessage.emit(message)

    def error(self, name, msg):
        self.log('ERROR', name, msg)

    def info(self, name, msg):
        self.log('INFO', name, msg)

    def warning(self, name, msg):
        self.log('WARNING', name, msg)

    warn = warning

    def _writeFile(self, message):
        if self.out:
            self.out.write(message)
            self.readyToFlush = True

    def _flush(self):
        if self.readyToFlush and self.out:
            self.out.flush()
            self.readyToFlush = False


class Logger:
    logger = _Logger()

    def __init__(self, name):
        self.log = partial(self.logger.log, name)
        self.info = partial(self.logger.info, name)
        self.error = partial(self.logger.error, name)
        self.warning = partial(self.logger.warning, name)
        self.warn = self.warning
