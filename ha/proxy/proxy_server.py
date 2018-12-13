import argparse
import time
from queue import Empty, Queue

from ha.commons.sap_servers import ProxyServer, ProxyRequestHandler, BaseMulitThreadAdmin, ProxyRegisterPrimaryServer, \
    ProxyRegisterPrimaryRequestHandler
from ha.commons.connections import ClientConn
import config as conf
from ha.commons.logger import get_module_logger

logger = get_module_logger(__name__)


class ProxyThreadAdmin(BaseMulitThreadAdmin):

    def __init__(self, parsed_args: argparse.ArgumentParser()):
        super().__init__(parsed_args)
        self.proxy_register_socket_started = False
        self.backup_started = False
        self.primary_is_registered = False
        self.name = 'proxy'
        self.primary_server_sap = parsed_args.proxy_sap
        self.thread_Q_handlers.update({'REGISTER': self.handle_new_primary_registn})
        self.Q_to_server = Queue()

    def initialize(self):
        """ Initial Tuple Space service"""
        try:
            self.start_shutdown_socket()
            self.start_proxy_register_socket()
            self.wait_for_sap_registn()
            self.start_proxy_server_socket()
            self.monitor_threads()
        except InterruptedError as err:
            logger.error("{} Shutting down - error: {}".format(self.name, err))
        except Exception as err:
            logger.exception("{} Shutting down {}".format(self.name, err))
            raise
        finally:
            self.shutdown_service()


    def wait_for_sap_registn(self):
        try:
            logger.info("proxy waiting for primary server to register")
            data = self.thread_Q.get(timeout=conf.REGISTER_WAIT_TIME)
            response = data['payload'].split(':')
            logger.info("proxy registering {} as primary".format(data['payload']))
            self.primary_server_sap = (response[0], int(response[1]))
        except Empty:
            raise RuntimeError("no server sap after {} secs".format(conf.REGISTER_WAIT_TIME))

    def handle_new_primary_registn(self, msg: str):
        print(msg)
        msg = msg.split(":")
        self.Q_to_server.put((msg[0], int(msg[1])))

    def start_proxy_register_socket(self):
        if not self.proxy_register_socket_started:
            sh = ProxyRegisterPrimaryServer(ProxyRegisterPrimaryRequestHandler,
                                self.parsed_args.primary_reg_sap[0],
                                self.parsed_args.primary_reg_sap[1],
                                Q=self.thread_Q)
            sh.server_type = self.name + '-' + sh.server_type + "-listener"
            self.start_thread(sh.serve_forever, sh.server_type)
            self.proxy_register_socket_started = True

    def start_proxy_server_socket(self):
        server_conn = ClientConn(self.primary_server_sap)
        server_conn.connect_client_to_socket()
        server = ProxyServer(ProxyRequestHandler, server_conn, self.parsed_args.proxy_sap[0], self.parsed_args.proxy_sap[1], self.Q_to_server, max_client_count=5)
        self.start_thread(server.serve_forever, server.server_type)

    def monitor_threads(self):
        logger.info("monitoring {} threads".format(self.name))
        while True:
            time.sleep(1)
            try:
                data = self.thread_Q.get(False)
                self.thread_Q_handlers[data['command']](data['payload'])
            except Empty:
                pass
            except Exception as err:
                raise


def main(host, port):
    server_conn = ClientConn((conf.PRIMARY_SERVER_2_PROXY_IP, conf.PRIMARY_SERVER_2_PROXY_PORT))
    server_conn.connect_client_to_socket()
    server = ProxyServer(ProxyRequestHandler, server_conn, host, port)
    server.serve_forever()


if __name__ == '__main__':
    main(conf.PROXY_2_CLIENT_IP, conf.PROXY_2_CLIENT_PORT)
