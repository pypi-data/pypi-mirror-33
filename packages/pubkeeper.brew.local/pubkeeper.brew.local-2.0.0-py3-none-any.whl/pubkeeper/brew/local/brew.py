"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from copy import deepcopy
from pubkeeper.brew.base import Brew
from pubkeeper.brew.local.server import LocalBrewServer
from pubkeeper.brew.local.patron import LocalBrewPatron
try:
    from tornado.netutil import bind_unix_socket, bind_sockets
except ImportError:
    from tornado.netutil import bind_sockets
from pubkeeper.utils.logging import get_logger
from pubkeeper.brew.local import LocalSettings
from uuid import getnode
from struct import pack
import socket
import os


class LocalBrew(Brew):
    def __init__(self, *args, **kwargs):
        self.logger = get_logger(self.__class__.__name__)
        self.name = "local-{}".format(str(getnode()))
        self._patrons = {}
        self._local_servers = {}
        self._local_servers_details = {}
        self._settings = deepcopy(LocalSettings)

        super().__init__(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        return LocalSettings

    def configure(self, context):
        non_casting_types = [type(None), str]
        for setting in self._settings.keys():
            if context and setting in context:
                _type = type(self._settings[setting])
                if _type in non_casting_types:
                    self._settings[setting] = context[setting]
                else:
                    # cast incoming value to known type
                    self._settings[setting] = _type(context[setting])

    def start(self):
        self.logger.info("Starting local brew")

    def stop(self):
        self.logger.info("Stopping local brew")
        for key, patron in self._patrons.items():
            patron.stop()

        for brewer_id, local_server in self._local_servers.items():
            local_server.stop()

    def create_brewer(self, brewer):
        if brewer.brewer_id not in self._local_servers:
            if os.name == 'nt' or self._settings['use_localhost']:
                _socket = bind_sockets(0, address='127.0.0.1',
                                       family=socket.AF_INET)[0]
                sock_args = ('127.0.0.1', _socket.getsockname()[1])
            else:
                sock_args = '/tmp/{}.sock'.format(brewer.brewer_id)
                _socket = bind_unix_socket(sock_args)

            self._local_servers[brewer.brewer_id] = LocalBrewServer(
                brewer_id=brewer.brewer_id
            )
            self._local_servers[brewer.brewer_id].add_socket(_socket)

            details = super().create_brewer(brewer)

            if details is None:
                details = {}

            details.update({
                'sock': sock_args,
            })

            self._local_servers_details[brewer.brewer_id] = details
        else:
            self.logger.warning("Brewer already created for {}".format(
                brewer.brewer_id
            ))

        return self._local_servers_details[brewer.brewer_id]

    def destroy_brewer(self, brewer):
        if brewer.brewer_id in self._local_servers:
            self._local_servers[brewer.brewer_id].stop()
            del(self._local_servers[brewer.brewer_id])

    def _patron_key(self, patron_id, brewer_id):
        return "{}.{}".format(patron_id, brewer_id)

    def create_patron(self, patron):
        details = super().create_patron(patron)

        if details is None:
            details = {}

        return details

    def start_patron(self, patron_id, topic, brewer_id, brewer_config,
                     brewer_brew, callback):
        key = self._patron_key(patron_id, brewer_id)
        if key in self._patrons:
            self.logger.info("Already subscribed to the brewer")

        self._patrons[key] = LocalBrewPatron(brewer_brew['sock'], self,
                                             patron_id, brewer_id,
                                             callback)

    def stop_patron(self, patron_id, topic, brewer_id):
        key = self._patron_key(patron_id, brewer_id)
        if key in self._patrons:
            self._patrons[key].stop()
            del(self._patrons[key])

    def brew(self, brewer_id, topic, data, patrons):
        if brewer_id in self._local_servers:
            self._local_servers[brewer_id].write_all(
                pack('<I', len(data)) + data
            )
