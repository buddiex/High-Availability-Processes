from ha.commons.sap_servers import PrimaryServer, PrimaryServerRequestHandler, ServerEchoRequestHandler, HeartBeatServer, HearthBeatRequestHandler, ShutdownServer, ShutDownRequestHandler
import config as conf
from queue import Queue
import threading
import time
from ha.commons.logger import get_module_logger


logger = get_module_logger(__name__)


class TupleSpaceApp:

    def __init__(self):
        pass

    def get(self, data):
        return "do get"

    def post(self, data):
        return "do post"

    def put(self, data):
        return "do put"

    def delete(self, data):
        return "do delete"

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
    app_to_run = TupleSpaceApp()
    server = PrimaryServer(PrimaryServerRequestHandler,host, port, app_to_run)
    server.serve_forever()
    # test_other_sap_servers()


if __name__ == '__main__':
    main(conf.SERVER_DEFAULT_HOST, conf.SERVER_DEFAULT_PORT)
