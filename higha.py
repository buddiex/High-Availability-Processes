import argparse
import sys

import config as conf
from ha.proxy.proxy_server import ProxyThreadAdmin
from ha.server.tuple_space_app.tuplespace_app import TupleSpaceApp
from ha.server.server_app import ServerMainThread
from tests.simulate_shutdowns import main


# logger = get_module_logger(__name__)


def client(args_in):
    print(args_in.z)


def simulate(args=''):
    """
    Simulate shutdown requests - primary_shutdown, backup_shutdown
    :param args:
    :return:
    """
    main(args.simulatn_type)


def proxy(args_in):
    """
    Start Proxy service and initialize it
    :param args_in:
    :return:
    """
    proxy_service = ProxyThreadAdmin(args_in)
    proxy_service.server_script_name = sys.argv[0]
    proxy_service.initialize()


def server(args_in):
    """
    Start tuplesprace service, using the required arguments (SAPS, and tuple space file)
    :param args_in:
    :return:
    """
    tuple_space_service = ServerMainThread(args_in, TupleSpaceApp(args_in.tuple_space_file))
    tuple_space_service.server_script_name = sys.argv[0]
    tuple_space_service.initialize()


def to_tuple(arg_in):
    """
    Define structure of SAPs as tuple.
    It converts string values to python tuple
    :return:
    """
    arg = arg_in.split(':')
    return (arg[0], int(arg[1]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--stats', action='store_true', help='returns a summary of the system')
    subparsers = parser.add_subparsers(title='sub-commands')

    # Parse client arguments

    client_args = subparsers.add_parser('client', help="client related commands, <client> - h", )
    client_args.add_argument('z')
    client_args.set_defaults(func=client)

    simulate_args = subparsers.add_parser('simulate', help="client related commands, <client> - h")
    simulate_args.add_argument('-type', dest='simulatn_type', help="simulation type")
    simulate_args.set_defaults(func=simulate)

    # Parse proxy service arguments

    proxy_bar = subparsers.add_parser('proxy', help="proxy related commands, <proxy> - h")
    proxy_bar.add_argument('-proxysap', '--proxy-sap', dest='proxy_sap', type=to_tuple,
                           default=f"{conf.PROXY_2_CLIENT_IP}:{conf.PROXY_2_CLIENT_PORT}")
    proxy_bar.add_argument('-shutdown', '--shutdown-sap', dest='shutdown_sap', type=to_tuple,
                           default=f"{conf.PROXY_SHUTDOWN_IP}:{conf.PROXY_SHUTDOWN_PORT}")
    proxy_bar.add_argument('-primaryreg', '--primary-reg-sap', dest='primary_reg_sap', type=to_tuple,
                           default=f"{conf.PROXY_PRIMARY_REG_IP}:{conf.PROXY_PRIMARY_REG_PORT}")
    proxy_bar.set_defaults(func=proxy)

    # Parse server arguments

    server_args = subparsers.add_parser('server', help="for server related commands, <server> - h")
    server_args.add_argument('-tpfile', '--tuple-space-file', dest='tuple_space_file', default=conf.TUPLE_SPACE_JSON)

    server_args.add_argument('-tpsap', '--tp-sap', dest='tp_sap', type=to_tuple,
                             default=f"{conf.PRIMARY_SERVER_2_PROXY_IP}:{conf.PRIMARY_SERVER_2_PROXY_PORT}")
    server_args.add_argument('-shutdown', '--shutdown-sap', dest='shutdown_sap', type=to_tuple,
                             default=f"{conf.PRIMARY_SERVER_SHUTDOWN_IP}:{conf.PRIMARY_SERVER_SHUTDOWN_PORT}")
    server_args.add_argument('-heartbeat', '--heartbeat-sap', dest='heartbeat_sap', type=to_tuple,
                             default=f"{conf.PRIMARY_SERVER_HEARTBEAT_IP}:{conf.PRIMARY_SERVER_HEARTBEAT_PORT}")

    server_args.add_argument('-backup', '--backup-sap', dest='backup_sap', type=to_tuple,
                             default=f"{conf.BACKUP_SERVER_2_PROXY_IP}:{conf.BACKUP_SERVER_2_PROXY_PORT}")
    server_args.add_argument('-bk_shutdown', '--bk-shutdown-sap', dest='bk_shutdown_sap', type=to_tuple,
                             default=f"{conf.BACKUP_SERVER_SHUTDOWN_IP}:{conf.BACKUP_SERVER_SHUTDOWN_PORT}")
    server_args.add_argument('-bk_heartbeat', '--bk-heartbeat-sap', dest='bk_heartbeat_sap', type=to_tuple,
                             default=f"{conf.BACKUP_SERVER_HEARTBEAT_IP}:{conf.BACKUP_SERVER_HEARTBEAT_PORT}")

    server_args.add_argument('-proxy', '--proxy-sap', dest='proxy_sap', type=to_tuple,
                             default=f"{conf.PROXY_PRIMARY_REG_IP}:{conf.PROXY_PRIMARY_REG_PORT}")

    server_args.add_argument('--is_primary', default=True, dest='is_primary', type=lambda x: (str(x).lower() == 'true'))
    server_args.add_argument('-primary_id', '--primary-process-id', dest='primary_id', default=None)
    server_args.set_defaults(func=server)

    args = parser.parse_args()
    # logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s {} [%(filename)s:%(lineno)d] %(message)s'
    #                     .format(args.func.__name__),
    #                     datefmt='%d-%m-%Y:%H:%M:%S')

    args.func(args)

    # time.sleep(30)
