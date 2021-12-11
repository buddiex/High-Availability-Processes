from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import socketserver
from threading import Thread
import requests
import re, json

from ha.commons.sap_servers import MainServer, ServerEchoRequestHandler


class MockServerRequestHandler(BaseHTTPRequestHandler):
    USERS_PATTERN = re.compile(r'/users')

    def do_GET(self):
        if re.search(self.USERS_PATTERN, self.path):
            # Add response status code.
            self.send_response(requests.codes.ok)

            # Add response headers.
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()

            # Add response content.
            response_content = json.dumps([])
            self.wfile.write(response_content.encode('utf-8'))
            return


class MockServerRequestHandler2(BaseHTTPRequestHandler):
    def do_GET(self):
        # Process an HTTP GET request and return a response with an HTTP 200 status.
        self.send_response(requests.codes.ok)
        self.end_headers()
        return


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


def start_mock_server(port):
    # Configure mock server.
    mock_server = HTTPServer(('localhost', port), MockServerRequestHandler)

    # Start running mock server in a separate thread.
    # Daemon threads automatically shut down when the main process exits.f
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        # self.request.sendall(self.data.upper())
        self.request.sendall(self.data)


def start_tcp_mock_server(host, port):
    server = socketserver.TCPServer((host, port), MyTCPHandler)
    mock_server_thread = Thread(target=server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()


def start_tcp_main_server(host, port, app_to_run):
    server = MainServer(ServerEchoRequestHandler, host, port, app_to_run)
    mock_server_thread = Thread(target=server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()
