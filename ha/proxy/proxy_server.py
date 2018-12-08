from ha.commons.server import ProxyServer, ServerRequestHandler,  ProxyRequestHandler
from ha.commons.connection import ClientConn
import ha.config as conf
import threading


def main(host, port):
    # server = PrimaryServer(ProxyRequestHandler,host, port)
    server_conn = ClientConn((conf.SERVER_DEFAULT_HOST, conf.SERVER_DEFAULT_PORT))
    server_conn.connect_client_to_socket()
    server = ProxyServer(ProxyRequestHandler,server_conn, host, port)
    server.serve_forever()


if __name__ == '__main__':
    main(conf.PROXY_DEFAULT_HOST, conf.PROXY_DEFAULT_PORT)
