import re
import subprocess
import sys
from ha.commons.server import HeartbeatServer, HearbeatRequestHandler
import json
import argparse


class ServiceCommandLineArguments(object):
    def __int__(self, tuple_space_file=None):
        self.tuple_space_file = tuple_space_file
        self.shutdown_sap = ("localhost",8999)
        self.heartbeat_sap = ("localhost",8999)
        self.isPrimary = False


class TupleSpaceService:

    def __init__(self, command_args:ServiceCommandLineArguments):
        self.tuple_space_file = command_args.tuple_space_file
        self.tuple_space = ""
        self.tuple_space_regex = ""
        self.shutdown_sap = command_args.shutdown_sap
        self.hearbeat_sap = command_args.heartbeat_sap
        self.isPrimary = command_args.isPrimary
        self.server_script_name = ""

    def initialize(self):
        if self.isPrimary:
            self.start_as_primary()
        else:
            self.start_as_backup()

    def load_tuple_space(self) -> None:
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

        subprocess.Popen(["python", self.server_script_name], shell=False)

    def start_heartbeat_socket(self):
        #server = HeartbeatServer(HearbeatRequestHandler, host, port)
        #server.serve_forever()
        pass

    def start_shutdown_socket(self):
        # use ServeSideClientConn

        pass

    def start_update_socket(self):
        # use ServeSideClientConn
        pass

    def start(self):
        pass

    def start_as_primary(self):

        self.load_tuple_space()
        self.start_backup()
        self.start_heartbeat_socket()
        #self.wait_for_backup()

        pass

    def start_as_backup(self):
        pass


if __name__ == "__main__":
    # get current script name
    script_name = sys.argv[0]

    # Get command line arguments
    command_line_args = ServiceCommandLineArguments()

    parser = argparse.ArgumentParser()
    parser.add_argument('-primary', '--primary-server',
                        dest='is_primary_server', default=False)

    parsed_args = parser.parse_args()
    command_line_args.isPrimary = False if parsed_args.is_primary_server is False else True
    command_line_args.tuple_space_file = "sample_tuple_file.json"
    command_line_args.shutdown_sap =("localhost",8999)
    command_line_args.heartbeat_sap = ("localhost", 8999)

    # cl arguments end

    # initialize tuple space service
    tuple_space_service = TupleSpaceService(command_line_args)
    tuple_space_service.server_script_name = script_name
    tuple_space_service.initialize()
    tuple_space_service.start_as_primary()

    print(tuple_space_service.tuple_space)

    # start backup service
