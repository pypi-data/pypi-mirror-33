#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import socket
import kombu
import auxygen
from PyQt5 import QtCore
from .config import Config
from ..gui.gutils import GUtils


RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
EXCHANGE_DCU = 'Pilatus_data'
QUEUE_DCU = 'Pilatus_data'
EXCHANGE_SCAN = 'Pilatus_scans'


def get_hostport(address):
    if isinstance(address, (tuple, list)):
        host, port = address
    elif isinstance(address, str):
        if ':' in address:
            host, port = address.split(':')[:2]
        else:
            host, port = address, RABBITMQ_PORT
    else:
        host, port = RABBITMQ_HOST, RABBITMQ_PORT
    try:
        port = int(port)
    except ValueError:
        port = RABBITMQ_PORT
    return host, port


class RabbitMQ(QtCore.QObject):
    sigConnected = QtCore.pyqtSignal()
    sigDisconnected = QtCore.pyqtSignal()
    sigScanValue = QtCore.pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.address = None
        self.host = None
        self.port = None
        self.connection = None
        self.producer = None
        self.running = False
        self.reconnecting = False
        self.timer = None
        self.logger = auxygen.devices.logger.Logger('RabbitMQ')

    def setConfig(self):
        if Config.RabbitMQAddress == self.address:
            return
        self.address = Config.RabbitMQAddress
        self.host, self.port = get_hostport(self.address)
        if self.running:
            self.start()

    def start(self):
        self.running = True
        self.timer = QtCore.QTimer()
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.drainEvents)
        self.connect()

    def connect(self):
        self._disconnect()
        if not self.host or not self.port:
            return False
        self.connection = kombu.Connection(f'amqp://{self.host}:{self.port}//')
        try:
            self.connection.connect()
        except socket.error as err:
            self._disconnect()
            self.logger.error(f'Could not connect to {self.host}:{self.port}: {str(err)}')
            return False
        channel = self.connection.channel()
        exchange = kombu.Exchange(EXCHANGE_DCU, type='fanout', durable=False)
        self.producer = kombu.Producer(exchange=exchange, channel=channel, routing_key='', serializer='json')
        exchange_scan = kombu.Exchange(EXCHANGE_SCAN, type='fanout', durable=False)
        queue = kombu.Queue(EXCHANGE_SCAN, exchange_scan, channel=channel)
        self.consumer = kombu.Consumer(channel, queue, no_ack=True, prefetch_count=1, on_message=self.processScan)
        self.consumer.consume()
        self.sigConnected.emit()
        self.logger.info(f'Connected to {self.host}:{self.port}. Declared the exchange {EXCHANGE_DCU}')
        return True

    def stop(self):
        self.running = False
        self._disconnect()

    def _disconnect(self):
        if self.connection:
            self.connection.release()
            self.logger.warn(f'Disconnected from {self.host}:{self.port}')
        self.connection = None
        self.producer = None
        self.consumer = None
        self.sigDisconnected.emit()

    def _send(self, obj):
        if not self.connection:
            return
        if self.connection.connected:
            try:
                self.producer.publish(obj)
            except OSError as err:
                self.logger.warn(f'RabbitMQ has gone: {str(err)}. Trying to reconnect...')
                self.reconnect()
                QtCore.QTimer.singleShot(int(self.reconnecting) * 1000, lambda: self._send(obj))

    def reconnect(self):
        if not self.reconnecting:
            self.reconnecting = True
            while self.running:
                self.logger.warning('Trying to reconnect to RabbitMQ in 1 second')
                GUtils.delay(1000)
                if self.connect():
                    break
            self.reconnecting = False

    def sendChunk(self, opts):
        # a workaround to avoid sending exp params every period
        if not opts.sent:
            opts.sent = True
            self._send(opts.json())

    def processScan(self, message):
        try:
            name, value = json.loads(message.payload)
        except json.JSONDecodeError as err:
            self.logger.error(f'Error in JSON from PPU Broker: {err}')
        else:
            self.sigScanValue.emit(name, value)

    def drainEvents(self):
        if self.running and self.connection and self.connection.connected and not self.reconnecting:
            try:
                self.connection.drain_events(timeout=0.01)
            except socket.timeout:
                pass

    def scanStarted(self):
        self.timer.start(10)

    def scanFinished(self):
        self.timer.stop()
