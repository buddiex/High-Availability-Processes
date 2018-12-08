import subprocess
import sys
import json
import argparse
import os
from ha.commons.logger import get_module_logger

logger = get_module_logger(__name__)


class TupleSpaceService:

    def __init__(self, parsed_args: argparse.ArgumentParser()):
        self.tuple_space_file = parsed_args.tuple_space_file
        self.tuple_space = None
        self.shutdown_sap = parsed_args.shutdown_sap
        self.proxy_sap = parsed_args.proxy_sap
        self.backup_sap = parsed_args.backup_sap
        self.primary_sap = parsed_args.primary_sap
        self.isPrimary = parsed_args.is_primary_server
        self.server_script_name = ""
        self.primary_process_id = ""

        # Get command line arguments to be used by backup_service
        self.raw_command_args = sys.argv[1:]

    def initialize(self):
        """ Initial Tuple Space service"""

        if self.isPrimary is True:
            self.start_as_primary()
        else:
            self.start_as_backup()

    def load_tuple_space(self) -> None:
        """ Load tuple space from tuple space file"""
        try:
            if self.tuple_space_file is not None:
                with open(self.tuple_space_file, "r") as file:
                    file_content = file.read().strip()
                    try:
                        self.tuple_space = json.loads(file_content)
                    except ValueError as err:
                        raise

        except Exception as err:
            raise

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

    def start_as_primary(self):
        logger.info("Starting primary service")
        self.load_tuple_space()
        self.start_backup()
        self.start_heartbeat_socket()
        # self.wait_for_backup()

        pass

    def start_as_backup(self):
        pass


if __name__ == "__main__":
    # get current script name - used to start backup service
    script_name = sys.argv[0]

    # Parse command line arguments

    parser = argparse.ArgumentParser()

    parser.add_argument('-tpfile', '--tuple-space-file',
                        dest='tuple_space_file', default="sample_tuple_file.json")
    parser.add_argument('-proxy', '--proxy-sap',
                        dest='proxy_sap', default=('localhost', 8999))
    parser.add_argument('-backup', '--backup-sap',
                        dest='backup_sap', default=('localhost', 8999))
    parser.add_argument('-primary', '--primary-sap',
                        dest='primary_sap', default=('localhost', 8999))
    parser.add_argument('-p', '--is-primary-server',
                        dest='is_primary_server', default=None)
    parser.add_argument('-shutdown', '--shutdown-sap',
                        dest='shutdown_sap', default=('localhost', 8999))
    parser.add_argument('-primary_id', '--primary-process-id',
                        dest='primary_id', default=None)
    parser.add_argument('-b', '--is-backup-server',
                        dest='is_backup_server', default=None)

    parsed_args = parser.parse_args()
    if parsed_args.is_backup_server is not None and parsed_args.is_backup_server is not False:
        parsed_args.is_primary_server = False
    else:
        parsed_args.is_primary_server = True

    # initialize tuple space service
    tuple_space_service = TupleSpaceService(parsed_args)
    tuple_space_service.server_script_name = script_name
    tuple_space_service.initialize()

    # print(tuple_space_service.tuple_space)

