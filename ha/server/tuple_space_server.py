import subprocess
import sys
import argparse
import os
import threading
import time
from queue import Queue, Empty

from ha.commons.logger import get_module_logger
import config as conf
from ha.commons.sap_servers import HearthBeatRequestHandler, HeartBeatServer, ShutdownServer, ShutDownRequestHandler, \
    PrimaryServer, PrimaryServerRequestHandler
from ha.server.tuple_space_app.tuplespace_app import TupleSpaceApp

logger = get_module_logger(__name__)


class TupleSpaceService:

    def __init__(self, parsed_args: argparse.ArgumentParser(), app: TupleSpaceApp):
        self.all_threads = []
        self.parsed_args = parsed_args
        self.isPrimary = parsed_args.is_primary
        self.server_script_name = ""
        self.primary_process_id = ""
        self.backup_process_id = ""
        self.app = app
        # Get command line arguments to be used by backup_service
        self.raw_command_args = sys.argv[1:]

    def initialize(self):
        """ Initial Tuple Space service"""
        try:
            self.thread_Q = Queue()
            if self.isPrimary:
                self.start_as_primary()
            else:
                self.start_as_backup()
        except Exception as err:
            logger.info("shutdown: error - {}".format(err))
            self.shutdown_service()
            raise
        
    def delete_this_test_backup_start(self):

        for i in range(1):
            logger.debug(i)
            time.sleep(1)

    def start_as_primary(self):
        logger.info("Starting primary service")

        self.app.init()
        self.start_shutdown_socket()
        # self.start_backup()
        self.start_heartbeat_socket()
        # self.get_first_heartbeat()
        server = PrimaryServer(PrimaryServerRequestHandler,
                                self.parsed_args.tp_sap[0],
                                self.parsed_args.tp_sap[1],
                                self.app)
        server.serve_forever()

    def start_as_backup(self):
        logger.debug("server starting as backup")
        self.delete_this_test_backup_start()
        self.app.init()
        self.start_heartbeat_client()
        server = PrimaryServer(PrimaryServerRequestHandler,
                               self.parsed_args.tp_sap[0],
                               self.parsed_args.tp_sap[1],
                               self.app, server_type='back-up')
        # server.serve_forever()

        logger.debug("backup started as backup")



    def start_backup(self) -> None:
        """ Start backup service with specific arguments"""
        # use os.getpid() get process id that can be used to kill the primary process
        # add additional parameters for the backup service
        backup_start_cmd = """python "{}" server -tpfile "{}" -tpsap "{}" -shutdown "{}" -heartbeat "{}" -backup "{}" -bk_shutdown "{}" -proxy "{}" --is_primary "{}" -primary_id "{}"
        """.format(self.server_script_name,
                   self.parsed_args.tuple_space_file,
                   (conf.BACKUP_SERVER_2_PROXY_IP, conf.BACKUP_SERVER_2_PROXY_PORT),
                   (self.parsed_args.backup_sap[0], self.parsed_args.backup_sap[1]),
                   (conf.BACKUP_SERVER_HEARTBEAT_IP, conf.BACKUP_SERVER_HEARTBEAT_PORT),
                   (self.parsed_args.tp_sap[0], self.parsed_args.tp_sap[1]),
                   (self.parsed_args.bk_shutdown_sap[0], self.parsed_args.bk_shutdown_sap[1]),
                   (self.parsed_args.proxy_sap[0], self.parsed_args.proxy_sap[1]),
                   'false',
                   str(os.getpid())
                   )

        logger.info("Starting backup service")
        subprocess.Popen(backup_start_cmd, shell=False)

    def start_heartbeat_socket(self,):
        hb = HeartBeatServer(HearthBeatRequestHandler,
                             self.parsed_args.heartbeat_sap[0],
                             self.parsed_args.heartbeat_sap[1],
                             2,
                             Q=self.thread_Q)
        self.start_thread(hb)

    def start_shutdown_socket(self):
        sh = ShutdownServer(ShutDownRequestHandler,
                            self.parsed_args.shutdown_sap[0],
                            self.parsed_args.shutdown_sap[1],
                            Q=self.thread_Q)
        self.start_thread(sh)

    def start_thread(self, app_to_run):
        s_thread = threading.Thread(target=app_to_run.serve_forever, name=app_to_run.server_type)
        # s_thread.setDaemon(True)
        s_thread.start()
        self.all_threads.append(s_thread)

    def start_update_socket(self):
        pass

    def start(self):
        pass

    def shutdown_service(self):
        logger.info("shutting down all services")
        self.app.shutdown()

    def get_first_heartbeat(self):
        try:
            data = self.thread_Q.get(timeout=conf.HEARTBEAT_WAIT_TIME)
            return data == 'HB-0'
        except Empty:
            raise RuntimeError("no heartbeat after {} secs".format(conf.HEARTBEAT_WAIT_TIME))

