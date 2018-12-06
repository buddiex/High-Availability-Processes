import json
import select
import time
import socket
from typing import Dict, Tuple, List
import ha.config as conf
from ha.commons.logger import get_module_logger
from ha.commons.connection import ServerSideClientConn

logger = get_module_logger(__name__)


class BaseRequestHandler(object):
    """Base class for request handler classes.
    """

    def __init__(self, client_conn: ServerSideClientConn):
        self.client_conn = client_conn
        self.setup()
        self.data = {}
        try:
            self.handle()
        finally:
            self.finish()

    def setup(self):
        pass

    def handle(self):
        raise NotImplementedError

    def send(self):
        self.client_conn.enqueue(self._json_encode())
        self.client_conn.send()

    def recv(self):

        return self.client_conn.recv()

    def _json_encode(self)-> bytes:
        return json.dumps(self.data).encode()

    def finish(self):
        pass


class ProxyRequestHandler(BaseRequestHandler):
    pass


# class ServerRequestHandler(BaseRequestHandler):
#     def handle(self):
#         # self.request is the TCP socket connected to the client
#         self.data = self.client_conn.socket.recv(1024).strip()
#         # self.request.sendall(self.data.upper())
#         self.client_conn.socket.sendall(self.data)

class ServerRequestHandler(BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.recv().strip()
        # self.request.sendall(self.data.upper())
        self.send()





class BaseServer(object):

    def __init__(self, request_handler, hostname: str , port: int,
                 backlog: int = 100, max_client_count: int = conf.MAX_CLIENT_COUNT):
        self.server_type = None
        self.socket: socket
        self.server_address: tuple = (hostname, port)
        self.connections: Dict[tuple, ServerSideClientConn] = {}
        self.request_handler  = request_handler
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
            logger.info('No clients connected - listening for connections on {} at port {}'.format(*self.server_address))
        try:
            conn, address = self.socket.accept()
            logger.info('client {}:{} added'.format(*self.server_address))
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
                    (new_conn, recv_sockets, send_sockets, error_sockets) = self.get_all_socket_activities()
                except:
                    raise

                # check for new connection requests
                if new_conn:
                    self.accept_new_connection()

                # drop clients for sockets that have encountered exceptions
                for error_client_conn in [self.connections[sock.getpeername()] for sock in error_sockets]:
                    self.manage_problem_client(error_client_conn)
                    if error_client_conn.socket in recv_sockets:
                        recv_sockets.remove(error_client_conn.socket)
                    if error_client_conn.socket in send_sockets:
                        send_sockets.remove(error_client_conn.socket)

                # obtain messages from active clients, enqueuing them to send to other clients
                for client_conn in [self.connections[sock.getpeername()] for sock in recv_sockets]:
                    try:
                        self.process_request(client_conn)
                    except Exception as err:
                        if client_conn.socket in send_sockets:
                            send_sockets.remove(client_conn.socket)
                        if client_conn.socket in recv_sockets:
                            recv_sockets.remove(client_conn.socket)
                        del self.connections[client_conn.peername()]


                # check for messages to send and the ability to send them
                for client_conn in [self.connections[sock.getpeername()] for sock in send_sockets]:
                    try:
                        self.manage_send_request(client_conn)
                    except:
                        pass
                    #  report exceptions - allow select() loop to recover as needed

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
                if conf.DEBUG_MODE:
                    raise

    def get_all_socket_activities(self, timeout: int=5) -> Tuple[bool, List, List, List]:
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
        if self.socket in problem_sockets:
            raise OSError('?? server socket failure')

        return (
            self.socket in active_sockets,
            [sock for sock in active_sockets if sock is not self.socket],
            available_response_channels,
            [sock for sock in problem_sockets if sock is not self.socket]
        )

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
            logger.info(
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
        pass


class PrimaryServer(BaseServer):

    def __init__(self, request_handler, hostname='127.0.0.1', port=8899):
        super(PrimaryServer, self).__init__(request_handler, hostname, port)
        self.client_tags = 'clt'
        self.server_type = 'server'


class ProxyServer(BaseServer):

    def __init__(self, request_handler, hostname='127.0.0.1', port=8899):
        super(ProxyServer, self).__init__(request_handler, hostname, port)
        self.client_tags = 'clt'
        self.server_type = 'proxy'
