import argparse
from _queue import Empty

from ha.commons.sap_servers import ProxyServer, ProxyRequestHandler, BaseMulitThreadAdmin
from ha.commons.connections import ClientConn
import config as conf
from ha.commons.logger import get_module_logger

logger = get_module_logger(__name__)


class ProxyThreadAdmin(BaseMulitThreadAdmin):

    def __init__(self, parsed_args: argparse.ArgumentParser()):
        super().__init__(parsed_args)
        self.backup_started = False
        self.primary_is_registered = False
        self.name = 'proxy'
        self.primary_sap = parsed_args.tp_sap


    def initialize(self):
        """ Initial Tuple Space service"""

        self.start_shutdown_socket()
        self.get_server_sap()
        self.start_server()
        self.monitor_threads()


    def get_server_sap(self):
        try:
            logger.info("waiting for server sap")
            data = self.thread_Q.get(timeout=conf.HEARTBEAT_WAIT_TIME)
            response = data.split(':')
            self.primary_sap = tuple(response[0], int(response[1]))
        except Empty:
            raise RuntimeError("no server sap after {} secs".format(conf.HEARTBEAT_WAIT_TIME))

    def start_server(self):

        server_conn = ClientConn(self.primary_sap)
        server_conn.connect_client_to_socket()
        server = ProxyServer(ProxyRequestHandler, server_conn, conf.PROXY_2_CLIENT_IP, conf.PROXY_2_CLIENT_PORT)
        self.start_thread(server.serve_forever, 'server')


def main(host, port):
    # server = PrimaryServer(ProxyRequestHandler,host, port)
    # change parameters to primary sap
    server_conn = ClientConn((conf.PRIMARY_SERVER_2_PROXY_IP, conf.PRIMARY_SERVER_2_PROXY_PORT))
    server_conn.connect_client_to_socket()
    server = ProxyServer(ProxyRequestHandler, server_conn, host, port)
    server.serve_forever()


if __name__ == '__main__':
    main(conf.PROXY_2_CLIENT_IP, conf.PROXY_2_CLIENT_PORT)
