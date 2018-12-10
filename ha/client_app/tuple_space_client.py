from ha.commons.clients import TupleSpaceClient
from ha.commons.logger import get_module_logger
import config as conf
from ha.commons.utils import hostname_parser, IPv4_addr_parser, port_parser
import socket
import random
import argparse

logger = get_module_logger(__name__)


def main():
    random.seed()
    try:
        # set up to acquire arguments from command line
        parser = argparse.ArgumentParser()
        # parser.add_argument('-host', '--server-host', type=hostname_parser, dest='server_host', default=None, )
        # parser.add_argument('-ip', '--server-IP', type=IPv4_addr_parser, dest='server_IP', default=conf.PROXY_2_CLIENT_IP, )
        # parser.add_argument('-port', '--server-port', type=port_parser, dest='server_port', default=conf.PROXY_2_CLIENT_PORT, )

        parser.add_argument('-ip', '--server-IP', dest='server_IP', default=conf.PROXY_2_CLIENT_IP, )
        parser.add_argument('-port', '--server-port', type=port_parser, dest='server_port', default=conf.PROXY_2_CLIENT_PORT, )

        parsed_args = parser.parse_args()


        # # postprocess host, IP arguments to set default / validate consistency, depending on what's there
        # if parsed_args.server_IP is None:
        #     try:
        #         parsed_args.server_IP = socket.gethostbyname(conf.PROXY_2_CLIENT_IP) if parsed_args.server_host is None else \
        #             parsed_args.server_host[1]
        #     except OSError as err:
        #         raise OSError('invalid hostname (%s): %s' % (parsed_args.server_host[0], logger.debug(err)))
        # else:
        #     specified_IP, specified_host, actual_IP = parsed_args.server_host[1], parsed_args.server_host[
        #         0], parsed_args.server_IP
        #     syndrome = "specified IP address {} for server host {} differs from actual IP address {}".format(
        #         specified_IP, specified_host, actual_IP)
        #     assert parsed_args.server_host[1] == parsed_args.server_IP, syndrome

        # --------------------------------------------------
        #  instantiate and run the client
        # --------------------------------------------------
        tp_service = TupleSpaceClient(parsed_args.server_IP, parsed_args.server_port)
        for i in range(10):
            try:
                keyExpr = "^f"
                valExpr = ".*"
                res = tp_service.get(keyExpr, valExpr)
                print(res.data['payload'])
                print(res.data['status'])

                res = tp_service.post('[("fal","niyilomo"),("gal","heyes"),("zal","heyes"),("gal","heyes")]')
                print(res.data['payload'])
                print(res.data['status'])

                res = tp_service.put('[("fal","niyi"),("gal","heyes"),("zal","heyes"),("galoolll","heyes")]')
                print(res.data['payload'])

            except ConnectionAbortedError as err:
                #@TODO: implement a wait and retry here
                pass
                # raise
    #
    except Exception as err:
        logger.info('aborting {}'.format(err))
        if conf.DEBUG_MODE: raise


if __name__ == '__main__':
    main()
