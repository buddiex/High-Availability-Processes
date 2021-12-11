import threading
import time
from queue import Queue

import config as conf
from ha.commons.logger import get_module_logger
from ha.commons.sap_servers import MainServer, PrimaryServerRequestHandler, HeartBeatServer, HearthBeatRequestHandler, \
    ShutdownServer, ShutDownRequestHandler
from ha.server.tuple_space_app.tuplespace_app import TupleSpaceApp

logger = get_module_logger(__name__)


def test_other_sap_servers():
    thread_q = Queue()
    servs = []
    servs.append(HeartBeatServer(HearthBeatRequestHandler, 'localhost', 1111, 2, Q=thread_q))
    servs.append(ShutdownServer(ShutDownRequestHandler, 'localhost', 11020, Q=thread_q))
    for th in servs:
        s_thread = threading.Thread(target=th.serve_forever)
        s_thread.start()
        s_thread.setDaemon(True)

    for i in range(10):
        time.sleep(1)
        print(i)
        try:
            print(thread_q.get(block=False))
        except:
            pass


def main(host, port):
    app_to_run = TupleSpaceApp(' ')
    server = MainServer(PrimaryServerRequestHandler, host, port, app_to_run)
    server.serve_forever()
    # test_other_sap_servers()


if __name__ == '__main__':
    main(conf.PRIMARY_SERVER_2_PROXY_IP, conf.PRIMARY_SERVER_2_PROXY_PORT)
