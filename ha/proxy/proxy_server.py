from ha.commons.sap_servers import ProxyServer, ProxyRequestHandler
from ha.commons.connections import ClientConn
import config as conf


def main(host, port):
    # server = PrimaryServer(ProxyRequestHandler,host, port)
    server_conn = ClientConn((conf.PRIMARY_SERVER_2_PROXY_IP, conf.PRIMARY_SERVER_2_PROXY_PORT))
    server_conn.connect_client_to_socket()
    server = ProxyServer(ProxyRequestHandler,server_conn, host, port)
    server.serve_forever()


if __name__ == '__main__':
    main(conf.PROXY_2_CLIENT_IP, conf.PROXY_2_CLIENT_PORT)
