import unittest
import pytest
import socket
from unittest.mock import patch
from ha.commons.sap_servers import PrimaryServer, ServerEchoRequestHandler
from tests.mocks import start_mock_server, get_free_port, start_tcp_main_server
from ha.commons.services import TupleSpaceServer


@pytest.fixture()
def server():
    HOST = "localhost"
    port = 9999
    start_tcp_main_server(HOST, port)
    req = TupleSpaceServer(HOST, port)
    return req

def client(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        ip = 'localhost'
        port = get_free_port()
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        yield response
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

@pytest.mark.parametrize('data', [
    'name'
])
def test_server(server, data):
    res = server.get(data)
    assert {'command': 'GET', 'payload': data}.items() <= res.items(), f'{res}'
