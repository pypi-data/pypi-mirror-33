#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from .const import Spec
from .manager import manager


class Qounter(QtCore.QObject):
    sigConnected = QtCore.pyqtSignal(str)
    sigDisconnected = QtCore.pyqtSignal(str)
    sigValueChanged = QtCore.pyqtSignal(str, float)
    sigError = QtCore.pyqtSignal(str)
    sigCountingStarts = QtCore.pyqtSignal()
    sigCountingStops = QtCore.pyqtSignal()

    def __init__(self, address, name):
        super().__init__()
        self._address = address
        self._name = name
        self._value = 0
        self._manager = manager
        self._connected = False
        self._counting: bool = False
        self._connect()

    def _connect(self):
        self.sigCountingStarts.connect(self._setCounting)
        self.sigCountingStops.connect(self._setNotCounting)
        self._connection = self._manager.qonnect(self._address)
        self._message = self._connection.message
        self._connection.sigConnectedToSpec.connect(self._connectedToSpec)
        self._connection.sigSpecReplyArrived.connect(self._parseReply)
        self._connection.sigError.connect(self._connectionHasError)
        self._connection.sigCountingStarts.connect(self.sigCountingStarts.emit)
        self._connection.sigCountingStops.connect(self.sigCountingStops.emit)
        if self._connection.connected:
            QtCore.QTimer.singleShot(0, self._connectedToSpec)

    def _setCounting(self):
        self._counting = True

    def _setNotCounting(self):
        self._counting = False

    def _connectionHasError(self, emsg):
        self._connected = False
        self.sigError.emit(emsg)

    def _connectedToSpec(self):
        self._connected = True
        self._connection.send(self._message.counter_register(self._name))
        self._connection.send(self._message.counter_read(self._name))
        self.sigConnected.emit(self._name)

    def _parseReply(self, header, value):
        try:
            device, name, propert = header.name.decode().split('/')
        except ValueError:
            return
        if device != 'scaler' or name != self._name or header.cmd not in (Spec.Event, Spec.Reply):
            return
        elif isinstance(value, str):
            self.sigError.emit(f'counter {self._name} at {self._address[0]}:{self._address[1]}: {value}')
        elif propert == 'value':
            self._value = value
            self.sigValueChanged.emit(self._name, value)

    def read(self):
        self._connection.send(self._message.counter_read(self._name))

    def count(self, sec):
        self._connection.send(self._message.counter_count(self._name, sec))

    def isConnected(self):
        return self._connected

    def name(self):
        return self._name

    def value(self):
        return self._value

    def connection(self):
        return self._connection

    def isCounting(self) -> bool:
        return self._counting

    def __del__(self):
        self._connection.send(self._message.counter_unregister(self._name))
