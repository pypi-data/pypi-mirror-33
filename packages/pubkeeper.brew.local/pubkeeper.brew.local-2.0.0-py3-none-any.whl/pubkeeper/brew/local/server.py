"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.logging import get_logger
from tornado import gen
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer


class LocalBrewServer(TCPServer):
    def __init__(self, *args, brewer_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)
        self.connected_streams = []
        self.brewer_id = brewer_id
        self.logger.debug("Starting {}".format(self.brewer_id))

    def handle_stream(self, stream, addr):
        self.logger.debug("Brewer {}: New Stream Connected".format(
            self.brewer_id
        ))
        self.connected_streams.append(stream)

    @gen.coroutine
    def write_all(self, data):
        closed = []
        for stream in self.connected_streams:
            try:
                ret = yield stream.write(data)
                if ret is not None:
                    self.logger.debug(
                        "Brewer {} - Write returned non none, closing".format(
                            self.brewer_id
                        )
                    )
                    closed.append(stream)
            except StreamClosedError:
                self.logger.debug(
                    "Brewer {} - StreamClosedError, closing".format(
                        self.brewer_id
                    )
                )
                closed.append(stream)

        for closed_stream in closed:
            self.connected_streams.remove(closed_stream)
