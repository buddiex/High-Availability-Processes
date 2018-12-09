import argparse
import sys
import config as conf

from ha.server.tuple_space_server import TupleSpaceService
from ha.server.tuple_space_app.tuplespace_app import TupleSpaceApp


def client(args_in):
    print(args_in.z)


def proxy(args_in):
    print(args_in)


def server(args_in):
    tuple_space_service = TupleSpaceService(args_in, TupleSpaceApp(args_in.tuple_space_file))
    tuple_space_service.server_script_name = sys.argv[0]
    tuple_space_service.initialize()


if __name__ == "__main__":
    # get current script name - used to start backup service
    parser = argparse.ArgumentParser()
    parser.add_argument('--stats', action='store_true', help='returns a summary of the system')
    subparsers = parser.add_subparsers(title='sub-commands')

    client_args = subparsers.add_parser('client', help="client related commands, <client> - h")
    client_args.add_argument('z')
    client_args.set_defaults(func=client)

    proxy_bar = subparsers.add_parser('proxy', help="proxy related commands, <proxy> - h")
    proxy_bar.add_argument('z')
    proxy_bar.set_defaults(func=proxy)

    server_args = subparsers.add_parser('server', help="for server related commands, <server> - h")
    server_args.add_argument('-tpfile', '--tuple-space-file', dest='tuple_space_file', default=conf.TUPLE_SPACE_JSON)
    server_args.add_argument('-tpsap', '--tp-sap', dest='primary_sap',default=(conf.PRIMARY_SERVER_2_PROXY_IP, conf.PRIMARY_SERVER_2_PROXY_PORT))
    server_args.add_argument('-shutdown', '--shutdown-sap', dest='shutdown_sap', default=(conf.PRIMARY_SERVER_SHUTDOWN_IP, conf.PRIMARY_SERVER_SHUTDOWN_PORT))
    server_args.add_argument('-heartbeat', '--heartbeat-sap', dest='heartbeat_sap', default=(conf.PRIMARY_SERVER_HEARTBEAT_IP, conf.PRIMARY_SERVER_HEARTBEAT_PORT))
    server_args.add_argument('-backup', '--backup-sap', dest='backup_sap', default=(conf.BACKUP_SERVER_UPDATE_IP, conf.BACKUP_SERVER_UPDATE_PORT))
    server_args.add_argument('-bk_shutdown', '--bk-shutdown-sap', dest='bk_shutdown_sap',default=(conf.BACKUP_SERVER_SHUTDOWN_IP, conf.BACKUP_SERVER_SHUTDOWN_PORT))
    server_args.add_argument('-proxy', '--proxy-sap', dest='proxy_sap',default=(conf.PROXY_COMM_IP, conf.PROXY_COMM_PORT))
    server_args.add_argument('--is_primary', default=True, dest='is_primary', type=lambda x: (str(x).lower() == 'true'))
    server_args.add_argument('-primary_id', '--primary-process-id', dest='primary_id', default=None)
    server_args.set_defaults(func=server)

    args = parser.parse_args()
    args.func(args)




