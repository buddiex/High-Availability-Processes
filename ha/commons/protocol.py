import time
import json

import config as conf
from ha.commons.connection import ClientConn, logger
from ha.commons.utils import ConnectionError


class BasePackage(object):
    def __init__(self, package_type,cmd, args):
        self.cmd = cmd
        self.args = args
        self.package_type = package_type
        self.data = {}

    def pack(self)-> dict:
        if self._validate_request():
            self.data = {"type": self.package_type,
                         "command": self.cmd,
                         "send_time": time.time(),
                         "payload": self.args}
        else:
            raise RuntimeError(f"wrong command format for {self.cmd}: {self.args}")

        return json.dumps(self.data).encode()

    def _validate_request(self):
        return True


class RequestPackage(BasePackage):
    def __init__(self, cmd, args=''):
        super(RequestPackage, self).__init__('request', cmd, args )


class RespondsePackage(BasePackage):

    def __init__(self, cmd, args=''):
        super(RespondsePackage, self).__init__('response', cmd, args )


class Request(object):

    def __init__(self, server_IP, server_port):
        self.server = ClientConn((server_IP, server_port))
        self._connect_to_server()
        self.data = ''

    def get(self, args):
        self._package('GET', args)
        return self._send_recv()

    def post(self, args):
        self._package('POST', args)
        return self._send_recv()

    def put(self, args):
        self._package('PUT', args)
        return self._send_recv()

    def delete(self, args):
        self._package('DELETE', args)
        return self._send_recv()

    def _package(self, cmd, args):
        pk = RequestPackage(cmd,args)
        self.data = pk.pack()

    def _connect_to_server(self):
        attempts = 0
        while attempts != conf.MAX_CLIENT_CONN_ATTEMPT:
            try:
                self.server.connect_client_to_socket()
                break
            except Exception as err:
                attempts += 1
                time.sleep(1)
                raise

        else:
            raise ConnectionError("failed to connect after {} attempts".format(attempts))

    def _send_recv(self):
        try:
            self._send_message()
            return Respondse(self._recieve_message())
        except Exception as err:
            msg = 'server terminated connection: {}'.format(err)
            logger.info(msg)
            raise ConnectionAbortedError(msg)

        # finally:
        #     # self.server.socket.shutdown(socket.SHUT_RDWR)
        #     self.server.socket.close()
        #     logger.debug("shutting down server connection")

    def _send_message(self):
        self.server.enqueue(self.data)
        self.server.send()

    def _recieve_message(self):
        return self.server.recv()

    def _validate_request(self, cmd, args) -> bool:
        # @TODO implement validate of commands
        return True


class Respondse(object):
    def __init__(self, msg) -> None:
        self._respondse = msg
        self.data: dict = {}
        self._process_response()

    def _process_response(self) -> None:
        msg = json.loads(self._respondse)
        if self._validate_response(msg):
            self.data = msg
        else:
            raise RuntimeError(f"wrongly formatted respondse {msg}")

    def _validate_response(self, msg) -> bool:
        # @TODO implement validate of respondse
        return True
