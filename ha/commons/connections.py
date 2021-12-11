import socket
import sys

import config as conf

from .logger import get_module_logger

logger = get_module_logger(__name__)


def bytes_in_representation(value):
    return (value.bit_length() + 7) // 8


BYTES_PER_SHORT = bytes_in_representation(2 ** 16 - 1)


class BaseConn(object):
    """TCP connection abstraction to manage a socket's lifetime"""

    def __init__(self, name, byte_count_size=conf.BYTES_PER_SHORT):
        self.socket = None
        self.residue_from_previous_messages = b''
        self.pending_messages = []
        self.byte_count_size = byte_count_size
        self.__dict__['initialized_'] = True
        self.name = name

    def instantiate_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as err:
            raise OSError('could not instantiate TCP socket')

    def sockname(self):
        """ return host and port for server side of connection """
        return self.socket.getsockname()

    def peername(self):
        """ return host and port for client side of connection """
        return self.socket.getpeername()

    def recv(self):
        """ receive variable-length message from client. format: standard-network-order byte count, followed by
        message body """

        # ---------------------------------------------------------

        def receive_k_bytes(k=self.byte_count_size):
            """ receive k bytes from socket connection, from which residue bytes have previouisly been extracted
                -. account for residue required because messages can be delivered in irregularly sized packets
                -. treat bytes in residue as initial part of data received
                -. return the k byte sequence received, updating the residue
            """
            chunk = b''
            while len(self.residue_from_previous_messages) < k:
                try:
                    chunk = self.socket.recv(k - len(self.residue_from_previous_messages))
                except ConnectionAbortedError as err:
                    logger.error("{}:{} - {}".format(*self.socket.getpeername(), err))
                    # self.socket_.close()
                    raise

                if chunk == b'': raise ConnectionAbortedError("socket connection broken")
                self.residue_from_previous_messages = self.residue_from_previous_messages + chunk
            result, self.residue_from_previous_messages = self.residue_from_previous_messages[:k], \
                                                          self.residue_from_previous_messages[k:]
            return result

        # ----------------------------------------------------------
        # first, get byte count for message, correcting for network order; then, get message proper
        self.socket.setblocking(True)
        byte_count_for_msg = socket.ntohs(int.from_bytes(receive_k_bytes(), byteorder=sys.byteorder, signed=False))
        message = receive_k_bytes(byte_count_for_msg)
        logger.debug('received {} from {}:{}'.format(message, *self.peername()))
        self.socket.setblocking(False)
        return message.decode()

    def enqueue(self, message):
        """ enqueue message for send to client """
        self.pending_messages += [message]

    def send(self):
        """ send next enqueued variable-length message to client.
            format: standard-network-order byte count, followed by message body
        """
        if self.pending_messages:
            (encoded_message, self.pending_messages) = (self.pending_messages[0], self.pending_messages[1:])
            # encoded_message = json.dumps(this_message).encode()
            if bytes_in_representation(len(encoded_message)) > self.byte_count_size:
                raise RuntimeError(
                    "?? excessive length (%d) for outgoing text (%s)" % (len(encoded_message), encoded_message))
            #
            # finally, send outgoing byte count, followed by message
            #
            logger.debug("sending {} to {}:{}".format(encoded_message, *self.socket.getpeername()))
            self.socket.sendall(
                socket.htons(len(encoded_message)).to_bytes(self.byte_count_size, byteorder=sys.byteorder,
                                                            signed=False) + encoded_message)

    def close(self):
        """ close connection, warning if unsent messages are present """
        if self.pending_messages:
            logger.info("?? closing client socket with unsent messages. message list follows. ")
            for message in self.pending_messages:
                logger.info("*** ", message)
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()


class ServerSideClientConn(BaseConn):
    """Accepted client connection."""

    def __init__(self, server_socket, addr, name=''):
        super(ServerSideClientConn, self).__init__(name)
        self.socket = server_socket
        self.address = addr


class ClientConn(BaseConn):
    """Accepted client connection."""

    def __init__(self, addr: tuple, name=''):
        super(ClientConn, self).__init__(name)
        self.addr = addr

    def connect_client_to_socket(self):
        """  configure a socket at specified host and port"""
        self.instantiate_socket()
        # self.socket.setblocking(False)
        try:
            self.socket.connect(self.addr)
            logger.info('connected to server: {}:{}'.format(*self.addr))
        except Exception as err:
            raise OSError("couldn't connect to {}:{} Error: {}".format(self.addr[0], self.addr[1], err))
