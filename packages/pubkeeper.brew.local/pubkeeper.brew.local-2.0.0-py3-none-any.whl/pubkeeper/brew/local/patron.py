"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.logging import get_logger
from tornado import gen
from tornado.iostream import IOStream, StreamClosedError
from struct import unpack, error as StructError
import socket
import os


class LocalBrewPatron(object):
    def __init__(self, sock, brew, patron_id, brewer_id, callback):
        self.sock = sock
        self.brew = brew
        self.patron_id = patron_id
        self.brewer_id = brewer_id
        self.callback = callback

        self.logger = get_logger(self.__class__.__name__)

        self.running = True

        self.connect()

    def connect(self):
        if os.name == 'nt' or self.brew._settings['use_localhost'] \
                or type(self.sock) is list:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock = (self.sock[0], self.sock[1])
        else:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock = self.sock

        self.stream = IOStream(self.socket)
        self.stream.connect(sock, callback=self._read_data)

    def stop(self):
        self.running = False
        self.stream.close()

    @gen.coroutine
    def _read_data(self):  # pragma no cover
        while self.running:
            try:
                (length,) = unpack('<I', (yield self.stream.read_bytes(4)))
                data = yield self.stream.read_bytes(length)
                self.callback(self.brewer_id, data)
            except StructError:
                self.logger.error("Unable to determine length of data")
                self.stream.close()
                self.connect()
                return
            except StreamClosedError:
                self.stop()
                return
