import re
import subprocess
import sys
from ha.commons.server import HeartbeatServer, HearbeatRequestHandler
import json
import argparse


class TupleSpaceService:

    def __init__(self, parsed_args):
        self.tuple_space_file = parsed_args.tuple_space_file
        self.tuple_space = ""
        self.tuple_space_regex = ""
        self.shutdown_sap = parsed_args.shutdown_sap
        self.hearbeat_sap = parsed_args.heartbeat_sap
        self.isPrimary = False if parsed_args.is_primary_server is False else True
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
        # server = HeartbeatServer(HearbeatRequestHandler, host, port)
        # server.serve_forever()
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
        # self.wait_for_backup()

        pass

    def start_as_backup(self):
        pass


if __name__ == "__main__":
    # get current script name
    script_name = sys.argv[0]

    # Get command line arguments

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--primary-server',
                        dest='is_primary_server', default=False)
    parser.add_argument('-tpfile', '--tuple-space-file',
                        dest='tuple_space_file', default="sample_tuple_file.json")
    parser.add_argument('-shutdown', '--shutdown-sap',
                        dest='shutdown_sap', default=('localhost', 8999))
    parser.add_argument('-heartbeat', '--heartbeat-sap',
                        dest='heartbeat_sap', default=('localhost', 8999))

    parsed_args = parser.parse_args()

    # initialize tuple space service
    tuple_space_service = TupleSpaceService(parsed_args)
    tuple_space_service.server_script_name = script_name
    tuple_space_service.initialize()

    print(tuple_space_service.tuple_space)

    # start backup service
