from ha.commons.sap_servers import PrimaryServer, PrimaryServerRequestHandler, HeartBeatServer, HearthBeatRequestHandler, ShutdownServer, ShutDownRequestHandler
import config as conf
from queue import Queue
import threading
import time
from ha.commons.logger import get_module_logger
from ha.server.tuplespace_app import TupleSpaceApp

logger = get_module_logger(__name__)


def test_other_sap_servers():
    thread_Q = Queue()
    servs = []
    servs.append(HeartBeatServer(HearthBeatRequestHandler,'localhost', 1111, 2, Q=thread_Q))
    servs.append(ShutdownServer(ShutDownRequestHandler, 'localhost', 11020, Q=thread_Q))
    for th in servs:
        s_thread = threading.Thread(target=th.serve_forever)
        s_thread.start()
        s_thread.setDaemon(True)

    for i in range(10):
        time.sleep(1)
        print(i)
        try:
            print(thread_Q.get(block=False))
        except:
            pass



def main(host, port):
    app_to_run = TupleSpaceApp(' ')
    server = PrimaryServer(PrimaryServerRequestHandler,host, port, app_to_run)
    server.serve_forever()
    # test_other_sap_servers()


if __name__ == '__main__':
    main(conf.PRIMARY_SERVER_2_PROXY_IP, conf.PRIMARY_SERVER_2_PROXY_PORT)
