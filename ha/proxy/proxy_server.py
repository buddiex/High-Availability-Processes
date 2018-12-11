import argparse

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

    def initialize(self):
        """ Initial Tuple Space service"""
        #@TODO: NIYI
        pass


def main(host, port):
    # server = PrimaryServer(ProxyRequestHandler,host, port)
    server_conn = ClientConn((conf.PRIMARY_SERVER_2_PROXY_IP, conf.PRIMARY_SERVER_2_PROXY_PORT))
    server_conn.connect_client_to_socket()
    server = ProxyServer(ProxyRequestHandler, server_conn, host, port)
    server.serve_forever()


if __name__ == '__main__':
    main(conf.PROXY_2_CLIENT_IP, conf.PROXY_2_CLIENT_PORT)
