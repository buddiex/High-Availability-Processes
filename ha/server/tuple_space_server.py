import subprocess
import sys
import json
import argparse
import os
from ha.commons.logger import get_module_logger
import config as conf
from ha.commons.sap_servers import PrimaryServer, PrimaryServerRequestHandler

logger = get_module_logger(__name__)


from ha.server.tuplespace_app import TupleSpaceApp


class TupleSpaceService:

    def __init__(self, parsed_args: argparse.ArgumentParser(), app: TupleSpaceApp):
        self.tuple_space = None
        self.shutdown_sap = parsed_args.shutdown_sap
        self.proxy_sap = parsed_args.proxy_sap
        self.backup_sap = parsed_args.backup_sap
        self.primary_sap = parsed_args.primary_sap
        self.isPrimary = parsed_args.is_primary
        self.server_script_name = ""
        self.primary_process_id = ""
        self.backup_process_id = ""
        self.app = app(parsed_args.tuple_space_file)

        # Get command line arguments to be used by backup_service
        self.raw_command_args = sys.argv[1:]

    def initialize(self):
        """ Initial Tuple Space service"""
        try:
            if self.isPrimary:
                self.start_as_primary()
            else:
                self.start_as_backup()
        except Exception:
            pass

    def start_as_backup(self):
        pass


    def start_as_primary(self):
        logger.info("Starting primary service")

        self.app.load_tuple_space()

        self.start_backup()
        self.start_heartbeat_socket()

        server = PrimaryServer(PrimaryServerRequestHandler, host, port, app_to_run)
        server.serve_forever()
        # self.wait_for_backup()


    def start_backup(self) -> None:
        """ Start backup service with specific arguments"""
        # use os.getpid() get process id that can be used to kill the primary process
        # add additional parameters for the backup service
        # -b flags it as a backup service

        backup_args = self.raw_command_args + ['-primary_id', str(os.getpid()), '-b', 'yes']

        # if the backup can't be started, write the tuple space to file
        try:
            logger.info("Starting backup service")

            subprocess.Popen(["python", self.server_script_name] + backup_args, shell=False)
        except:
            raise
            if self.tuple_space is not None:
                with open(self.tuple_space_file, "w") as file:
                    file.write(self.tuple_space)

    def start_heartbeat_socket(self):
        pass

    def start_shutdown_socket(self):
        pass

    def start_update_socket(self):
        pass

    def start(self):
        pass





if __name__ == "__main__":
    # get current script name - used to start backup service
    script_name = sys.argv[0]

    # Parse command line arguments

    parser = argparse.ArgumentParser()

    parser.add_argument('-tpfile', '--tuple-space-file',  dest='tuple_space_file', default=conf.TUPLE_SPACE_JSON)
    parser.add_argument('-primary', '--primary-sap', dest='primary_sap', default=(conf.PRIMARY_SERVER_2_PROXY_IP, conf.PRIMARY_SERVER_2_PROXY_PORT))
    parser.add_argument('-shutdown', '--shutdown-sap', dest='shutdown_sap', default=(conf.PRIMARY_SERVER_SHUTDOWN_IP, conf.PRIMARY_SERVER_SHUTDOWN_PORT))
    parser.add_argument('-heartbeat', '--heartbeat-sap', dest='heartbeat_sap', default=(conf.PRIMARY_SERVER_HEARTBEAT_IP, conf.PRIMARY_SERVER_HEARTBEAT_PORT))
    parser.add_argument('-backup', '--backup-sap', dest='backup_sap', default=(conf.BACKUP_SERVER_UPDATE_IP, conf.BACKUP_SERVER_UPDATE_PORT))
    parser.add_argument('-bk_shutdown', '--bk-shutdown-sap', dest='bk_shutdown_sap', default=(conf.BACKUP_SERVER_SHUTDOWN_IP, conf.BACKUP_SERVER_SHUTDOWN_PORT))
    parser.add_argument('-proxy', '--proxy-sap', dest='proxy_sap', default=(conf.PROXY_COMM_IP, conf.PROXY_COMM_PORT))
    parser.add_argument('-server_type', '--is-primary-server',  dest='server_type', default='primary')
    parser.add_argument('--is_primary', default=True, dest='is_primary', type=lambda x: (str(x).lower() == 'true'))
    parser.add_argument('-primary_id', '--primary-process-id',  dest='primary_id', default=None)

    parsed_args = parser.parse_args()
    tuple_space_service = TupleSpaceService(parsed_args)
    tuple_space_service.server_script_name = script_name
    tuple_space_service.initialize()

    # print(tuple_space_service.tuple_space)

