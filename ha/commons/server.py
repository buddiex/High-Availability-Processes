import json
import select
import time
import socket
# from queue import Queue
from typing import Dict
import config as conf
from ha.commons.logger import get_module_logger
from ha.commons.connection import ServerSideClientConn, ClientConn
from ha.commons.protocol import RespondsePackage

logger = get_module_logger(__name__)


class BaseRequestHandler(object):
    """Base class for request handler classes.
    """

    def __init__(self, client_conn: ServerSideClientConn):
        self.client_conn = client_conn
        self.setup()
        self.data = {}
        # try:
        #     self.handle()
        # finally:
        #     self.finish()

    def setup(self):
        pass

    def handle(self):
        raise NotImplementedError

    def send(self):
        self.client_conn.enqueue(self._json_encode())
        # self.client_conn.send()

    def recv(self):
        return self.client_conn.recv()

    def _json_encode(self) -> bytes:
        rtn = json.dumps(self.data).encode()
        return rtn

    def _json_load(self, msg) -> dict:
        return json.loads(msg)

    def finish(self):
        pass


class ProxyRequestHandler(BaseRequestHandler):

    def __init__(self, client_conn: ServerSideClientConn, server_conn: ClientConn):
        super(ProxyRequestHandler, self).__init__(client_conn)
        self.server_conn: ClientConn = server_conn

    def handle(self):
        self.data = self._json_load(self.recv())
        self.data['client'] = self.client_conn.peername()
        self.server_conn.enqueue(self._json_encode())
        self.server_conn.send()
        res = self.server_conn.recv()
        data = self._json_load(res)
        del data['client']
        self.data = data
        self.send()


class ServerRequestHandler(BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self._json_load(self.recv())
        # self.request.sendall(self.data.upper())
        self.send()


class BaseServer(object):

    def __init__(self, request_handler: BaseRequestHandler, hostname: str, port: int,
                 backlog: int = 100, max_client_count: int = conf.MAX_CLIENT_COUNT):
        self.server_type: str = ''
        self._new_conn: bool
        self.socket: socket
        self.server_address: tuple = (hostname, port)
        self.connections: Dict[tuple, ServerSideClientConn] = {}
        self.request_handler = request_handler
        self.client_tags = ''
        self.backlog = backlog
        self.max_client_count = max_client_count
        self.shutdown = False

        self.create_server_socket()

    def create_server_socket(self) -> None:

        """  configure a nonblocking socket at specified host and port

             returns the configured socket
        """
        # instantiate the socket
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as err:
            raise OSError(f"could not instantiate TCP socket {err}")
        self.socket.setblocking(False)

        # bind this socket to the specified port
        try:
            self.socket.bind(self.server_address)
        except Exception as err:
            raise OSError("could not bind to {}, port {}: {}".format(*self.server_address, err))

        # specify number of simultaneous clients to support
        try:
            self.socket.listen(self.max_client_count)
        except Exception as err:
            raise OSError("could not connect to {}, port {}: {}".format(*self.server_address, err))

    def handle(self, conn: ServerSideClientConn) -> None:
        raise NotImplementedError()

    def handle_error(self) -> None:
        pass

    def accept_new_connection(self) -> None:
        num_of_con = len(self.connections)
        con_name = self.client_tags + str(num_of_con + 1)
        self.socket.setblocking(False)
        if num_of_con == 0:
            self.socket.setblocking(True)
            logger.info('{} listening on {}:{}'.format(self.server_type, *self.server_address))
        try:
            conn, address = self.socket.accept()
            logger.info('client {}:{} added'.format(*conn.getpeername()))
        except Exception as err:
            raise ConnectionAbortedError(f"{self.server_type} cannot connect accept client: {err}")
        self.socket.setblocking(False)
        new_conn = ServerSideClientConn(conn, address, con_name)
        if len(self.connections) < self.max_client_count:
            self.connections[address] = new_conn
        else:
            self.reject_connection(new_conn)

    def serve_forever(self) -> None:

        # -----------------------------------------------------------------------------------
        #    Look for requests from interested clients,
        #    -.  fielding connection requests, up to limit -
        #        and closing connections beyond limit, with error messages
        #    -.  pushing sent content to other clients, prepended with connection information
        # ------------------------------------------------------------------------------------
        while not self.shutdown:
            # need try/except block because aborting connections generates exceptions that bypass select
            try:
                if not self.connections:
                    self.accept_new_connection()
                try:
                    self.get_all_socket_activities()
                except Exception as err:
                    raise

                # check for new connection requests
                if self._new_conn:
                    self.accept_new_connection()

                self._manage_error_socket()
                # obtain messages from active clients, enqueuing them to send to other clients

                self._manage_readable_sockets()
                # check for messages to send and the ability to send them

                self._manage_writable_sockets()

                time.sleep(0.5)

            except Exception as err:
                # halt all remaining dialogues with clients, if any
                try:
                    for conn in self.connections.values():
                        conn.close()
                except Exception as err:
                    pass
                # end of all exchanges
                self.socket.close()
                logger.info('exiting')
                if conf.DEBUG_MODE: raise

    def _manage_readable_sockets(self):
        for client_conn in [self.connections[sock.getpeername()] for sock in self._recv_sockets]:
            try:
                self.process_request(client_conn)
            except Exception as err:
                logger.error("closing connection {}:{}".format(*client_conn.peername()))
                if client_conn.socket in self._send_sockets:
                    self._send_sockets.remove(client_conn.socket)
                if client_conn.socket in self._recv_sockets:
                    self._recv_sockets.remove(client_conn.socket)
                del self.connections[client_conn.peername()]
                # if conf.DEBUG_MODE: raise

    def _manage_writable_sockets(self):
        for client_conn in [self.connections[sock.getpeername()] for sock in self._send_sockets]:
            try:
                self.manage_send_request(client_conn)
            except:
                pass

    def _manage_error_socket(self):
        # drop clients for sockets that have encountered exceptions
        for error_client_conn in [self.connections[sock.getpeername()] for sock in self._error_sockets]:
            self.manage_problem_client(error_client_conn)
            if error_client_conn.socket in self._recv_sockets:
                self._recv_sockets.remove(error_client_conn.socket)
            if error_client_conn.socket in self._send_sockets:
                self._send_sockets.remove(error_client_conn.socket)

    def get_all_socket_activities(self, timeout: int = 5) -> None:
        """ select.select() provides a fairly ratty, undifferentiated interface.
             clean it up by
             -.  preprocessing socket inputs per what select.select() wants, then
             -.  throwing an exception if the server_socket is in the problem sockets
             -.  breaking result down into four categories:
                 -.  open connection requests
                 -.  "receive content" requests
                 -.  channels that are free to receive responses
                 -.  channels that have detectable anomalies
         """
        client_sockets = [sock.socket for sock in self.connections.values()]
        all_channels = all_request_channels = [self.socket] + client_sockets
        (active_sockets, available_response_channels, problem_sockets) = select.select(all_request_channels,
                                                                                       client_sockets, all_channels,
                                                                                       timeout)

        self._new_conn = self.socket in active_sockets
        self._recv_sockets = [socket for socket in active_sockets if socket is not self.socket]
        self._send_sockets = available_response_channels
        self._error_sockets = [socket for socket in problem_sockets if socket is not self.socket]

        if self.socket in self._error_sockets:
            raise OSError('?? server socket failure')

    def process_request(self, client: ServerSideClientConn) -> None:
        """  try to accept and logger.info incoming message from client
             -.  on success, enqueue it for remaining clients
             -.  on failure, issue error message, remove client from connection_list,
                 and propagate exception to caller for further corrective action
        """
        handler = self.request_handler(client)
        handler.handle()

    def manage_send_request(self, client: ServerSideClientConn) -> None:
        """  try to output message to this client
             -.  on failure, issue error message, remove client from connection_list,
                 and propagate exception to caller for further corrective action
        """
        try:
            client.send()
        except Exception as err:
            # condition, when encountered, denotes socket closing
            (this_client_host, this_client_port) = client.socket.getpeername()
            logger.error(
                'closing connection from {}, port {} - {}'.format(this_client_host, this_client_port, err))
            client.close()
            del self.connections[client.address]
            raise

    def manage_problem_client(self, client: ServerSideClientConn) -> None:
        """  issue error message, then shut down the problem connection, removing it from the active connection list """
        (problem_client_host, problem_client_port) = client.socket.getpeername()
        logger.info('exception for %s, port %s: closing connection' % (problem_client_host, problem_client_port))
        client.close()
        del self.connections[client.address]

    def server_close(self) -> None:
        pass

    def reject_connection(self, new_conn: ServerSideClientConn) -> None:
        res = RespondsePackage("ERROR", "cant allow more that {} clients".format(conf.MAX_CLIENT_COUNT))
        new_conn.enqueue(res.pack())
        new_conn.send()
        logger.info("max connections: {} rejected".format(new_conn.peername()))
        new_conn.close()


class PrimaryServer(BaseServer):
    def __init__(self, request_handler, hostname, port, server_type='primary server'):
        super(PrimaryServer, self).__init__(request_handler, hostname, port)
        self.client_tags = 'clt'
        self.server_type = server_type


class ProxyServer(BaseServer):

    def __init__(self, request_handler: ProxyRequestHandler, server_conn: ClientConn, hostname, port,
                 server_type='proxy'):
        super(ProxyServer, self).__init__(request_handler, hostname, port)
        self.client_tags = 'clt'
        self.server_type = server_type
        self.server_conn = server_conn

    def process_request(self, client: ServerSideClientConn) -> None:
        """  try to accept and logger.info incoming message from client
             -.  on success, enqueue it for remaining clients
             -.  on failure, issue error message, remove client from connection_list,
                 and propagate exception to caller for further corrective action
        """
        handler = self.request_handler(client, self.server_conn)
        handler.handle()
