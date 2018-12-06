import unittest
import pytest
from unittest.mock import patch
from ha.commons.connection import ClientConn
from ha.commons.protocol import Request
from tests.mocks import start_mock_server, get_free_port, start_tcp_mock_server, start_tcp_main_server
from ha.commons.services import get_users, client


# class TestMockServer(unittest.TestCase):
#
#     def setUp(self):
#         self.mock_server_port = get_free_port()
#         start_mock_server(self.mock_server_port)
#
#     def test_request_response(self):
#         mock_users_url = 'http://localhost:{port}/users'.format(port=self.mock_server_port)
#
#         # Patch USERS_URL so that the service uses the mock server URL instead of the real URL.
#         with patch.dict('ha.commons.services.__dict__', {'USERS_URL': mock_users_url}):
#             response = get_users()
#
#         # self.assertDictContainsSubset({'Content-Type': 'application/json; charset=utf-8'}, response.headers)
#         self.assertTrue(response.ok)
#         self.assertListEqual(response.json(), [])

@pytest.fixture()
def server1():
    HOST = "localhost"
    mock_server_port = get_free_port()
    start_tcp_mock_server(HOST, mock_server_port)
    req = Request(HOST, mock_server_port)
    return req


@pytest.fixture()
def server():
    HOST = "localhost"
    mock_server_port = get_free_port()
    start_tcp_main_server(HOST, mock_server_port)
    req = Request(HOST, mock_server_port)
    return req

@pytest.mark.parametrize('data', [
    'name',
    'age',
    'school'
])
def test_request_get(server, data):
    res = server.get(data)
    assert {'command': 'GET', 'payload': data}.items() <= res.items(), f'{res}'
